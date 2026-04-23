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
    severity_on_fail=ValidationSeverity.WARNING,
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
    term_names = [t.name.strip().lower() for t in glossary.terms]
    counts = Counter(term_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="glossary.no_duplicate_terms",
                    severity=ValidationSeverity.WARNING,
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


@validation_rule(
    rule_id="glossary.valid_categories",
    phase="01_glossary",
    description="Terms must use accepted categories",
    severity_on_fail=ValidationSeverity.WARNING,
)
def valid_categories(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    glossary = artifacts.get("glossary")
    if glossary is None:
        return []

    valid_cats = {"entity", "value_object", "event", "command", "role", "rule_policy", "other"}
    results: list[ValidationResult] = []
    invalid_terms = []

    for term in glossary.terms:
        if term.category not in valid_cats:
            invalid_terms.append((term.name, term.category))

    if invalid_terms:
        for name, cat in invalid_terms:
            results.append(
                ValidationResult(
                    rule_id="glossary.valid_categories",
                    severity=ValidationSeverity.WARNING,
                    phase="01_glossary",
                    message=f"Term '{name}' uses invalid category '{cat}'",
                    source_element=name,
                    suggestion=f"Change category to one of: {', '.join(valid_cats)}",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="glossary.valid_categories",
                severity=ValidationSeverity.PASS,
                phase="01_glossary",
                message="All terms use valid categories",
            )
        )
    return results


@validation_rule(
    rule_id="glossary.related_terms_exist",
    phase="01_glossary",
    description="Related terms should exist in the glossary",
    severity_on_fail=ValidationSeverity.WARNING,
)
def related_terms_exist(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    glossary = artifacts.get("glossary")
    if glossary is None:
        return []

    results: list[ValidationResult] = []
    term_names = {t.name.strip().lower() for t in glossary.terms}

    missing_references = []
    for term in glossary.terms:
        for related in term.related_terms:
            if related.strip().lower() not in term_names:
                missing_references.append((term.name, related))

    if missing_references:
        for name, related in missing_references:
            results.append(
                ValidationResult(
                    rule_id="glossary.related_terms_exist",
                    severity=ValidationSeverity.WARNING,
                    phase="01_glossary",
                    message=f"Term '{name}' references non-existent related term '{related}'",
                    source_element=name,
                    suggestion="Add the missing term to the glossary or correct the reference",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="glossary.related_terms_exist",
                severity=ValidationSeverity.PASS,
                phase="01_glossary",
                message="All related terms exist in the glossary",
            )
        )
    return results
