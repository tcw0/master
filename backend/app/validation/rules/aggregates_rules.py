"""
Validation rules for Phase 4: Aggregates.

Intra-phase and cross-phase checks for aggregate design.
"""

from collections import Counter

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="aggregates.no_duplicate_aggregate_names",
    phase="04_aggregates",
    description="No two aggregates should share the same name (case-insensitive)",
    severity_on_fail=ValidationSeverity.FAILURE,
)
def no_duplicate_aggregate_names(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that every aggregate has a unique name.

    Duplicate aggregate names break context assignment and make
    cross-aggregate references ambiguous.
    """
    agg_artifact = artifacts.get("aggregates")
    if agg_artifact is None:
        return []

    results: list[ValidationResult] = []
    agg_names = [a.name.strip().lower() for a in agg_artifact.aggregates]
    counts = Counter(agg_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="aggregates.no_duplicate_aggregate_names",
                    severity=ValidationSeverity.FAILURE,
                    phase="04_aggregates",
                    message=f"Duplicate aggregate name '{name}' appears {count} times",
                    source_element=name,
                    suggestion="Rename or merge duplicate aggregates",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="aggregates.no_duplicate_aggregate_names",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message=f"All {len(agg_names)} aggregate names are unique",
            )
        )

    return results
