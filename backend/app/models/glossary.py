"""
Phase 1 — Ubiquitous Language (Glossary).

Structured output model for extracting domain terms from requirements.
Designed for OpenAI-compatible structured output (all fields required,
Literal enums, ≤3 nesting levels).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GlossaryTerm(BaseModel):
    """A single domain term in the ubiquitous language."""

    name: str = Field(
        description="The domain term exactly as used in the requirements",
    )
    definition: str = Field(
        description=(
            "Clear, business-focused definition (not technical). "
            "Written as a domain expert would explain it."
        ),
    )
    category: Literal[
        "entity",
        "value_object",
        "command",
        "event",
        "rule_policy",
        "role",
        "state",
        "other",
    ] = Field(
        description="DDD classification of this term",
    )
    business_context: str = Field(
        description="When and where this term is used in the business domain",
    )
    related_terms: list[str] = Field(
        description="Other domain terms that are related to this term",
    )
    is_ambiguous: bool = Field(
        description=(
            "Whether this term has multiple possible meanings "
            "or needs clarification"
        ),
    )
    clarification_needed: str | None = Field(
        default=None,
        description=(
            "Specific question or ambiguity about this term, "
            "null if none"
        ),
    )
    bounded_context_hint: str | None = Field(
        default=None,
        description=(
            "Suggested bounded context this term might belong to, "
            "null if unclear"
        ),
    )


class BoundedContextHint(BaseModel):
    """Early indicator of a potential bounded context based on term groupings."""

    context_name: str = Field(
        description="Suggested name for this potential bounded context",
    )
    term_names: list[str] = Field(
        description="Names of glossary terms that belong to this context",
    )
    reasoning: str = Field(
        description="Why these terms are grouped together",
    )


class GlossaryArtifact(BaseModel):
    """Phase 1 artifact — the ubiquitous language glossary."""

    terms: list[GlossaryTerm] = Field(
        description="All domain terms extracted from the requirements",
    )
    bounded_context_hints: list[BoundedContextHint] = Field(
        description=(
            "Early indicators of potential bounded contexts "
            "based on term groupings"
        ),
    )
