"""
FastAPI dependency injection.

Provides:
- Database session via get_db
- SessionRepository via get_repository
- Helper functions for phase lookup, prerequisite checking, and validation
"""

from __future__ import annotations

import json

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db.models import Artifact, Session
from db.repository import SessionRepository
from pipeline_config import PHASES, PhaseConfig, WorkflowState
from validation import ValidationEngine


# =============================================================================
# FastAPI Dependencies
# =============================================================================


def get_repository(db: DBSession = Depends(get_db)) -> SessionRepository:
    """Provide a SessionRepository backed by the current DB session."""
    return SessionRepository(db)


# =============================================================================
# Phase Lookup Helpers
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


# =============================================================================
# Business Logic Helpers
# =============================================================================


def check_phase_prerequisites(
    artifacts: list[Artifact],
    phase: PhaseConfig,
) -> str | None:
    """
    Check whether a phase's input prerequisites are met.

    Returns None if OK, or an error message describing what's missing.
    """
    artifact_map = {a.phase_id: a for a in artifacts}

    for inp in phase.inputs:
        if inp == "requirements":
            continue
        producer = get_phase_by_output_key(inp)
        if producer is None:
            return f"Unknown input '{inp}' — no phase produces it"
        producer_artifact = artifact_map.get(producer.id)
        if producer_artifact is None or producer_artifact.status != "completed":
            return (
                f"Phase '{producer.name}' must be completed before "
                f"running '{phase.name}' (provides '{inp}')"
            )
    return None


def build_workflow_state(
    session: Session,
    artifacts: list[Artifact],
    phase: PhaseConfig,
) -> WorkflowState:
    """
    Build a WorkflowState from DB data for phase execution.

    Converts stored JSONB artifact content back to Pydantic models
    so PipelineService can use them in prompts and validation.
    """
    artifact_map = {a.phase_id: a for a in artifacts}
    pydantic_artifacts: dict[str, BaseModel] = {}

    for inp in phase.inputs:
        if inp == "requirements":
            continue
        producer = get_phase_by_output_key(inp)
        if producer is None:
            continue
        db_artifact = artifact_map.get(producer.id)
        if db_artifact and db_artifact.content:
            pydantic_artifacts[inp] = producer.output_schema.model_validate(
                db_artifact.content,
            )

    domain = session.requirements_name.lower().replace(" ", "_")

    return WorkflowState(
        domain=domain,
        provider=session.provider,
        model=session.model,
        requirements_text=session.requirements_text,
        artifacts=pydantic_artifacts,
    )


def run_validation_on_artifact(
    artifacts: list[Artifact],
    phase: PhaseConfig,
    artifact_dict: dict,
) -> dict | None:
    """
    Run validation on an artifact dict and return the report as a dict.

    Converts all needed artifacts to Pydantic models, runs the engine,
    and returns the serialized report.
    """
    engine = ValidationEngine()
    artifact_map = {a.phase_id: a for a in artifacts}

    pydantic_artifacts: dict[str, BaseModel] = {}
    for p in PHASES:
        if p.id == phase.id:
            continue
        db_artifact = artifact_map.get(p.id)
        if db_artifact and db_artifact.content:
            try:
                pydantic_artifacts[p.output_key] = p.output_schema.model_validate(
                    db_artifact.content,
                )
            except Exception:
                pass

    try:
        pydantic_artifacts[phase.output_key] = phase.output_schema.model_validate(
            artifact_dict,
        )
    except Exception:
        return None

    report = engine.validate_phase(phase.id, pydantic_artifacts)
    return json.loads(report.model_dump_json())
