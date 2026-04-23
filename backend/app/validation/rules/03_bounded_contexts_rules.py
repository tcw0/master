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
    severity_on_fail=ValidationSeverity.WARNING,
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
    context_names = [c.name.strip().lower() for c in bc_artifact.bounded_contexts]
    counts = Counter(context_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="contexts.no_duplicate_context_names",
                    severity=ValidationSeverity.WARNING,
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


@validation_rule(
    rule_id="contexts.relationship_references_valid_contexts",
    phase="03_bounded_contexts",
    description="Context relationships must reference defined bounded contexts",
    severity_on_fail=ValidationSeverity.WARNING,
)
def relationship_references_valid_contexts(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    bc_artifact = artifacts.get("bounded_contexts")
    if bc_artifact is None:
        return []

    results: list[ValidationResult] = []
    context_names = {c.name.strip().lower() for c in bc_artifact.bounded_contexts}
    invalid_refs = []

    for rel in bc_artifact.context_relationships:
        if rel.source_context.strip().lower() not in context_names:
            invalid_refs.append((rel.source_context, "source_context", rel.relationship_type))
        if rel.target_context.strip().lower() not in context_names:
            invalid_refs.append((rel.target_context, "target_context", rel.relationship_type))

    if invalid_refs:
        for context, side, rel_type in invalid_refs:
            results.append(
                ValidationResult(
                    rule_id="contexts.relationship_references_valid_contexts",
                    severity=ValidationSeverity.WARNING,
                    phase="03_bounded_contexts",
                    message=f"Relationship uses undefined {side} '{context}'",
                    source_element=context,
                    suggestion="Ensure the context is defined in bounded_contexts",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="contexts.relationship_references_valid_contexts",
                severity=ValidationSeverity.PASS,
                phase="03_bounded_contexts",
                message="All relationships reference valid contexts",
            )
        )
    return results


@validation_rule(
    rule_id="contexts.no_self_referencing_relationships",
    phase="03_bounded_contexts",
    description="A bounded context cannot have a relationship with itself",
    severity_on_fail=ValidationSeverity.WARNING,
)
def no_self_referencing_relationships(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    bc_artifact = artifacts.get("bounded_contexts")
    if bc_artifact is None:
        return []

    results: list[ValidationResult] = []
    self_refs = []

    for rel in bc_artifact.context_relationships:
        if rel.source_context.strip().lower() == rel.target_context.strip().lower():
            self_refs.append(rel.source_context)

    if self_refs:
        for context in self_refs:
            results.append(
                ValidationResult(
                    rule_id="contexts.no_self_referencing_relationships",
                    severity=ValidationSeverity.WARNING,
                    phase="03_bounded_contexts",
                    message=f"Bounded context '{context}' has a relationship with itself",
                    source_element=context,
                    suggestion="Remove the self-referencing relationship",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="contexts.no_self_referencing_relationships",
                severity=ValidationSeverity.PASS,
                phase="03_bounded_contexts",
                message="No self-referencing relationships found",
            )
        )
    return results

