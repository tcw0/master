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
    severity_on_fail=ValidationSeverity.WARNING,
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
                    severity=ValidationSeverity.WARNING,
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


@validation_rule(
    rule_id="aggregates.root_entity_exists",
    phase="04_aggregates",
    description="The root_entity must be explicitly defined in the elements list as an entity",
    severity_on_fail=ValidationSeverity.WARNING,
)
def root_entity_exists(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    agg_artifact = artifacts.get("aggregates")
    if agg_artifact is None:
        return []

    results: list[ValidationResult] = []
    missing_roots = []

    for agg in agg_artifact.aggregates:
        if not agg.root_entity:
            missing_roots.append((agg.name, "No root entity specified"))
            continue

        root_found = False
        for el in agg.elements:
            if el.name == agg.root_entity:
                if el.element_type == "entity":
                    root_found = True
                else:
                    missing_roots.append((agg.name, f"Root entity '{agg.root_entity}' is defined as '{el.element_type}' instead of 'entity'"))
                break

        if not root_found and not any(m[0] == agg.name for m in missing_roots):
            missing_roots.append((agg.name, f"Root entity '{agg.root_entity}' is not defined in elements"))

    if missing_roots:
        for agg_name, reason in missing_roots:
            results.append(
                ValidationResult(
                    rule_id="aggregates.root_entity_exists",
                    severity=ValidationSeverity.WARNING,
                    phase="04_aggregates",
                    message=f"Aggregate '{agg_name}' has an invalid root_entity: {reason}",
                    source_element=agg_name,
                    suggestion="Ensure root_entity is correctly defined in the elements list as an 'entity'",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="aggregates.root_entity_exists",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message="All aggregates have valid root entities",
            )
        )
    return results


@validation_rule(
    rule_id="aggregates.unique_element_names",
    phase="04_aggregates",
    description="Elements inside an aggregate cannot share the same name",
    severity_on_fail=ValidationSeverity.WARNING,
)
def unique_element_names(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    agg_artifact = artifacts.get("aggregates")
    if agg_artifact is None:
        return []

    results: list[ValidationResult] = []
    duplicates_found = []

    for agg in agg_artifact.aggregates:
        el_names = [e.name.strip().lower() for e in agg.elements]
        counts = Counter(el_names)
        dups = [name for name, count in counts.items() if count > 1]
        if dups:
            duplicates_found.append((agg.name, dups))

    if duplicates_found:
        for agg_name, dups in duplicates_found:
            for dup in dups:
                results.append(
                    ValidationResult(
                        rule_id="aggregates.unique_element_names",
                        severity=ValidationSeverity.WARNING,
                        phase="04_aggregates",
                        message=f"Aggregate '{agg_name}' contains duplicate element name '{dup}'",
                        source_element=agg_name,
                        suggestion="Ensure all elements within the aggregate have unique names",
                    )
                )
    else:
        results.append(
            ValidationResult(
                rule_id="aggregates.unique_element_names",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message="All elements within aggregates have unique names",
            )
        )
    return results


