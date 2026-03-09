"""
Phase 3 — Bounded Context Identification.

Structured output model for identifying bounded contexts, their relationships
(context map), and terms with different meanings across contexts.

Designed for OpenAI-compatible structured output (all fields required,
Literal enums, ≤3 nesting levels).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BoundedContext(BaseModel):
    """A bounded context with its purpose, classification, and contents."""

    name: str = Field(
        description="Name of the bounded context",
    )
    purpose: str = Field(
        description="Core purpose and responsibility of this context",
    )
    domain_type: Literal["core", "supporting", "generic"] = Field(
        description="Strategic classification of this context",
    )
    key_aggregates: list[str] = Field(
        description="Names of the main aggregates within this context",
    )
    ubiquitous_language_terms: list[str] = Field(
        description="Glossary terms that are specific to this context",
    )


class ContextRelationship(BaseModel):
    """A relationship between two bounded contexts in the context map."""

    source_context: str = Field(
        description="Name of the upstream / source bounded context",
    )
    target_context: str = Field(
        description="Name of the downstream / target bounded context",
    )
    relationship_type: Literal[
        "upstream_downstream",
        "shared_kernel",
        "customer_supplier",
        "conformist",
        "anti_corruption_layer",
        "published_language",
        "open_host_service",
        "partnership",
        "separate_ways",
    ] = Field(
        description="Type of relationship between the two contexts",
    )
    description: str = Field(
        description="Explanation of how these contexts interact",
    )


class ContextSpecificMeaning(BaseModel):
    """How a term is interpreted within a specific bounded context."""

    context_name: str = Field(
        description="The bounded context where this meaning applies",
    )
    meaning: str = Field(
        description="What the term means in this specific context",
    )


class TermOverlap(BaseModel):
    """A term that has different meanings across bounded contexts."""

    term_name: str = Field(
        description="The term that has different meanings across contexts",
    )
    contexts_and_meanings: list[ContextSpecificMeaning] = Field(
        description="How this term is interpreted in each context",
    )


class BoundedContextsArtifact(BaseModel):
    """Phase 3 artifact — bounded contexts and context map."""

    bounded_contexts: list[BoundedContext] = Field(
        description="All identified bounded contexts",
    )
    context_relationships: list[ContextRelationship] = Field(
        description=(
            "All relationships between bounded contexts "
            "(the Context Map)"
        ),
    )
    term_overlaps: list[TermOverlap] = Field(
        description="Terms that have different meanings across contexts",
    )
