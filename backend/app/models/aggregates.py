"""
Phase 4 — Aggregate Design.

Structured output model for designing aggregates with consistency boundaries,
invariants, commands, and domain events per bounded context.

Designed for OpenAI-compatible structured output (all fields required,
Literal enums, ≤3 nesting levels).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AggregateElement(BaseModel):
    """An entity or value object within an aggregate."""

    name: str = Field(
        description="Name of the entity or value object",
    )
    element_type: Literal["entity", "value_object"] = Field(
        description=(
            "Whether this is an entity (has identity) "
            "or a value object (defined by attributes)"
        ),
    )
    description: str = Field(
        description="Brief description of this element's role within the aggregate",
    )
    properties: list[str] = Field(
        description="Key properties/attributes of this element",
    )


class Invariant(BaseModel):
    """A business rule that an aggregate must protect."""

    name: str = Field(
        description="Short name for this business rule",
    )
    description: str = Field(
        description=(
            "The business rule this aggregate must protect, "
            "stated in domain language"
        ),
    )


class AggregateCommand(BaseModel):
    """A command handled by an aggregate."""

    name: str = Field(
        description="Name of the command (e.g., 'PlaceOrder')",
    )
    description: str = Field(
        description="What this command does in business terms",
    )
    parameters: list[str] = Field(
        description="Key input parameters for this command",
    )
    emitted_events: list[str] = Field(
        description="Domain event names emitted when this command succeeds",
    )
    rules_applied: list[str] = Field(
        description="Names of invariants checked during this command",
    )


class Aggregate(BaseModel):
    """An aggregate with its root, elements, invariants, and commands."""

    name: str = Field(
        description="Name of the aggregate",
    )
    bounded_context: str = Field(
        description="Name of the bounded context this aggregate belongs to",
    )
    root_entity: str = Field(
        description="Name of the aggregate root entity",
    )
    elements: list[AggregateElement] = Field(
        description="Entities and value objects within this aggregate",
    )
    invariants: list[Invariant] = Field(
        description="Business rules this aggregate must enforce",
    )
    commands: list[AggregateCommand] = Field(
        description="Commands this aggregate handles",
    )
    domain_events: list[str] = Field(
        description="All domain events this aggregate can emit",
    )
    size_evaluation: Literal["small", "moderate", "large"] = Field(
        description=(
            "Assessment of aggregate size — 'large' flags "
            "potential need to split"
        ),
    )
    size_rationale: str = Field(
        description=(
            "Explanation of the size evaluation and any "
            "recommendations"
        ),
    )


class AggregatesArtifact(BaseModel):
    """Phase 4 artifact — aggregate designs across all bounded contexts."""

    aggregates: list[Aggregate] = Field(
        description="All aggregates designed across all bounded contexts",
    )
    design_decisions: list[str] = Field(
        description=(
            "Key design decisions and rationale for the "
            "aggregate partitioning"
        ),
    )
