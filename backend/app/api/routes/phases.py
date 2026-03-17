"""
Phase execution, artifact management, and validation endpoints.

Core HITL workflow:
1. POST  .../phases/{phase_id}/run       → Execute a phase (creates LLM version)
2. GET   .../phases/{phase_id}/artifact  → Review the artifact
3. PUT   .../phases/{phase_id}/artifact  → Edit the artifact (creates human version)
4. GET   .../phases/{phase_id}/history   → View all versions
5. POST  .../phases/{phase_id}/validate  → Re-validate after editing
6. GET   .../phases/{phase_id}/validation → Get latest validation report
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    ArtifactHistoryResponse,
    ArtifactResponse,
    ArtifactVersionSummary,
    RunPhaseRequest,
    RunPhaseResponse,
    RefinePhaseRequest,
    UpdateArtifactRequest,
    UpdateArtifactResponse,
    ValidationResponse,
)
from api.dependencies import (
    build_workflow_state,
    check_phase_prerequisites,
    get_phase_config,
    get_repository,
    run_validation_on_artifact,
)
from db.repository import SessionRepository
from services.llm_service import LLMService
from services.pipeline_service import PipelineService
from validation import ValidationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions/{session_id}/phases", tags=["phases"])


# =============================================================================
# Phase Execution
# =============================================================================


@router.post("/{phase_id}/run", response_model=RunPhaseResponse)
def run_phase(
    session_id: str,
    phase_id: str,
    request: RunPhaseRequest = RunPhaseRequest(),
    repo: SessionRepository = Depends(get_repository),
) -> RunPhaseResponse:
    """
    Execute a single pipeline phase.

    Creates a new artifact version with source='llm'.
    Prerequisites: all input phases must have a completed artifact.
    """
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    # Check prerequisites using latest artifacts
    latest_artifacts = repo.get_latest_artifacts(session_id)
    prereq_error = check_phase_prerequisites(latest_artifacts, phase)
    if prereq_error:
        raise HTTPException(status_code=409, detail=prereq_error)

    try:
        # Build services
        llm_service = LLMService(
            provider=session.provider,
            model=session.model,
            temperature=session.temperature,
        )
        pipeline = PipelineService(
            llm_service=llm_service,
            validation_engine=ValidationEngine(),
        )

        # Build workflow state from latest artifacts
        state = build_workflow_state(session, latest_artifacts, phase)

        # Execute
        artifact, raw_or_error, report = pipeline.run_phase(
            phase, state, max_retries=request.max_retries,
        )

        if artifact is not None:
            artifact_dict = json.loads(artifact.model_dump_json())
            report_dict = json.loads(report.model_dump_json()) if report else None

            db_artifact = repo.create_artifact_version(
                session_id=session.id,
                phase_id=phase.id,
                source="llm",
                status="completed",
                content=artifact_dict,
                validation_report=report_dict,
            )

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status="completed",
                version=db_artifact.version,
                source="llm",
                artifact=artifact_dict,
                validation=report_dict,
            )
        else:
            db_artifact = repo.create_artifact_version(
                session_id=session.id,
                phase_id=phase.id,
                source="llm",
                status="failed",
                error=raw_or_error,
            )

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status="failed",
                version=db_artifact.version,
                source="llm",
                error=raw_or_error,
            )

    except (ValueError, ConnectionError) as e:
        repo.create_artifact_version(
            session_id=session.id,
            phase_id=phase.id,
            source="llm",
            status="failed",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{phase_id}/refine", response_model=RunPhaseResponse)
def refine_phase(
    session_id: str,
    phase_id: str,
    request: RefinePhaseRequest,
    repo: SessionRepository = Depends(get_repository),
) -> RunPhaseResponse:
    """
    Refine an existing pipeline phase artifact via LLM using human instructions.

    Creates a new artifact version with source='llm'.
    Requires an existing artifact for this phase to be present.
    """
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    # Get the latest artifact for this phase to refine
    db_artifact = repo.get_latest_artifact(session_id, phase_id)
    if db_artifact is None or db_artifact.content is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot refine phase '{phase.name}' because it has not been run yet.",
        )

    # Check prerequisites using latest artifacts (same as run_phase)
    latest_artifacts = repo.get_latest_artifacts(session_id)
    prereq_error = check_phase_prerequisites(latest_artifacts, phase)
    if prereq_error:
        raise HTTPException(status_code=409, detail=prereq_error)

    try:
        # Build services
        llm_service = LLMService(
            provider=session.provider,
            model=session.model,
            temperature=session.temperature,
        )
        pipeline = PipelineService(
            llm_service=llm_service,
            validation_engine=ValidationEngine(),
        )

        # Build workflow state from latest artifacts
        state = build_workflow_state(session, latest_artifacts, phase)

        # Execute Refinement
        artifact, raw_or_error, report = pipeline.run_phase(
            phase,
            state,
            max_retries=request.max_retries,
            instructions=request.instructions,
            current_artifact=db_artifact.content,
        )

        if artifact is not None:
            artifact_dict = json.loads(artifact.model_dump_json())
            report_dict = json.loads(report.model_dump_json()) if report else None

            new_db_artifact = repo.create_artifact_version(
                session_id=session.id,
                phase_id=phase.id,
                source="llm",  # Source is LLM because it generated the response, even if guided by human
                status="completed",
                content=artifact_dict,
                validation_report=report_dict,
            )

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status="completed",
                version=new_db_artifact.version,
                source="llm",
                artifact=artifact_dict,
                validation=report_dict,
            )
        else:
            new_db_artifact = repo.create_artifact_version(
                session_id=session.id,
                phase_id=phase.id,
                source="llm",
                status="failed",
                error=raw_or_error,
            )

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status="failed",
                version=new_db_artifact.version,
                source="llm",
                error=raw_or_error,
            )

    except (ValueError, ConnectionError) as e:
        repo.create_artifact_version(
            session_id=session.id,
            phase_id=phase.id,
            source="llm",
            status="failed",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Artifact Retrieval, Editing & History
# =============================================================================


@router.get("/{phase_id}/artifact", response_model=ArtifactResponse)
def get_artifact(
    session_id: str,
    phase_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> ArtifactResponse:
    """Get the latest artifact version for a phase."""
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    db_artifact = repo.get_latest_artifact(session_id, phase_id)
    if db_artifact is None or db_artifact.content is None:
        raise HTTPException(
            status_code=404,
            detail=f"No artifact for phase '{phase.name}'. Run the phase first.",
        )

    return ArtifactResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        version=db_artifact.version,
        source=db_artifact.source,
        artifact=db_artifact.content,
    )


@router.put("/{phase_id}/artifact", response_model=UpdateArtifactResponse)
def update_artifact(
    session_id: str,
    phase_id: str,
    request: UpdateArtifactRequest,
    repo: SessionRepository = Depends(get_repository),
) -> UpdateArtifactResponse:
    """
    Update a phase artifact (human edit).

    Creates a new version with source='human'. The previous version is preserved.
    The edited artifact is validated against the phase's Pydantic schema.
    """
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    # Validate against schema
    try:
        validated = phase.output_schema.model_validate(request.artifact)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Artifact does not conform to {phase.output_schema.__name__} schema: {e}",
        )

    artifact_dict = json.loads(validated.model_dump_json())

    # Run validation
    latest_artifacts = repo.get_latest_artifacts(session_id)
    validation_dict = run_validation_on_artifact(latest_artifacts, phase, artifact_dict)

    # Create new version
    db_artifact = repo.create_artifact_version(
        session_id=session.id,
        phase_id=phase.id,
        source="human",
        status="completed",
        content=artifact_dict,
        validation_report=validation_dict,
    )

    return UpdateArtifactResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        version=db_artifact.version,
        source="human",
        artifact=artifact_dict,
        validation=validation_dict,
    )


@router.get("/{phase_id}/history", response_model=ArtifactHistoryResponse)
def get_artifact_history(
    session_id: str,
    phase_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> ArtifactHistoryResponse:
    """Get all versions of a phase artifact."""
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    versions = repo.get_artifact_history(session_id, phase_id)

    return ArtifactHistoryResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        versions=[
            ArtifactVersionSummary(
                version=v.version,
                source=v.source,
                status=v.status,
                created_at=v.created_at.isoformat(),
            )
            for v in versions
        ],
    )


# =============================================================================
# Validation
# =============================================================================


@router.post("/{phase_id}/validate", response_model=ValidationResponse)
def validate_phase(
    session_id: str,
    phase_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> ValidationResponse:
    """Re-run validation on the latest phase artifact."""
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    db_artifact = repo.get_latest_artifact(session_id, phase_id)
    if db_artifact is None or db_artifact.content is None:
        raise HTTPException(
            status_code=404,
            detail=f"No artifact for phase '{phase.name}'. Run the phase first.",
        )

    latest_artifacts = repo.get_latest_artifacts(session_id)
    validation_dict = run_validation_on_artifact(latest_artifacts, phase, db_artifact.content)
    if validation_dict is None:
        raise HTTPException(status_code=500, detail="Failed to validate artifact")

    # Create a new version with updated validation
    repo.create_artifact_version(
        session_id=session.id,
        phase_id=phase.id,
        source=db_artifact.source,
        status="completed",
        content=db_artifact.content,
        validation_report=validation_dict,
    )

    return ValidationResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        validation=validation_dict,
    )


@router.get("/{phase_id}/validation", response_model=ValidationResponse)
def get_validation(
    session_id: str,
    phase_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> ValidationResponse:
    """Get the validation report from the latest artifact version."""
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")

    db_artifact = repo.get_latest_artifact(session_id, phase_id)
    if db_artifact is None or db_artifact.validation_report is None:
        raise HTTPException(
            status_code=404,
            detail=f"No validation report for phase '{phase.name}'.",
        )

    return ValidationResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        validation=db_artifact.validation_report,
    )
