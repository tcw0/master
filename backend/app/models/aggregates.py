"""
Pydantic models for Aggregates artifact (Phase 4).

Schema design principles:
- Capture aggregate structure with clear consistency boundaries
- Model entities, value objects, and their relationships
- Define invariants as explicit business rules
- Support Mermaid class diagram generation
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# Element types for visualization styling
ElementType = Literal["aggregate_root", "entity", "value_object", "enum"]

# Size evaluation for aggregate design review
SizeEvaluation = Literal[
    "appropriate",        # Well-sized for concurrency and consistency
    "possibly_too_large", # Consider splitting
    "possibly_too_small", # Consider merging or this is a VO
]


class Attribute(BaseModel):
    """An attribute of an entity or value object."""

    name: str = Field(
        ...,
        description="Attribute name in camelCase (e.g., 'startTime', 'emailAddress')"
    )
    type: str = Field(
        ...,
        description="Data type (e.g., 'string', 'DateTime', 'Money', 'BookingId')"
    )
    is_required: bool = Field(
        default=True,
        description="Whether this attribute is required"
    )
    description: Optional[str] = Field(
        None,
        description="Business meaning of this attribute"
    )


class ValueObject(BaseModel):
    """
    A value object - immutable, identity-less, defined by its attributes.
    
    Examples: Money, EmailAddress, TimeSlot, Address
    """

    name: str = Field(
        ...,
        description="Value object name in PascalCase (e.g., 'TimeSlot', 'EmailAddress')"
    )
    description: str = Field(
        ...,
        description="What this value object represents"
    )
    attributes: list[Attribute] = Field(
        ...,
        description="Attributes that make up this value object"
    )
    validation_rules: list[str] = Field(
        default_factory=list,
        description="Validation rules for this value object (e.g., 'End must be after Start')"
    )
    is_reusable: bool = Field(
        default=False,
        description="Whether this VO is used across multiple aggregates"
    )


class EnumDefinition(BaseModel):
    """An enumeration of allowed values."""

    name: str = Field(
        ...,
        description="Enum name in PascalCase (e.g., 'BookingStatus', 'RoomType')"
    )
    description: str = Field(
        ...,
        description="What this enum represents"
    )
    values: list[str] = Field(
        ...,
        description="Allowed values in UPPER_SNAKE_CASE (e.g., ['PENDING', 'CONFIRMED', 'CANCELLED'])"
    )


class Entity(BaseModel):
    """
    An entity within an aggregate (not the root).
    
    Has identity, but lifecycle is controlled by the aggregate root.
    """

    name: str = Field(
        ...,
        description="Entity name in PascalCase"
    )
    description: str = Field(
        ...,
        description="What this entity represents"
    )
    identity_attribute: str = Field(
        ...,
        description="Attribute that uniquely identifies this entity (e.g., 'lineItemId')"
    )
    attributes: list[Attribute] = Field(
        default_factory=list,
        description="Entity attributes"
    )
    value_objects: list[str] = Field(
        default_factory=list,
        description="Names of value objects used by this entity"
    )
    relationship_to_root: str = Field(
        ...,
        description="How this entity relates to the aggregate root (e.g., 'Booking contains many LineItems')"
    )


class AggregateCommand(BaseModel):
    """A command/method that an aggregate can handle."""

    name: str = Field(
        ...,
        description="Command name in camelCase or imperative form (e.g., 'book', 'cancel', 'reschedule')"
    )
    description: str = Field(
        ...,
        description="What this command does"
    )
    parameters: list[str] = Field(
        default_factory=list,
        description="Input parameters (e.g., ['newTimeSlot: TimeSlot', 'reason: string'])"
    )
    preconditions: list[str] = Field(
        default_factory=list,
        description="Business conditions that must be true before execution"
    )
    postconditions: list[str] = Field(
        default_factory=list,
        description="State changes after successful execution"
    )
    events_raised: list[str] = Field(
        default_factory=list,
        description="Domain events raised on success"
    )
    exceptions: list[str] = Field(
        default_factory=list,
        description="Errors that can be thrown (e.g., 'RoomNotAvailable', 'BookingAlreadyCancelled')"
    )


class Invariant(BaseModel):
    """A business rule that the aggregate must always protect."""

    name: str = Field(
        ...,
        description="Short invariant name (e.g., 'NoDoubleBooking', 'MaxCapacityEnforced')"
    )
    description: str = Field(
        ...,
        description="The business rule in plain language"
    )
    enforcement: str = Field(
        ...,
        description="How this invariant is enforced (e.g., 'Checked on BookRoom command')"
    )


class Aggregate(BaseModel):
    """
    A complete aggregate design with root, entities, VOs, and behavior.
    
    Designed for:
    - Mermaid class diagram generation
    - Code generation templates
    - Cross-phase validation
    """

    name: str = Field(
        ...,
        description="Aggregate name in PascalCase (e.g., 'Booking', 'Room')"
    )
    description: str = Field(
        ...,
        description="Purpose of this aggregate"
    )
    bounded_context: str = Field(
        ...,
        description="The bounded context this aggregate belongs to"
    )

    # Root entity
    root_entity: str = Field(
        ...,
        description="Name of the aggregate root entity (often same as aggregate name)"
    )
    identity: Attribute = Field(
        ...,
        description="The identity attribute of the aggregate root"
    )
    root_attributes: list[Attribute] = Field(
        default_factory=list,
        description="Attributes of the aggregate root (excluding identity)"
    )

    # Contained elements
    entities: list[Entity] = Field(
        default_factory=list,
        description="Child entities within this aggregate"
    )
    value_objects: list[ValueObject] = Field(
        default_factory=list,
        description="Value objects defined in this aggregate"
    )
    enums: list[EnumDefinition] = Field(
        default_factory=list,
        description="Enumerations used by this aggregate"
    )

    # Behavior
    invariants: list[Invariant] = Field(
        ...,
        description="Business rules this aggregate protects"
    )
    commands: list[AggregateCommand] = Field(
        ...,
        description="Commands this aggregate handles"
    )
    domain_events: list[str] = Field(
        ...,
        description="Domain events this aggregate can publish"
    )

    # Design evaluation
    consistency_boundary: str = Field(
        ...,
        description="What must be consistent within this aggregate"
    )
    size_evaluation: SizeEvaluation = Field(
        ...,
        description="Assessment of aggregate size"
    )
    size_notes: Optional[str] = Field(
        None,
        description="Notes on size - splitting or merging recommendations"
    )

    # References to other aggregates (via IDs, not direct references)
    references_aggregates: list[str] = Field(
        default_factory=list,
        description="Other aggregates referenced by ID (e.g., 'Room' referenced via roomId)"
    )


class CrossAggregateInteraction(BaseModel):
    """
    An interaction between aggregates via events/eventual consistency.
    
    Used for documenting and visualizing aggregate boundaries.
    """

    source_aggregate: str = Field(
        ...,
        description="Aggregate that publishes the event"
    )
    event: str = Field(
        ...,
        description="Domain event name"
    )
    target_aggregate: str = Field(
        ...,
        description="Aggregate that reacts to the event"
    )
    reaction: str = Field(
        ...,
        description="What the target aggregate does in response"
    )
    consistency: Literal["eventual", "saga"] = Field(
        default="eventual",
        description="Consistency model for this interaction"
    )


class AggregatesArtifact(BaseModel):
    """
    Complete Aggregates artifact for Phase 4 of the DDD workflow.
    
    Designed for:
    - Machine-readable JSON storage
    - Mermaid class diagram generation (per aggregate)
    - Code scaffolding templates
    - Cross-phase validation with events and contexts
    """

    # All aggregates
    aggregates: list[Aggregate] = Field(
        ...,
        description="All designed aggregates"
    )

    # Shared value objects (used across multiple aggregates)
    shared_value_objects: list[ValueObject] = Field(
        default_factory=list,
        description="Value objects reused across aggregates"
    )

    # Cross-aggregate interactions
    cross_aggregate_interactions: list[CrossAggregateInteraction] = Field(
        default_factory=list,
        description="Interactions between aggregates via events"
    )

    # Design concerns
    design_concerns: list[str] = Field(
        default_factory=list,
        description="Aggregates that may need restructuring"
    )
    missing_invariants: list[str] = Field(
        default_factory=list,
        description="Business rules that may not be covered"
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
                    "aggregates": [
                        {
                            "name": "Booking",
                            "description": "Manages room reservations",
                            "bounded_context": "Reservation",
                            "root_entity": "Booking",
                            "identity": {
                                "name": "bookingId",
                                "type": "BookingId",
                                "is_required": True,
                                "description": "Unique booking identifier"
                            },
                            "root_attributes": [
                                {"name": "roomId", "type": "RoomId", "is_required": True, "description": "Referenced room"},
                                {"name": "guestId", "type": "GuestId", "is_required": True, "description": "Who made the booking"},
                                {"name": "status", "type": "BookingStatus", "is_required": True, "description": "Current booking state"}
                            ],
                            "entities": [],
                            "value_objects": [
                                {
                                    "name": "TimeSlot",
                                    "description": "A time range for the booking",
                                    "attributes": [
                                        {"name": "startTime", "type": "DateTime", "is_required": True, "description": None},
                                        {"name": "endTime", "type": "DateTime", "is_required": True, "description": None}
                                    ],
                                    "validation_rules": ["endTime must be after startTime", "Duration must be at least 30 minutes"],
                                    "is_reusable": True
                                }
                            ],
                            "enums": [
                                {
                                    "name": "BookingStatus",
                                    "description": "Possible states of a booking",
                                    "values": ["PENDING", "CONFIRMED", "CANCELLED", "COMPLETED"]
                                }
                            ],
                            "invariants": [
                                {
                                    "name": "NoDoubleBooking",
                                    "description": "A room cannot be booked for overlapping time slots",
                                    "enforcement": "Checked via Room aggregate before confirming"
                                },
                                {
                                    "name": "ValidTimeSlot",
                                    "description": "Booking must have a valid future time slot",
                                    "enforcement": "Validated on creation and modification"
                                }
                            ],
                            "commands": [
                                {
                                    "name": "createBooking",
                                    "description": "Create a new booking request",
                                    "parameters": ["roomId: RoomId", "guestId: GuestId", "timeSlot: TimeSlot"],
                                    "preconditions": ["Guest is authenticated", "TimeSlot is in the future"],
                                    "postconditions": ["Booking exists in PENDING status"],
                                    "events_raised": ["BookingCreated"],
                                    "exceptions": ["InvalidTimeSlot"]
                                },
                                {
                                    "name": "confirmBooking",
                                    "description": "Confirm a pending booking",
                                    "parameters": [],
                                    "preconditions": ["Booking is in PENDING status", "Room is available"],
                                    "postconditions": ["Booking is in CONFIRMED status"],
                                    "events_raised": ["BookingConfirmed"],
                                    "exceptions": ["BookingNotPending", "RoomNotAvailable"]
                                },
                                {
                                    "name": "cancelBooking",
                                    "description": "Cancel an existing booking",
                                    "parameters": ["reason: string"],
                                    "preconditions": ["Booking is not already cancelled"],
                                    "postconditions": ["Booking is in CANCELLED status"],
                                    "events_raised": ["BookingCancelled"],
                                    "exceptions": ["BookingAlreadyCancelled"]
                                }
                            ],
                            "domain_events": ["BookingCreated", "BookingConfirmed", "BookingCancelled", "BookingCompleted"],
                            "consistency_boundary": "Single booking with its time slot and status",
                            "size_evaluation": "appropriate",
                            "size_notes": None,
                            "references_aggregates": ["Room", "Guest"]
                        }
                    ],
                    "shared_value_objects": [
                        {
                            "name": "TimeSlot",
                            "description": "A time range used across booking and availability",
                            "attributes": [
                                {"name": "startTime", "type": "DateTime", "is_required": True, "description": None},
                                {"name": "endTime", "type": "DateTime", "is_required": True, "description": None}
                            ],
                            "validation_rules": ["endTime must be after startTime"],
                            "is_reusable": True
                        }
                    ],
                    "cross_aggregate_interactions": [
                        {
                            "source_aggregate": "Booking",
                            "event": "BookingConfirmed",
                            "target_aggregate": "Room",
                            "reaction": "Mark time slot as occupied",
                            "consistency": "eventual"
                        }
                    ],
                    "design_concerns": [],
                    "missing_invariants": ["Cancellation policy time window not yet modeled"],
                    "schema_version": "1.0"
                }
            ]
        }
    }
