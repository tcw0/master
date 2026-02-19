"""
Validation rules for Phase 1: Glossary (Ubiquitous Language).

Intra-phase checks that verify the glossary artifact is internally consistent.
"""

from collections import Counter

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="glossary.no_duplicate_terms",
    phase="01_glossary",
    description="No two glossary terms should share the same name (case-insensitive)",
    severity_on_fail=ValidationSeverity.FAILURE,
)
def no_duplicate_terms(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that every term in the glossary has a unique name.

    Comparison is case-insensitive to catch near-duplicates like
    'Room' vs 'room'.
    """
    glossary = artifacts.get("glossary")
    if glossary is None:
        return []

    results: list[ValidationResult] = []
    term_names = [t.term.strip().lower() for t in glossary.terms]
    counts = Counter(term_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="glossary.no_duplicate_terms",
                    severity=ValidationSeverity.FAILURE,
                    phase="01_glossary",
                    message=f"Duplicate glossary term '{name}' appears {count} times",
                    source_element=name,
                    suggestion="Remove or merge duplicate term definitions",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="glossary.no_duplicate_terms",
                severity=ValidationSeverity.PASS,
                phase="01_glossary",
                message=f"All {len(term_names)} glossary terms are unique",
            )
        )

    return results
