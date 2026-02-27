"""
Pipeline configuration — phase definitions, system prompts, and workflow state.

Centralizes all pipeline configuration that is shared across services.
This module is intentionally free of business logic; it only defines data.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel

from models.glossary import GlossaryArtifact
from models.event_storming import EventStormingArtifact
from models.bounded_contexts import BoundedContextsArtifact
from models.aggregates import AggregatesArtifact
from models.architecture import ArchitectureArtifact
from validation.models import ValidationReport

# =============================================================================
# Path Constants
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = DATA_DIR / "prompts"
REQUIREMENTS_DIR = DATA_DIR / "requirements"

# =============================================================================
# Phase Configuration
# =============================================================================


@dataclass
class PhaseConfig:
    """
    Configuration for a single DDD modeling phase.

    Attributes:
        id: Unique phase identifier (e.g., '01_glossary')
        name: Human-readable phase name
        inputs: List of artifact keys required as input
        output_key: Key to store the output artifact under
        output_schema: Pydantic model class for structured output
        system_prompt: Optional system message for better LLM guidance
    """

    id: str
    name: str
    inputs: list[str]
    output_key: str
    output_schema: type[BaseModel]
    system_prompt: str = ""

    @property
    def prompt_file(self) -> str:
        return f"{self.id}.txt"

    @property
    def phase_number(self) -> int:
        return int(self.id.split("_")[0])


# =============================================================================
# System Prompts
# =============================================================================

GLOSSARY_SYSTEM_PROMPT = (
    "You are a Domain-Driven Design (DDD) expert specializing in ubiquitous "
    "language extraction.\nYour task is to analyze requirements and extract "
    "domain terms with precise, business-focused definitions.\nFocus on "
    "clarity, consistency, and identifying potential bounded context boundaries."
)

EVENT_STORMING_SYSTEM_PROMPT = (
    "You are a Domain-Driven Design (DDD) expert facilitating an Event "
    "Storming session.\nYour task is to identify domain events, commands, "
    "actors, and policies from the requirements and glossary.\nFocus on "
    "temporal flows, cause-effect relationships, and business process boundaries."
)

BOUNDED_CONTEXTS_SYSTEM_PROMPT = (
    "You are a Domain-Driven Design (DDD) expert specializing in strategic "
    "design.\nYour task is to identify bounded contexts and their relationships "
    "from the domain model.\nFocus on linguistic boundaries, team ownership, "
    "and integration patterns."
)

AGGREGATES_SYSTEM_PROMPT = (
    "You are a Domain-Driven Design (DDD) expert specializing in tactical "
    "design.\nYour task is to design aggregates with clear consistency "
    "boundaries and invariants.\nFocus on transactional boundaries, entity vs "
    "value object distinctions, and aggregate sizing."
)

ARCHITECTURE_SYSTEM_PROMPT = (
    "You are a Domain-Driven Design (DDD) expert specializing in technical "
    "architecture.\nYour task is to map the domain model to a hexagonal "
    "architecture with clear layer responsibilities.\nFocus on ports/adapters, "
    "anti-corruption layers, and integration patterns."
)

# =============================================================================
# Phase Registry
# =============================================================================

PHASES: list[PhaseConfig] = [
    PhaseConfig(
        id="01_glossary",
        name="Glossary",
        inputs=["requirements"],
        output_key="glossary",
        output_schema=GlossaryArtifact,
        system_prompt=GLOSSARY_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="02_event_storming",
        name="Event Storming",
        inputs=["requirements", "glossary"],
        output_key="events",
        output_schema=EventStormingArtifact,
        system_prompt=EVENT_STORMING_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="03_bounded_contexts",
        name="Bounded Contexts",
        inputs=["requirements", "glossary", "events"],
        output_key="bounded_contexts",
        output_schema=BoundedContextsArtifact,
        system_prompt=BOUNDED_CONTEXTS_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="04_aggregates",
        name="Aggregates",
        inputs=["glossary", "events", "bounded_contexts"],
        output_key="aggregates",
        output_schema=AggregatesArtifact,
        system_prompt=AGGREGATES_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="05_architecture",
        name="Architecture",
        inputs=["bounded_contexts", "aggregates"],
        output_key="architecture",
        output_schema=ArchitectureArtifact,
        system_prompt=ARCHITECTURE_SYSTEM_PROMPT,
    ),
]


# =============================================================================
# Workflow State
# =============================================================================


@dataclass
class WorkflowState:
    """
    Maintains state across workflow execution.

    Stores artifacts, metadata, and provides serialization for downstream phases.
    Supports both file-path and text-based requirements for CLI and API usage.
    """

    domain: str
    provider: str
    model: str
    requirements_path: Path | None = None
    requirements_text: str | None = None
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    artifacts: dict[str, BaseModel] = field(default_factory=dict)
    raw_responses: dict[str, str] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    validation_reports: dict[str, ValidationReport] = field(default_factory=dict)

    def get_requirements_content(self) -> str:
        """Get requirements text, from either text field or file path."""
        if self.requirements_text:
            return self.requirements_text
        if self.requirements_path:
            return self.requirements_path.read_text(encoding="utf-8")
        raise ValueError("No requirements provided (need requirements_text or requirements_path)")

    def get_artifact_as_json(self, key: str) -> str:
        """
        Get artifact serialized as JSON for use in prompts.

        Downstream phases receive previous artifacts as JSON strings,
        allowing the LLM to parse and reference structured data.
        """
        artifact = self.artifacts.get(key)
        if artifact is None:
            return ""
        return artifact.model_dump_json(indent=2)

    def get_requirements_hash(self) -> str:
        """Generate a hash of the requirements for traceability."""
        content = self.get_requirements_content()
        return hashlib.sha256(content.encode()).hexdigest()[:16]

