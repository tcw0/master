"""
Cross-phase validation rules spanning multiple pipeline phases.

These rules verify consistency and traceability across the full artifact chain.
"""

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


def _normalize(name: str) -> str:
    """Normalize a name for fuzzy matching: lowercase, strip, collapse whitespace."""
    return " ".join(name.strip().lower().split())


@validation_rule(
    rule_id="cross.terminology_consistency",
    phase="04_aggregates",
    description="Aggregate names should substantially overlap with glossary terms",
    severity_on_fail=ValidationSeverity.WARNING,
)
def terminology_consistency(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that aggregate names from Phase 4 appear in the Phase 1 glossary.

    LLMs may invent new names in later phases that diverge from the
    established ubiquitous language. This rule surfaces those cases.
    """
    glossary = artifacts.get("glossary")
    agg_artifact = artifacts.get("aggregates")

    if glossary is None or agg_artifact is None:
        return []

    results: list[ValidationResult] = []

    # Build normalized set of glossary term names
    glossary_terms = {_normalize(t.name) for t in glossary.terms}

    # Check each aggregate name against glossary
    unmatched: list[str] = []
    for agg in agg_artifact.aggregates:
        normalized = _normalize(agg.name)
        if normalized not in glossary_terms:
            unmatched.append(agg.name)

    if unmatched:
        for name in unmatched:
            results.append(
                ValidationResult(
                    rule_id="cross.terminology_consistency",
                    severity=ValidationSeverity.WARNING,
                    phase="04_aggregates",
                    message=(
                        f"Aggregate '{name}' does not match any glossary term — "
                        f"possible ubiquitous language drift"
                    ),
                    source_element=name,
                    suggestion=(
                        "Add this term to the glossary or rename the aggregate "
                        "to match an existing glossary term"
                    ),
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="cross.terminology_consistency",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message="All aggregate names match glossary terms",
            )
        )

    return results
