"""
Validation rules for Phase 3: Bounded Contexts.

Intra-phase and cross-phase checks for context definitions and context map.
"""

from collections import Counter

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="contexts.no_duplicate_context_names",
    phase="03_bounded_contexts",
    description="No two bounded contexts should share the same name (case-insensitive)",
    severity_on_fail=ValidationSeverity.FAILURE,
)
def no_duplicate_context_names(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that every bounded context has a unique name.

    Duplicate context names would make the context map ambiguous and
    break aggregate-to-context assignment in Phase 4.
    """
    bc_artifact = artifacts.get("bounded_contexts")
    if bc_artifact is None:
        return []

    results: list[ValidationResult] = []
    context_names = [c.name.strip().lower() for c in bc_artifact.contexts]
    counts = Counter(context_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="contexts.no_duplicate_context_names",
                    severity=ValidationSeverity.FAILURE,
                    phase="03_bounded_contexts",
                    message=f"Duplicate bounded context name '{name}' appears {count} times",
                    source_element=name,
                    suggestion="Rename or merge duplicate bounded contexts",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="contexts.no_duplicate_context_names",
                severity=ValidationSeverity.PASS,
                phase="03_bounded_contexts",
                message=f"All {len(context_names)} bounded context names are unique",
            )
        )

    return results
