"""
Pydantic models for Bounded Contexts artifact (Phase 3).

Schema design principles:
- Capture context definitions with clear responsibilities
- Model relationships for Context Map visualization
- Track domain classification (core/supporting/generic)
- Support Mermaid diagram generation via explicit relationships
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# Strategic DDD relationship types
RelationshipType = Literal[
    "partnership",           # Two contexts cooperate as equals
    "shared_kernel",         # Shared subset of the domain model
    "customer_supplier",     # Upstream/downstream with negotiation
    "conformist",            # Downstream conforms to upstream model
    "anticorruption_layer",  # Downstream protects itself with ACL
    "open_host_service",     # Upstream provides well-defined protocol
    "published_language",    # Shared language for communication
    "separate_ways",         # No integration, independent
]

# Domain classification for strategic importance
DomainClassification = Literal[
    "core",        # Primary competitive advantage
    "supporting",  # Necessary but not differentiating
    "generic",     # Could be off-the-shelf
]

# Integration styles for technical decisions
IntegrationStyle = Literal[
    "synchronous_api",     # REST/gRPC calls
    "asynchronous_events", # Event-driven messaging
    "shared_database",     # Direct DB access (discouraged)
    "file_transfer",       # Batch file exchange
    "none",                # No runtime integration
]


class BoundedContext(BaseModel):
    """A bounded context representing a linguistic and model boundary."""

    name: str = Field(
        ...,
        description="Context name (e.g., 'Reservation', 'Billing', 'Identity')"
    )
    purpose: str = Field(
        ...,
        description="Core purpose and single responsibility of this context"
    )
    classification: DomainClassification = Field(
        ...,
        description="Strategic classification: core, supporting, or generic"
    )

    # Content from previous phases
    key_aggregates: list[str] = Field(
        ...,
        description="Main aggregates that belong to this context"
    )
    ubiquitous_language_terms: list[str] = Field(
        ...,
        description="Glossary terms specific to this context"
    )
    owned_events: list[str] = Field(
        default_factory=list,
        description="Domain events published by this context"
    )
    handled_commands: list[str] = Field(
        default_factory=list,
        description="Commands processed by this context"
    )

    # Team/ownership hints
    team_ownership: Optional[str] = Field(
        None,
        description="Suggested team or ownership area"
    )

    # Concerns
    boundary_concerns: Optional[str] = Field(
        None,
        description="Any concerns about this context's boundary or size"
    )


class ContextRelationship(BaseModel):
    """
    A relationship between two bounded contexts.
    
    Designed for Context Map visualization - each relationship becomes an edge.
    """

    upstream_context: str = Field(
        ...,
        description="The upstream (supplier/provider) context name"
    )
    downstream_context: str = Field(
        ...,
        description="The downstream (consumer) context name"
    )
    relationship_type: RelationshipType = Field(
        ...,
        description="Strategic DDD relationship pattern"
    )
    description: str = Field(
        ...,
        description="How these contexts interact and why this relationship type"
    )
    integration_style: IntegrationStyle = Field(
        default="asynchronous_events",
        description="Technical integration approach"
    )
    shared_model_elements: list[str] = Field(
        default_factory=list,
        description="Events, APIs, or data shared between contexts"
    )
    acl_needed: bool = Field(
        default=False,
        description="Whether downstream needs Anti-Corruption Layer protection"
    )
    acl_rationale: Optional[str] = Field(
        None,
        description="Why ACL is needed (if applicable)"
    )


class SharedTerm(BaseModel):
    """
    A term that has different meanings across bounded contexts.
    
    Important for identifying where translation/ACL is needed.
    """

    term: str = Field(
        ...,
        description="The term that differs across contexts"
    )
    definitions_by_context: dict[str, str] = Field(
        ...,
        description="Mapping of context name to meaning in that context"
    )
    translation_strategy: str = Field(
        ...,
        description="How to handle translation between contexts"
    )


class ExternalSystem(BaseModel):
    """An external system that interacts with bounded contexts."""

    name: str = Field(
        ...,
        description="External system name (e.g., 'PaymentGateway', 'EmailService')"
    )
    description: str = Field(
        ...,
        description="What this external system provides"
    )
    integration_contexts: list[str] = Field(
        ...,
        description="Bounded contexts that integrate with this system"
    )
    integration_style: IntegrationStyle = Field(
        ...,
        description="How contexts integrate with this external system"
    )
    acl_recommended: bool = Field(
        default=True,
        description="Whether ACL is recommended for this external integration"
    )


class BoundedContextsArtifact(BaseModel):
    """
    Complete Bounded Contexts artifact for Phase 3 of the DDD workflow.
    
    Designed for:
    - Machine-readable JSON storage
    - Mermaid Context Map generation
    - Strategic domain analysis
    - Cross-phase validation
    """

    # Bounded contexts (nodes in Context Map)
    contexts: list[BoundedContext] = Field(
        ...,
        description="All identified bounded contexts"
    )

    # Relationships (edges in Context Map)
    relationships: list[ContextRelationship] = Field(
        ...,
        description="Relationships between bounded contexts"
    )

    # External integrations
    external_systems: list[ExternalSystem] = Field(
        default_factory=list,
        description="External systems and their integrations"
    )

    # Terms that need translation
    shared_terms: list[SharedTerm] = Field(
        default_factory=list,
        description="Terms with different meanings across contexts"
    )

    # Strategic summary
    core_domain: Optional[str] = Field(
        None,
        description="The primary context providing competitive advantage"
    )
    core_domain_rationale: Optional[str] = Field(
        None,
        description="Why this context is considered core"
    )

    # Concerns and recommendations
    boundary_recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for splitting or merging contexts"
    )
    integration_concerns: list[str] = Field(
        default_factory=list,
        description="Concerns about context integrations"
    )

    # Metadata
    schema_version: str = Field(
        default="1.0",
        description="Schema version for compatibility"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "contexts": [
                        {
                            "name": "Reservation",
                            "purpose": "Manage room bookings and availability",
                            "classification": "core",
                            "key_aggregates": ["Booking", "Room"],
                            "ubiquitous_language_terms": ["Booking", "Room", "TimeSlot", "Availability"],
                            "owned_events": ["RoomBooked", "BookingCancelled", "RoomReleased"],
                            "handled_commands": ["BookRoom", "CancelBooking", "ModifyBooking"],
                            "team_ownership": "Booking Team",
                            "boundary_concerns": None
                        },
                        {
                            "name": "Notification",
                            "purpose": "Handle all outbound communications",
                            "classification": "supporting",
                            "key_aggregates": ["Notification", "Template"],
                            "ubiquitous_language_terms": ["Notification", "Channel", "Template"],
                            "owned_events": ["NotificationSent", "NotificationFailed"],
                            "handled_commands": ["SendEmail", "SendSMS"],
                            "team_ownership": "Platform Team",
                            "boundary_concerns": None
                        }
                    ],
                    "relationships": [
                        {
                            "upstream_context": "Reservation",
                            "downstream_context": "Notification",
                            "relationship_type": "customer_supplier",
                            "description": "Reservation publishes events that Notification reacts to",
                            "integration_style": "asynchronous_events",
                            "shared_model_elements": ["RoomBooked", "BookingCancelled"],
                            "acl_needed": False,
                            "acl_rationale": None
                        }
                    ],
                    "external_systems": [
                        {
                            "name": "SendGrid",
                            "description": "Email delivery service",
                            "integration_contexts": ["Notification"],
                            "integration_style": "synchronous_api",
                            "acl_recommended": True
                        }
                    ],
                    "shared_terms": [
                        {
                            "term": "User",
                            "definitions_by_context": {
                                "Reservation": "A guest who can make bookings",
                                "Identity": "An authenticated account with credentials"
                            },
                            "translation_strategy": "Map User ID; Reservation sees Guest, Identity sees Account"
                        }
                    ],
                    "core_domain": "Reservation",
                    "core_domain_rationale": "Room booking is the primary business value",
                    "boundary_recommendations": [],
                    "integration_concerns": ["Consider async for payment to avoid blocking bookings"],
                    "schema_version": "1.0"
                }
            ]
        }
    }
