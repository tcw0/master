"""
Pydantic models for Glossary (Ubiquitous Language) artifact.

Schema design principles:
- Business-focused definitions (not technical jargon)
- Capture relationships between terms
- Flag ambiguities for human review
- Support bounded context indicators
"""

from typing import Optional
from pydantic import BaseModel, Field


class GlossaryTerm(BaseModel):
    """A single domain term in the ubiquitous language glossary."""

    term: str = Field(
        ...,
        description="The domain term or concept name (e.g., 'Order', 'Customer', 'Booking')"
    )
    definition: str = Field(
        ...,
        description="Clear business-focused definition of the term, as a domain expert would explain it"
    )
    business_context: str = Field(
        ...,
        description="When and where this term is used in the business domain"
    )
    related_terms: list[str] = Field(
        default_factory=list,
        description="Other domain terms that are related to this term"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category: 'entity', 'value_object', 'command', 'event', 'policy', 'role', or 'state'"
    )
    clarification_needed: Optional[str] = Field(
        default=None,
        description="Any ambiguities or questions that need domain expert clarification"
    )


class BoundedContextIndicator(BaseModel):
    """Indicator of a potential bounded context based on term clustering."""

    context_name: str = Field(
        ...,
        description="Suggested name for the bounded context (e.g., 'Sales', 'Inventory')"
    )
    related_terms: list[str] = Field(
        ...,
        description="Terms from the glossary that belong to this context"
    )
    rationale: str = Field(
        ...,
        description="Why these terms seem to form a cohesive bounded context"
    )


class GlossaryArtifact(BaseModel):
    """
    Complete Glossary artifact for the Ubiquitous Language phase.

    This is the structured output schema for Phase 1 of the DDD workflow.
    """

    terms: list[GlossaryTerm] = Field(
        ...,
        description="List of all identified domain terms with their definitions"
    )
    bounded_context_indicators: list[BoundedContextIndicator] = Field(
        default_factory=list,
        description="Potential bounded contexts identified from term clustering"
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Questions to ask domain experts about ambiguous terms or concepts"
    )

    # Artifact metadata (populated by the system, not the LLM)
    schema_version: str = Field(
        default="1.0",
        description="Version of this schema for future compatibility"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "terms": [
                        {
                            "term": "Room",
                            "definition": "A physical space within a building that can be reserved for meetings or events",
                            "business_context": "Central to the booking and reservation process",
                            "related_terms": ["Booking", "Building", "Capacity"],
                            "category": "entity",
                            "clarification_needed": "Are virtual rooms also considered?"
                        },
                        {
                            "term": "Booking",
                            "definition": "A reservation of a room for a specific time period by a user",
                            "business_context": "The core transaction in the room reservation system",
                            "related_terms": ["Room", "User", "Time Slot"],
                            "category": "entity",
                            "clarification_needed": None
                        }
                    ],
                    "bounded_context_indicators": [
                        {
                            "context_name": "Reservation Management",
                            "related_terms": ["Booking", "Room", "Time Slot", "Cancellation"],
                            "rationale": "These terms all relate to the core booking lifecycle"
                        }
                    ],
                    "clarification_questions": [
                        "Is there a difference between a 'Booking' and a 'Reservation'?",
                        "Can a room belong to multiple buildings?"
                    ],
                    "schema_version": "1.0"
                }
            ]
        }
    }
