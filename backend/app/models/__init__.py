"""
Structured output models for the 5-phase DDD pipeline.

Each module defines the Pydantic schema that the LLM must produce
via `with_structured_output()`. These are the artifact *payloads*
stored in JSONB; persistence metadata is handled separately.
"""

from models.glossary import GlossaryArtifact, GlossaryTerm, BoundedContextHint
from models.event_storming import (
    EventStormingArtifact,
    Command,
    DomainEvent,
    Policy,
    FlowStep,
    EventFlow,
)
from models.bounded_contexts import (
    BoundedContextsArtifact,
    BoundedContext,
    ContextRelationship,
    ContextSpecificMeaning,
    TermOverlap,
)
from models.aggregates import (
    AggregatesArtifact,
    Aggregate,
    AggregateElement,
    AggregateCommand,
    Invariant,
)
from models.architecture import (
    ArchitectureArtifact,
    HexagonalArchitecture,
    DomainLayerElement,
    ApplicationLayerElement,
    InfrastructureLayerElement,
    PresentationLayerElement,
    AntiCorruptionLayer,
    PublishedInterface,
    TechnicalPattern,
)

__all__ = [
    # Phase 1
    "GlossaryArtifact",
    "GlossaryTerm",
    "BoundedContextHint",
    # Phase 2
    "EventStormingArtifact",
    "Command",
    "DomainEvent",
    "Policy",
    "FlowStep",
    "EventFlow",
    # Phase 3
    "BoundedContextsArtifact",
    "BoundedContext",
    "ContextRelationship",
    "ContextSpecificMeaning",
    "TermOverlap",
    # Phase 4
    "AggregatesArtifact",
    "Aggregate",
    "AggregateElement",
    "AggregateCommand",
    "Invariant",
    # Phase 5
    "ArchitectureArtifact",
    "HexagonalArchitecture",
    "DomainLayerElement",
    "ApplicationLayerElement",
    "InfrastructureLayerElement",
    "PresentationLayerElement",
    "AntiCorruptionLayer",
    "PublishedInterface",
    "TechnicalPattern",
]
