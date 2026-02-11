"""
Pydantic models for Event Storming artifact (Phase 2).

Schema design principles:
- Capture events, commands, actors, policies as discrete records
- Enable flow reconstruction via cross-references
- Support Mermaid flowchart generation via explicit relationships
- Flag ambiguities for human review
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# Categories for visualization grouping
EventCategory = Literal["domain_event", "integration_event", "system_event"]
CommandCategory = Literal["user_command", "system_command", "policy_command"]
ActorType = Literal["user", "external_system", "time", "policy"]


class Actor(BaseModel):
    """An actor or role that initiates commands in the system."""

    name: str = Field(
        ...,
        description="Actor name (e.g., 'Guest', 'Admin', 'PaymentGateway', 'Scheduler')"
    )
    type: ActorType = Field(
        ...,
        description="Type of actor: user, external_system, time (scheduler), or policy"
    )
    description: str = Field(
        ...,
        description="Role description and responsibilities"
    )


class DomainEvent(BaseModel):
    """A domain event representing something significant that happened."""

    name: str = Field(
        ...,
        description="Event name in PastTense (e.g., 'RoomBooked', 'PaymentReceived')"
    )
    description: str = Field(
        ...,
        description="What this event represents in business terms"
    )
    category: EventCategory = Field(
        default="domain_event",
        description="Event category for grouping"
    )
    aggregate: str = Field(
        ...,
        description="The aggregate that emits this event"
    )
    triggered_by: str = Field(
        ...,
        description="Command name that causes this event"
    )
    payload: list[str] = Field(
        default_factory=list,
        description="Key data attributes carried by this event"
    )
    triggers_policies: list[str] = Field(
        default_factory=list,
        description="Policy names that react to this event"
    )


class Command(BaseModel):
    """A command representing an intention to change system state."""

    name: str = Field(
        ...,
        description="Command name in imperative form (e.g., 'BookRoom', 'CancelBooking')"
    )
    description: str = Field(
        ...,
        description="What this command intends to accomplish"
    )
    category: CommandCategory = Field(
        default="user_command",
        description="Command category for visualization"
    )
    actor: str = Field(
        ...,
        description="Actor name who initiates this command"
    )
    target_aggregate: str = Field(
        ...,
        description="Aggregate name that handles this command"
    )
    parameters: list[str] = Field(
        default_factory=list,
        description="Input parameters required (e.g., 'roomId', 'startTime')"
    )
    preconditions: list[str] = Field(
        default_factory=list,
        description="Conditions that must be true before execution"
    )
    produces_events: list[str] = Field(
        default_factory=list,
        description="Event names produced on successful execution"
    )


class Policy(BaseModel):
    """A policy/rule that reacts to events and may trigger commands."""

    name: str = Field(
        ...,
        description="Policy name (e.g., 'SendConfirmationOnBooking', 'EnforceMaxCapacity')"
    )
    description: str = Field(
        ...,
        description="What this policy does and the business rule it enforces"
    )
    triggered_by_event: str = Field(
        ...,
        description="Event name that activates this policy"
    )
    condition: Optional[str] = Field(
        None,
        description="Condition under which the policy fires (if not always)"
    )
    resulting_commands: list[str] = Field(
        default_factory=list,
        description="Command names triggered by this policy"
    )
    is_automated: bool = Field(
        default=True,
        description="Whether this policy executes automatically or requires human decision"
    )


class EventFlow(BaseModel):
    """
    A complete flow representing one user story or process path.
    
    Used primarily for visualization - captures a sequence for Mermaid generation.
    """

    name: str = Field(
        ...,
        description="Flow name describing the scenario (e.g., 'Happy Path Booking')"
    )
    description: str = Field(
        ...,
        description="What this flow represents"
    )
    steps: list[str] = Field(
        ...,
        description="Ordered list where EACH ELEMENT is a SEPARATE string. Example: ['Guest', 'BookRoom', 'Booking', 'RoomBooked', 'SendConfirmation']. Do NOT concatenate with arrows like 'A -> B -> C'."
    )
    is_happy_path: bool = Field(
        default=True,
        description="Whether this is the main success scenario"
    )


class HotSpot(BaseModel):
    """
    An area of uncertainty or contention identified during event storming.
    
    Hot spots are marked with 'pink stickies' in traditional event storming.
    """

    description: str = Field(
        ...,
        description="What is unclear or contentious"
    )
    related_elements: list[str] = Field(
        default_factory=list,
        description="Names of events, commands, or aggregates involved"
    )
    questions: list[str] = Field(
        default_factory=list,
        description="Specific questions to resolve this hot spot"
    )


class EventStormingArtifact(BaseModel):
    """
    Complete Event Storming artifact for Phase 2 of the DDD workflow.
    
    Designed for:
    - Machine-readable JSON storage
    - Mermaid flowchart generation (via explicit relationships)
    - Cross-phase validation (events -> aggregates -> bounded contexts)
    """

    # Core elements (nodes in the visualization)
    actors: list[Actor] = Field(
        ...,
        description="All identified actors/roles in the system"
    )
    commands: list[Command] = Field(
        ...,
        description="All identified commands"
    )
    domain_events: list[DomainEvent] = Field(
        ...,
        description="All identified domain events"
    )
    policies: list[Policy] = Field(
        default_factory=list,
        description="All identified policies/reactions"
    )

    # Aggregates mentioned (will be fully designed in Phase 4)
    aggregates_mentioned: list[str] = Field(
        default_factory=list,
        description="Aggregate names identified during event storming"
    )

    # Flows for visualization
    event_flows: list[EventFlow] = Field(
        default_factory=list,
        description="Key flows showing complete scenarios"
    )

    # Temporal and process insights
    temporal_boundaries: list[str] = Field(
        default_factory=list,
        description="Identified time-based boundaries (e.g., 'End of Day', 'Booking Window')"
    )
    parallel_processes: list[str] = Field(
        default_factory=list,
        description="Processes that can happen concurrently"
    )

    # Uncertainties
    hot_spots: list[HotSpot] = Field(
        default_factory=list,
        description="Areas requiring clarification or domain expert input"
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
                    "actors": [
                        {
                            "name": "Guest",
                            "type": "user",
                            "description": "A user who wants to book a room"
                        }
                    ],
                    "commands": [
                        {
                            "name": "BookRoom",
                            "description": "Reserve a room for a specific time slot",
                            "category": "user_command",
                            "actor": "Guest",
                            "target_aggregate": "Booking",
                            "parameters": ["roomId", "timeSlot", "guestId"],
                            "preconditions": ["Room is available", "Guest is authenticated"],
                            "produces_events": ["RoomBooked"]
                        }
                    ],
                    "domain_events": [
                        {
                            "name": "RoomBooked",
                            "description": "A room has been successfully reserved",
                            "category": "domain_event",
                            "aggregate": "Booking",
                            "triggered_by": "BookRoom",
                            "payload": ["bookingId", "roomId", "timeSlot", "guestId"],
                            "triggers_policies": ["SendBookingConfirmation"]
                        }
                    ],
                    "policies": [
                        {
                            "name": "SendBookingConfirmation",
                            "description": "Send confirmation email when a booking is made",
                            "triggered_by_event": "RoomBooked",
                            "condition": None,
                            "resulting_commands": ["SendEmail"],
                            "is_automated": True
                        }
                    ],
                    "aggregates_mentioned": ["Booking", "Room", "Guest"],
                    "event_flows": [
                        {
                            "name": "Room Booking Happy Path",
                            "description": "Guest successfully books an available room",
                            "steps": ["Guest", "BookRoom", "Booking", "RoomBooked", "SendBookingConfirmation", "SendEmail"],
                            "is_happy_path": True
                        }
                    ],
                    "temporal_boundaries": ["Check-in time", "Cancellation deadline"],
                    "parallel_processes": ["Payment processing", "Notification sending"],
                    "hot_spots": [
                        {
                            "description": "What happens if payment fails after booking?",
                            "related_elements": ["RoomBooked", "PaymentFailed"],
                            "questions": ["Should we reserve the room before payment?", "How long to hold unpaid bookings?"]
                        }
                    ],
                    "schema_version": "1.0"
                }
            ]
        }
    }
