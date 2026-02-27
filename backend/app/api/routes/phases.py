"""
Phase execution, artifact management, and validation endpoints.

Core HITL workflow:
1. POST  .../phases/{phase_id}/run       → Execute a phase
2. GET   .../phases/{phase_id}/artifact  → Review the artifact
3. PUT   .../phases/{phase_id}/artifact  → Edit the artifact
4. POST  .../phases/{phase_id}/validate  → Re-validate after editing
5. GET   .../phases/{phase_id}/validation → Get latest validation report
"""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ArtifactResponse,
    PhaseStatus,
    RunPhaseRequest,
    RunPhaseResponse,
    UpdateArtifactRequest,
    UpdateArtifactResponse,
    ValidationResponse,
)
from api.dependencies import (
    PipelineSession,
    build_workflow_state,
    check_phase_prerequisites,
    get_phase_config,
    run_validation_on_artifact,
    session_store,
)
from services.llm_service import LLMService
from services.artifact_service import ArtifactService
from services.pipeline_service import PipelineService
from validation import ValidationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions/{session_id}/phases", tags=["phases"])


# =============================================================================
# Helpers
# =============================================================================


def _get_session_or_404(session_id: str) -> PipelineSession:
    """Retrieve a session or raise 404."""
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session


def _get_phase_or_404(phase_id: str):
    """Retrieve a PhaseConfig or raise 404."""
    phase = get_phase_config(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail=f"Phase '{phase_id}' not found")
    return phase


# =============================================================================
# Phase Execution
# =============================================================================


@router.post("/{phase_id}/run", response_model=RunPhaseResponse)
async def run_phase(
    session_id: str,
    phase_id: str,
    request: RunPhaseRequest = RunPhaseRequest(),
) -> RunPhaseResponse:
    """
    Execute a single pipeline phase.

    Prerequisites: all input phases must be completed (have artifacts).
    Phase 1 (Glossary) has no prerequisites other than requirements.

    The phase runs synchronously — the response contains the generated
    artifact and validation report.
    """
    session = _get_session_or_404(session_id)
    phase = _get_phase_or_404(phase_id)

    # Check prerequisites
    prereq_error = check_phase_prerequisites(session, phase)
    if prereq_error:
        raise HTTPException(status_code=409, detail=prereq_error)

    # Mark phase as running
    phase_state = session.phases[phase.id]
    phase_state.status = PhaseStatus.RUNNING
    phase_state.error = None
    session.touch()

    try:
        # Build services
        llm_service = LLMService(
            provider=session.provider,
            model=session.model,
            temperature=session.temperature,
            api_key=session.api_key,
        )
        artifact_service = ArtifactService()
        validation_engine = ValidationEngine()

        pipeline = PipelineService(
            llm_service=llm_service,
            artifact_service=artifact_service,
            validation_engine=validation_engine,
        )

        # Build workflow state from session
        state = build_workflow_state(session, phase)

        # Execute the phase
        artifact, raw_or_error, report = pipeline.run_phase(
            phase, state, max_retries=request.max_retries,
        )

        if artifact is not None:
            artifact_dict = json.loads(artifact.model_dump_json())
            report_dict = json.loads(report.model_dump_json()) if report else None

            # Update session state
            phase_state.status = PhaseStatus.COMPLETED
            phase_state.artifact = artifact_dict
            phase_state.raw_response = raw_or_error
            phase_state.validation_report = report_dict
            phase_state.error = None
            phase_state.completed_at = datetime.now(timezone.utc).isoformat()
            session.touch()

            # Persist to disk
            domain = session.requirements_name.lower().replace(" ", "_")
            artifact_service.save_artifact(
                domain, session.provider, session.model,
                phase, artifact, raw_or_error,
            )
            if report:
                artifact_service.save_validation_report(
                    domain, session.provider, session.model,
                    phase, report,
                )

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status=PhaseStatus.COMPLETED,
                artifact=artifact_dict,
                validation=report_dict,
            )
        else:
            # Phase failed
            phase_state.status = PhaseStatus.FAILED
            phase_state.error = raw_or_error
            session.touch()

            return RunPhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                status=PhaseStatus.FAILED,
                error=raw_or_error,
            )

    except (ValueError, ConnectionError) as e:
        phase_state.status = PhaseStatus.FAILED
        phase_state.error = str(e)
        session.touch()
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Artifact Retrieval & Editing
# =============================================================================


@router.get("/{phase_id}/artifact", response_model=ArtifactResponse)
async def get_artifact(session_id: str, phase_id: str) -> ArtifactResponse:
    """
    Get the artifact for a completed phase.

    Returns the artifact data as a JSON object matching the phase's
    Pydantic schema.
    """
    session = _get_session_or_404(session_id)
    phase = _get_phase_or_404(phase_id)

    phase_state = session.phases.get(phase.id)
    if not phase_state or phase_state.artifact is None:
        raise HTTPException(
            status_code=404,
            detail=f"No artifact found for phase '{phase.name}'. Run the phase first.",
        )

    return ArtifactResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        artifact=phase_state.artifact,
    )


@router.put("/{phase_id}/artifact", response_model=UpdateArtifactResponse)
async def update_artifact(
    session_id: str,
    phase_id: str,
    request: UpdateArtifactRequest,
) -> UpdateArtifactResponse:
    """
    Update a phase artifact (human edit).

    The edited artifact is validated against the phase's Pydantic schema.
    If validation passes, the artifact is stored and the phase is marked
    as completed. Downstream phases are NOT invalidated automatically.

    Re-run validation via POST .../validate after editing.
    """
    session = _get_session_or_404(session_id)
    phase = _get_phase_or_404(phase_id)

    # Validate the edited artifact against the schema
    try:
        validated = phase.output_schema.model_validate(request.artifact)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Artifact does not conform to {phase.output_schema.__name__} schema: {e}",
        )

    artifact_dict = json.loads(validated.model_dump_json())

    # Run validation
    validation_dict = run_validation_on_artifact(session, phase, artifact_dict)

    # Update session
    phase_state = session.phases[phase.id]
    phase_state.artifact = artifact_dict
    phase_state.status = PhaseStatus.COMPLETED
    phase_state.validation_report = validation_dict
    phase_state.completed_at = datetime.now(timezone.utc).isoformat()
    session.touch()

    return UpdateArtifactResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        artifact=artifact_dict,
        validation=validation_dict,
    )


# =============================================================================
# Validation
# =============================================================================


@router.post("/{phase_id}/validate", response_model=ValidationResponse)
async def validate_phase(session_id: str, phase_id: str) -> ValidationResponse:
    """
    Re-run validation on a phase artifact.

    Useful after editing an artifact to check if the changes fix
    validation issues or introduce new ones.
    """
    session = _get_session_or_404(session_id)
    phase = _get_phase_or_404(phase_id)

    phase_state = session.phases.get(phase.id)
    if not phase_state or phase_state.artifact is None:
        raise HTTPException(
            status_code=404,
            detail=f"No artifact for phase '{phase.name}'. Run the phase first.",
        )

    validation_dict = run_validation_on_artifact(
        session, phase, phase_state.artifact,
    )
    if validation_dict is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to validate artifact",
        )

    # Store updated validation
    phase_state.validation_report = validation_dict
    session.touch()

    return ValidationResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        validation=validation_dict,
    )


@router.get("/{phase_id}/validation", response_model=ValidationResponse)
async def get_validation(session_id: str, phase_id: str) -> ValidationResponse:
    """
    Get the latest validation report for a phase.

    Returns the validation report from the most recent run or validation.
    """
    session = _get_session_or_404(session_id)
    phase = _get_phase_or_404(phase_id)

    phase_state = session.phases.get(phase.id)
    if not phase_state or phase_state.validation_report is None:
        raise HTTPException(
            status_code=404,
            detail=f"No validation report for phase '{phase.name}'.",
        )

    return ValidationResponse(
        phase_id=phase.id,
        phase_name=phase.name,
        validation=phase_state.validation_report,
    )
