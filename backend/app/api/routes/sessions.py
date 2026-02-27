"""
Session management endpoints.

Sessions track the HITL pipeline workflow — one session per requirements
document. The user creates a session, then runs phases one at a time.
"""

import uuid
from fastapi import APIRouter, HTTPException

from api.schemas import (
    CreateSessionRequest,
    PhaseResponse,
    PhaseStatus,
    SessionListResponse,
    SessionResponse,
)
from api.dependencies import PipelineSession, session_store
from pipeline_config import PHASES

router = APIRouter(prefix="/sessions", tags=["sessions"])


# =============================================================================
# Helpers
# =============================================================================


def _session_to_response(session: PipelineSession) -> SessionResponse:
    """Convert a PipelineSession to an API response."""
    phase_responses = []
    for phase in PHASES:
        ps = session.phases.get(phase.id)
        phase_responses.append(
            PhaseResponse(
                phase_id=phase.id,
                phase_name=phase.name,
                phase_number=phase.phase_number,
                status=ps.status if ps else PhaseStatus.PENDING,
                has_artifact=ps.artifact is not None if ps else False,
                has_validation=ps.validation_report is not None if ps else False,
            )
        )
    return SessionResponse(
        id=session.id,
        requirements_name=session.requirements_name,
        provider=session.provider,
        model=session.model,
        temperature=session.temperature,
        phases=phase_responses,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _get_session_or_404(session_id: str) -> PipelineSession:
    """Retrieve a session or raise 404."""
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session


# =============================================================================
# Endpoints
# =============================================================================


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """
    Create a new pipeline session.

    A session holds the requirements text, model configuration, and
    tracks phase execution state. Each phase is run individually.
    """
    session = PipelineSession(
        id=str(uuid.uuid4())[:8],
        requirements_text=request.requirements_text,
        requirements_name=request.requirements_name,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        api_key=request.api_key,
    )
    session_store.create(session)
    return _session_to_response(session)


@router.get("", response_model=SessionListResponse)
async def list_sessions() -> SessionListResponse:
    """List all pipeline sessions."""
    sessions = session_store.list_all()
    return SessionListResponse(
        sessions=[_session_to_response(s) for s in sessions],
        count=len(sessions),
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get details of a specific pipeline session."""
    session = _get_session_or_404(session_id)
    return _session_to_response(session)


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """Delete a pipeline session."""
    if not session_store.delete(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
