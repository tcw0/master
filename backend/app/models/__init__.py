"""
Pydantic models for DDD artifacts across all pipeline phases.

Each phase produces a structured artifact:
- Phase 1: GlossaryArtifact (Ubiquitous Language)
- Phase 2: EventStormingArtifact (Events, Commands, Actors, Policies)
- Phase 3: BoundedContextsArtifact (Context Map)
- Phase 4: AggregatesArtifact (Aggregate Design)
- Phase 5: ArchitectureArtifact (Technical Architecture)
"""

# Phase 1: Glossary (Ubiquitous Language)
from backend.app.models.glossary import (
    GlossaryTerm,
    BoundedContextIndicator,
    GlossaryArtifact,
)

# Phase 2: Event Storming
from backend.app.models.event_storming import (
    Actor,
    DomainEvent,
    Command,
    Policy,
    EventFlow,
    HotSpot,
    EventStormingArtifact,
)

# Phase 3: Bounded Contexts
from backend.app.models.bounded_contexts import (
    BoundedContext,
    ContextRelationship,
    SharedTerm,
    ExternalSystem,
    BoundedContextsArtifact,
)

# Phase 4: Aggregates
from backend.app.models.aggregates import (
    Attribute,
    ValueObject,
    EnumDefinition,
    Entity,
    AggregateCommand,
    Invariant,
    Aggregate,
    CrossAggregateInteraction,
    AggregatesArtifact,
)

# Phase 5: Architecture
from backend.app.models.architecture import (
    Component,
    DomainLayer,
    ApplicationLayer,
    InfrastructureLayer,
    PresentationLayer,
    HexagonalArchitecture,
    AntiCorruptionLayer,
    PublishedInterface,
    TechnicalPattern,
    ContextArchitecture,
    DeploymentUnit,
    ArchitectureArtifact,
)

__all__ = [
    # Phase 1
    "GlossaryTerm",
    "BoundedContextIndicator",
    "GlossaryArtifact",
    # Phase 2
    "Actor",
    "DomainEvent",
    "Command",
    "Policy",
    "EventFlow",
    "HotSpot",
    "EventStormingArtifact",
    # Phase 3
    "BoundedContext",
    "ContextRelationship",
    "SharedTerm",
    "ExternalSystem",
    "BoundedContextsArtifact",
    # Phase 4
    "Attribute",
    "ValueObject",
    "EnumDefinition",
    "Entity",
    "AggregateCommand",
    "Invariant",
    "Aggregate",
    "CrossAggregateInteraction",
    "AggregatesArtifact",
    # Phase 5
    "Component",
    "DomainLayer",
    "ApplicationLayer",
    "InfrastructureLayer",
    "PresentationLayer",
    "HexagonalArchitecture",
    "AntiCorruptionLayer",
    "PublishedInterface",
    "TechnicalPattern",
    "ContextArchitecture",
    "DeploymentUnit",
    "ArchitectureArtifact",
]
