"""
Session management endpoints.

Sessions track the HITL pipeline workflow — one session per requirements
document + model configuration.
"""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_repository
from api.schemas import (
    CreateSessionRequest,
    PhaseResponse,
    SessionListResponse,
    SessionResponse,
)
from db.models import Session
from db.repository import SessionRepository
from pipeline_config import PHASES

router = APIRouter(prefix="/sessions", tags=["sessions"])


# =============================================================================
# Helpers
# =============================================================================


def _session_to_response(
    session: Session,
    repo: SessionRepository,
) -> SessionResponse:
    """Convert a DB Session to an API response."""
    latest_artifacts = repo.get_latest_artifacts(session.id)
    artifact_map = {a.phase_id: a for a in latest_artifacts}

    phase_responses = []
    for phase in PHASES:
        db_art = artifact_map.get(phase.id)
        if db_art:
            phase_responses.append(
                PhaseResponse(
                    phase_id=phase.id,
                    phase_name=phase.name,
                    phase_number=phase.phase_number,
                    status=db_art.status,
                    has_artifact=db_art.content is not None,
                    has_validation=db_art.validation_report is not None,
                    version=db_art.version,
                    source=db_art.source,
                )
            )
        else:
            phase_responses.append(
                PhaseResponse(
                    phase_id=phase.id,
                    phase_name=phase.name,
                    phase_number=phase.phase_number,
                    status="pending",
                    has_artifact=False,
                    has_validation=False,
                )
            )

    return SessionResponse(
        id=str(session.id),
        requirements_text=session.requirements_text,
        requirements_name=session.requirements_name,
        provider=session.provider,
        model=session.model,
        temperature=session.temperature,
        phases=phase_responses,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(
    request: CreateSessionRequest,
    repo: SessionRepository = Depends(get_repository),
) -> SessionResponse:
    """Create a new pipeline session with requirements + model config."""
    session = repo.create_session(
        requirements_text=request.requirements_text,
        requirements_name=request.requirements_name,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
    )
    return _session_to_response(session, repo)


@router.get("", response_model=SessionListResponse)
def list_sessions(
    repo: SessionRepository = Depends(get_repository),
) -> SessionListResponse:
    """List all pipeline sessions."""
    sessions = repo.list_sessions()
    return SessionListResponse(
        sessions=[_session_to_response(s, repo) for s in sessions],
        count=len(sessions),
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> SessionResponse:
    """Get details of a specific pipeline session."""
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return _session_to_response(session, repo)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    repo: SessionRepository = Depends(get_repository),
) -> None:
    """Delete a pipeline session and all its artifact versions."""
    if not repo.delete_session(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
