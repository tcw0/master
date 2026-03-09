"""
Phase 5 — Technical Architecture Mapping.

Structured output model for mapping the domain model to a hexagonal
architecture with domain, application, infrastructure, and presentation layers.

Designed for OpenAI-compatible structured output (all fields required,
Literal enums, ≤3 nesting levels).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DomainLayerElement(BaseModel):
    """An element in the innermost domain layer."""

    name: str = Field(
        description="Name of the domain layer element",
    )
    element_type: Literal[
        "entity",
        "value_object",
        "domain_service",
        "repository_interface",
        "domain_event",
    ] = Field(
        description="Type of domain layer element",
    )
    description: str = Field(
        description="Purpose and responsibility of this element",
    )


class ApplicationLayerElement(BaseModel):
    """An element in the application layer."""

    name: str = Field(
        description="Name of the application layer element",
    )
    element_type: Literal[
        "application_service",
        "dto",
        "command",
        "query",
        "command_handler",
        "query_handler",
    ] = Field(
        description="Type of application layer element",
    )
    description: str = Field(
        description="Purpose and responsibility of this element",
    )


class InfrastructureLayerElement(BaseModel):
    """An element in the infrastructure layer."""

    name: str = Field(
        description="Name of the infrastructure layer element",
    )
    element_type: Literal[
        "repository_implementation",
        "external_adapter",
        "event_publisher",
        "persistence_config",
        "messaging",
    ] = Field(
        description="Type of infrastructure layer element",
    )
    description: str = Field(
        description="Purpose and responsibility of this element",
    )


class PresentationLayerElement(BaseModel):
    """An element in the outermost presentation layer."""

    name: str = Field(
        description="Name of the presentation layer element",
    )
    element_type: Literal[
        "rest_controller",
        "graphql_resolver",
        "api_dto",
        "middleware",
    ] = Field(
        description="Type of presentation layer element",
    )
    description: str = Field(
        description="Purpose and responsibility of this element",
    )


class HexagonalArchitecture(BaseModel):
    """Hexagonal architecture mapping for a single bounded context."""

    bounded_context: str = Field(
        description="Name of the bounded context this architecture maps to",
    )
    domain_layer: list[DomainLayerElement] = Field(
        description="Elements in the domain layer (innermost)",
    )
    application_layer: list[ApplicationLayerElement] = Field(
        description="Elements in the application layer",
    )
    infrastructure_layer: list[InfrastructureLayerElement] = Field(
        description="Elements in the infrastructure layer",
    )
    presentation_layer: list[PresentationLayerElement] = Field(
        description="Elements in the presentation layer (outermost)",
    )


class AntiCorruptionLayer(BaseModel):
    """Translation layer protecting a bounded context from a foreign model."""

    owning_context: str = Field(
        description="The bounded context that owns this ACL",
    )
    foreign_context: str = Field(
        description="The external context being translated from",
    )
    translation_description: str = Field(
        description="What the ACL translates and how",
    )
    translated_elements: list[str] = Field(
        description="Domain elements that are translated through this ACL",
    )


class PublishedInterface(BaseModel):
    """An interface published by a bounded context for external consumption."""

    bounded_context: str = Field(
        description="The bounded context publishing this interface",
    )
    interface_type: Literal[
        "rest_api",
        "graphql_api",
        "domain_events",
        "shared_kernel",
    ] = Field(
        description="Type of published interface",
    )
    description: str = Field(
        description="What this interface exposes",
    )
    exposed_operations: list[str] = Field(
        description="List of operations or events exposed",
    )


class TechnicalPattern(BaseModel):
    """A technical pattern applied within a bounded context."""

    pattern_name: str = Field(
        description=(
            "Name of the technical pattern "
            "(e.g., 'Repository', 'Specification', 'Domain Events')"
        ),
    )
    applied_in_context: str = Field(
        description="Bounded context where this pattern is applied",
    )
    justification: str = Field(
        description="How this pattern supports the domain model",
    )


class ArchitectureArtifact(BaseModel):
    """Phase 5 artifact — technical architecture mapping."""

    architectures: list[HexagonalArchitecture] = Field(
        description="Hexagonal architecture mapping per bounded context",
    )
    anti_corruption_layers: list[AntiCorruptionLayer] = Field(
        description="All anti-corruption layers between contexts",
    )
    published_interfaces: list[PublishedInterface] = Field(
        description="Published APIs and events per context",
    )
    technical_patterns: list[TechnicalPattern] = Field(
        description="Technical patterns applied and their justification",
    )
