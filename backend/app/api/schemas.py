"""
API request/response schemas for the DDD pipeline.

Pydantic models for HTTP request bodies and response payloads.
These are separate from the domain models in models/ — they define
the shape of the API contract, not the DDD artifacts themselves.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================


class PhaseStatus(str, Enum):
    """Status of a pipeline phase within a session."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Session Schemas
# =============================================================================


class CreateSessionRequest(BaseModel):
    """Request body for creating a new pipeline session."""
    requirements_text: str = Field(
        ..., description="Full requirements document text",
    )
    requirements_name: str = Field(
        default="requirements",
        description="Human-readable name for the requirements",
    )
    provider: str = Field(
        default="ollama",
        description="LLM provider: 'ollama' or 'openrouter'",
    )
    model: str = Field(
        default="llama3.2",
        description="Model name (e.g., 'openai/gpt-4o' for OpenRouter)",
    )
    temperature: float = Field(
        default=0.3,
        description="LLM temperature (0.0–1.0)",
        ge=0.0,
        le=1.0,
    )
    api_key: str | None = Field(
        default=None,
        description="API key for OpenRouter (overrides env var)",
    )


class PhaseResponse(BaseModel):
    """Status of a single phase within a session."""
    phase_id: str
    phase_name: str
    phase_number: int
    status: PhaseStatus
    has_artifact: bool
    has_validation: bool


class SessionResponse(BaseModel):
    """Response for a pipeline session."""
    id: str
    requirements_name: str
    provider: str
    model: str
    temperature: float
    phases: list[PhaseResponse]
    created_at: str
    updated_at: str


class SessionListResponse(BaseModel):
    """Response for listing sessions."""
    sessions: list[SessionResponse]
    count: int


# =============================================================================
# Phase Execution Schemas
# =============================================================================


class RunPhaseRequest(BaseModel):
    """Request body for executing a pipeline phase."""
    max_retries: int = Field(
        default=2,
        description="Maximum retries on failure",
        ge=0,
        le=5,
    )


class RunPhaseResponse(BaseModel):
    """Response after executing a pipeline phase."""
    phase_id: str
    phase_name: str
    status: PhaseStatus
    artifact: dict | None = None
    validation: dict | None = None
    error: str | None = None


# =============================================================================
# Artifact Schemas
# =============================================================================


class ArtifactResponse(BaseModel):
    """Response for retrieving a phase artifact."""
    phase_id: str
    phase_name: str
    artifact: dict


class UpdateArtifactRequest(BaseModel):
    """Request body for updating a phase artifact (human edit)."""
    artifact: dict = Field(
        ..., description="The edited artifact data (must conform to phase schema)",
    )


class UpdateArtifactResponse(BaseModel):
    """Response after updating a phase artifact."""
    phase_id: str
    phase_name: str
    artifact: dict
    validation: dict | None = None


# =============================================================================
# Validation Schemas
# =============================================================================


class ValidationResponse(BaseModel):
    """Response for validation results."""
    phase_id: str
    phase_name: str
    validation: dict


# =============================================================================
# Health Check
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "0.1.0"
    phases_available: int
