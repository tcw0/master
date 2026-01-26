"""
Base classes and shared types for DDD artifact models.

This module provides:
- Common type aliases used across phases
- Base artifact class with shared metadata
- Utility functions for artifact management
"""

from typing import TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field


# Type alias for artifact content (the actual LLM output)
ArtifactContent = TypeVar("ArtifactContent", bound=BaseModel)


class ArtifactMetadata(BaseModel):
    """
    Metadata attached to every artifact for traceability and reproducibility.
    
    This is populated by the system, not by the LLM.
    """
    
    # Identification
    artifact_id: str = Field(
        ...,
        description="Unique identifier for this artifact instance"
    )
    artifact_type: str = Field(
        ...,
        description="Type of artifact: glossary, event_storming, bounded_contexts, aggregates, architecture"
    )
    
    # Pipeline context
    pipeline_run_id: str = Field(
        ...,
        description="ID of the pipeline run that produced this artifact"
    )
    phase: str = Field(
        ...,
        description="Phase identifier (e.g., '01_glossary', '02_event_storming')"
    )
    phase_number: int = Field(
        ...,
        ge=1,
        le=5,
        description="Phase number (1-5)"
    )
    
    # Lineage
    parent_artifact_ids: list[str] = Field(
        default_factory=list,
        description="IDs of artifacts this was generated from"
    )
    requirements_hash: str = Field(
        ...,
        description="Hash of the requirements document used"
    )
    
    # Model/prompt info
    model_provider: str = Field(
        ...,
        description="LLM provider (e.g., 'ollama', 'openai')"
    )
    model_name: str = Field(
        ...,
        description="Model name (e.g., 'llama3.2', 'gpt-4')"
    )
    model_parameters: dict = Field(
        default_factory=dict,
        description="Model parameters (temperature, etc.)"
    )
    prompt_version: str = Field(
        ...,
        description="Version or hash of the prompt template used"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this artifact was created"
    )
    
    # Validation summary
    validation_status: str = Field(
        default="pending",
        description="Validation status: pending, passed, warnings, failed"
    )
    validation_errors: int = Field(
        default=0,
        description="Number of validation errors"
    )
    validation_warnings: int = Field(
        default=0,
        description="Number of validation warnings"
    )
    
    # Human review
    reviewed_by: str | None = Field(
        default=None,
        description="User who reviewed this artifact"
    )
    reviewed_at: datetime | None = Field(
        default=None,
        description="When the artifact was reviewed"
    )
    review_status: str = Field(
        default="pending",
        description="Review status: pending, approved, rejected, needs_revision"
    )


class StoredArtifact(BaseModel, Generic[ArtifactContent]):
    """
    A complete stored artifact with metadata and content.
    
    This is the full record stored in the database, combining:
    - System-generated metadata for traceability
    - LLM-generated content (the actual artifact)
    """
    
    metadata: ArtifactMetadata = Field(
        ...,
        description="System-generated metadata"
    )
    content: ArtifactContent = Field(
        ...,
        description="The actual artifact content from the LLM"
    )
    
    # Raw response for debugging
    raw_response: str | None = Field(
        default=None,
        description="Raw LLM response (for debugging parse failures)"
    )


# Mapping of phase IDs to artifact types
PHASE_ARTIFACT_TYPES = {
    "01_glossary": "glossary",
    "02_event_storming": "event_storming", 
    "03_bounded_contexts": "bounded_contexts",
    "04_aggregates": "aggregates",
    "05_architecture": "architecture",
}

# Mapping of phase numbers to phase IDs
PHASE_IDS = {
    1: "01_glossary",
    2: "02_event_storming",
    3: "03_bounded_contexts",
    4: "04_aggregates",
    5: "05_architecture",
}
