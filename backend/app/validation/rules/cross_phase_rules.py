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
    rule_id="cross.bounded_context_terms_in_glossary",
    phase="03_bounded_contexts",
    description="Terms in bounded contexts must exist in the glossary",
    severity_on_fail=ValidationSeverity.WARNING,
)
def bounded_context_terms_in_glossary(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    glossary = artifacts.get("glossary")
    bc_artifact = artifacts.get("bounded_contexts")
    if glossary is None or bc_artifact is None:
        return []

    results: list[ValidationResult] = []
    glossary_terms = {_normalize(t.name) for t in glossary.terms}

    missing_terms = []
    for bc in bc_artifact.bounded_contexts:
        for term in bc.ubiquitous_language_terms:
            if _normalize(term) not in glossary_terms:
                missing_terms.append((bc.name, term))

    if missing_terms:
        for context, term in missing_terms:
            results.append(
                ValidationResult(
                    rule_id="cross.bounded_context_terms_in_glossary",
                    severity=ValidationSeverity.WARNING,
                    phase="03_bounded_contexts",
                    message=f"Bounded context '{context}' uses term '{term}' not found in glossary",
                    source_element=term,
                    suggestion="Add the term to the glossary",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="cross.bounded_context_terms_in_glossary",
                severity=ValidationSeverity.PASS,
                phase="03_bounded_contexts",
                message="All ubiquitous language terms are defined in the glossary",
            )
        )
    return results


@validation_rule(
    rule_id="cross.aggregate_belongs_to_valid_context",
    phase="04_aggregates",
    description="Aggregates must belong to a defined bounded context",
    severity_on_fail=ValidationSeverity.WARNING,
)
def aggregate_belongs_to_valid_context(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    bc_artifact = artifacts.get("bounded_contexts")
    agg_artifact = artifacts.get("aggregates")
    if bc_artifact is None or agg_artifact is None:
        return []

    results: list[ValidationResult] = []
    context_names = {_normalize(c.name) for c in bc_artifact.bounded_contexts}

    invalid_assignments = []
    for agg in agg_artifact.aggregates:
        if _normalize(agg.bounded_context) not in context_names:
            invalid_assignments.append((agg.name, agg.bounded_context))

    if invalid_assignments:
        for agg_name, context in invalid_assignments:
            results.append(
                ValidationResult(
                    rule_id="cross.aggregate_belongs_to_valid_context",
                    severity=ValidationSeverity.WARNING,
                    phase="04_aggregates",
                    message=f"Aggregate '{agg_name}' belongs to undefined context '{context}'",
                    source_element=context,
                    suggestion="Assign the aggregate to a context defined in bounded_contexts",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="cross.aggregate_belongs_to_valid_context",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message="All aggregates belong to valid bounded contexts",
            )
        )
    return results


@validation_rule(
    rule_id="cross.aggregate_commands_match_event_storming",
    phase="04_aggregates",
    description="Commands in aggregates should exist in event storming",
    severity_on_fail=ValidationSeverity.WARNING,
)
def aggregate_commands_match_event_storming(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    events = artifacts.get("events")
    agg_artifact = artifacts.get("aggregates")
    if events is None or agg_artifact is None:
        return []

    results: list[ValidationResult] = []
    event_commands = {_normalize(c.name) for c in events.commands}

    missing_commands = []
    for agg in agg_artifact.aggregates:
        for cmd in agg.commands:
            if _normalize(cmd.name) not in event_commands:
                missing_commands.append((agg.name, cmd.name))

    if missing_commands:
        for agg_name, cmd_name in missing_commands:
            results.append(
                ValidationResult(
                    rule_id="cross.aggregate_commands_match_event_storming",
                    severity=ValidationSeverity.WARNING,
                    phase="04_aggregates",
                    message=f"Command '{cmd_name}' in aggregate '{agg_name}' is missing from event storming",
                    source_element=cmd_name,
                    suggestion="Add the command to the event storming phase or remove it from the aggregate",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="cross.aggregate_commands_match_event_storming",
                severity=ValidationSeverity.PASS,
                phase="04_aggregates",
                message="All aggregate commands map back to event storming",
            )
        )
    return results


