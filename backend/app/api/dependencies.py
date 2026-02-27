"""
Dependency injection for the FastAPI application.

Provides:
- SessionStore: In-memory session store (will be replaced with DB in Phase C)
- PipelineSession: Session data model
- Helper functions to resolve phases and build WorkflowState from sessions

Design note:
    All state is stored in-memory. This is intentional for now —
    Phase C will introduce PostgreSQL persistence.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pydantic import BaseModel

from api.schemas import PhaseStatus
from pipeline_config import PHASES, PhaseConfig, WorkflowState
from validation import ValidationEngine
from validation.models import ValidationReport


# =============================================================================
# Session Data Model
# =============================================================================


@dataclass
class PhaseState:
    """State of a single phase within a session."""
    status: PhaseStatus = PhaseStatus.PENDING
    artifact: dict | None = None
    raw_response: str | None = None
    validation_report: dict | None = None
    error: str | None = None
    completed_at: str | None = None


@dataclass
class PipelineSession:
    """
    A pipeline session tracks the state of a HITL workflow.

    The user creates a session with requirements + model config,
    then runs phases one at a time, reviewing artifacts between phases.
    """
    id: str
    requirements_text: str
    requirements_name: str
    provider: str
    model: str
    temperature: float
    api_key: str | None
    phases: dict[str, PhaseState] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        # Initialize all phase states
        if not self.phases:
            for phase in PHASES:
                self.phases[phase.id] = PhaseState()

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()


# =============================================================================
# Session Store (in-memory, replaced with DB in Phase C)
# =============================================================================


class SessionStore:
    """
    In-memory session store.

    Thread-safety note: For development only. Production deployments
    should use the database-backed store from Phase C.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, PipelineSession] = {}

    def create(self, session: PipelineSession) -> PipelineSession:
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> PipelineSession | None:
        return self._sessions.get(session_id)

    def list_all(self) -> list[PipelineSession]:
        return list(self._sessions.values())

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# =============================================================================
# Singleton store instance
# =============================================================================

session_store = SessionStore()


# =============================================================================
# Helper Functions
# =============================================================================


def get_phase_config(phase_id: str) -> PhaseConfig | None:
    """Look up a PhaseConfig by its ID."""
    for phase in PHASES:
        if phase.id == phase_id:
            return phase
    return None


def get_phase_by_output_key(output_key: str) -> PhaseConfig | None:
    """Look up a PhaseConfig by its output_key."""
    for phase in PHASES:
        if phase.output_key == output_key:
            return phase
    return None


def check_phase_prerequisites(session: PipelineSession, phase: PhaseConfig) -> str | None:
    """
    Check whether a phase's prerequisites are met.

    Returns None if OK, or an error message describing what's missing.
    """
    for inp in phase.inputs:
        if inp == "requirements":
            continue  # Always available from session
        # Find the phase that produces this input
        producer = get_phase_by_output_key(inp)
        if producer is None:
            return f"Unknown input '{inp}' — no phase produces it"
        producer_state = session.phases.get(producer.id)
        if producer_state is None or producer_state.status != PhaseStatus.COMPLETED:
            return (
                f"Phase '{producer.name}' must be completed before "
                f"running '{phase.name}' (provides '{inp}')"
            )
    return None


def build_workflow_state(
    session: PipelineSession,
    phase: PhaseConfig,
) -> WorkflowState:
    """
    Build a WorkflowState from session data for phase execution.

    Converts stored artifact dicts back to Pydantic models so the
    pipeline service can use them in prompts and validation.
    """
    artifacts: dict[str, BaseModel] = {}

    for inp in phase.inputs:
        if inp == "requirements":
            continue
        producer = get_phase_by_output_key(inp)
        if producer is None:
            continue
        phase_state = session.phases.get(producer.id)
        if phase_state and phase_state.artifact:
            # Convert dict back to Pydantic model
            artifacts[inp] = producer.output_schema.model_validate(
                phase_state.artifact,
            )

    domain = session.requirements_name.lower().replace(" ", "_")

    return WorkflowState(
        domain=domain,
        provider=session.provider,
        model=session.model,
        requirements_text=session.requirements_text,
        artifacts=artifacts,
    )


def run_validation_on_artifact(
    session: PipelineSession,
    phase: PhaseConfig,
    artifact_dict: dict,
) -> dict | None:
    """
    Run validation on an artifact dict and return the report as a dict.

    Converts all needed artifacts to Pydantic models, runs the engine,
    and returns the serialized report.
    """
    engine = ValidationEngine()

    # Build artifacts dict with Pydantic models
    artifacts: dict[str, BaseModel] = {}
    for p in PHASES:
        ps = session.phases.get(p.id)
        if ps and ps.artifact and p.id != phase.id:
            try:
                artifacts[p.output_key] = p.output_schema.model_validate(ps.artifact)
            except Exception:
                pass

    # Add the artifact being validated
    try:
        artifacts[phase.output_key] = phase.output_schema.model_validate(artifact_dict)
    except Exception:
        return None

    report = engine.validate_phase(phase.id, artifacts)
    return json.loads(report.model_dump_json())
