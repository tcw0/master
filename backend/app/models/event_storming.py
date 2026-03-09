"""
Phase 2 — Event Storming.

Structured output model for identifying domain events, commands, actors,
policies, and business process flows.

Uses a dual structure:
- Normalized lists (commands, events, policies) for cross-phase validation
- Flow-oriented steps for direct 1:1 mapping to sticky-note visualization

Designed for OpenAI-compatible structured output (all fields required,
Literal enums, ≤3 nesting levels).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Command(BaseModel):
    """A command that can be issued by an actor to an aggregate."""

    name: str = Field(
        description="Command name in imperative form (e.g., 'PlaceOrder')",
    )
    description: str = Field(
        description="What this command does in business terms",
    )
    actor: str = Field(
        description="The actor or role who initiates this command",
    )
    target_aggregate: str = Field(
        description="The aggregate that handles this command",
    )


class DomainEvent(BaseModel):
    """A domain event — something that happened in the domain (past tense)."""

    name: str = Field(
        description="Domain event name in past tense (e.g., 'OrderPlaced')",
    )
    description: str = Field(
        description="What happened in business terms",
    )
    triggered_by_command: str = Field(
        description="Name of the command that causes this event",
    )
    aggregate: str = Field(
        description="The aggregate that emits this event",
    )


class Policy(BaseModel):
    """A business policy or reaction rule triggered by a domain event."""

    name: str = Field(
        description="Name of the business policy or reaction rule",
    )
    description: str = Field(
        description="What this policy does in business terms",
    )
    triggered_by_event: str = Field(
        description="The domain event that activates this policy",
    )
    resulting_command: str | None = Field(
        default=None,
        description="The command initiated by this policy, null if none",
    )


class FlowStep(BaseModel):
    """One sticky-note group in the event flow visualization.

    Maps 1:1 to: Actor → Command → Aggregate → Event [→ Policy → Next Command]
    """

    actor: str = Field(
        description="The actor or role performing the action",
    )
    command: str = Field(
        description="The command being executed",
    )
    aggregate: str = Field(
        description="The aggregate handling the command",
    )
    event: str = Field(
        description="The domain event emitted",
    )
    policy: str | None = Field(
        default=None,
        description="Policy triggered by this event, null if none",
    )
    next_command: str | None = Field(
        default=None,
        description=(
            "Command initiated by the policy, null if flow "
            "ends or no policy"
        ),
    )


class EventFlow(BaseModel):
    """A business process represented as an ordered sequence of flow steps."""

    name: str = Field(
        description=(
            "Name of this business process or flow "
            "(e.g., 'Order Fulfillment')"
        ),
    )
    description: str = Field(
        description="Brief description of this end-to-end process",
    )
    steps: list[FlowStep] = Field(
        description=(
            "Ordered sequence of flow steps, each representing "
            "one sticky-note group in the event storming board"
        ),
    )


class EventStormingArtifact(BaseModel):
    """Phase 2 artifact — event storming results with dual structure."""

    # --- Normalized lists (for validation & cross-phase references) ---
    commands: list[Command] = Field(
        description="All unique commands identified from the requirements",
    )
    domain_events: list[DomainEvent] = Field(
        description="All unique domain events identified from the requirements",
    )
    policies: list[Policy] = Field(
        description="All business policies and reactive rules",
    )
    # --- Flow-oriented structure (for visualization) ---
    flows: list[EventFlow] = Field(
        description=(
            "Business processes as ordered flow steps, "
            "each step maps to a sticky-note group"
        ),
    )
    ambiguities: list[str] = Field(
        description=(
            "Areas where the event flow is unclear or has "
            "multiple interpretations"
        ),
    )
