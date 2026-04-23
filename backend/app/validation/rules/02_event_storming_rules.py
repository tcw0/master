"""
Validation rules for Phase 2: Event Storming.

Intra-phase checks verifying internal consistency of events, commands, and actors.
"""

from collections import Counter

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="events.no_duplicate_event_names",
    phase="02_event_storming",
    description="No two domain events should share the same name (case-insensitive)",
    severity_on_fail=ValidationSeverity.WARNING,
)
def no_duplicate_event_names(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that every domain event has a unique name.

    Duplicate event names make cross-phase traceability ambiguous and
    indicate either a modelling error or a naming collision.
    """
    events_artifact = artifacts.get("events")
    if events_artifact is None:
        return []

    results: list[ValidationResult] = []
    event_names = [e.name.strip().lower() for e in events_artifact.domain_events]
    counts = Counter(event_names)

    duplicates = {name: count for name, count in counts.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            results.append(
                ValidationResult(
                    rule_id="events.no_duplicate_event_names",
                    severity=ValidationSeverity.WARNING,
                    phase="02_event_storming",
                    message=f"Duplicate domain event '{name}' appears {count} times",
                    source_element=name,
                    suggestion="Rename or merge duplicate domain events",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="events.no_duplicate_event_names",
                severity=ValidationSeverity.PASS,
                phase="02_event_storming",
                message=f"All {len(event_names)} domain event names are unique",
            )
        )

    return results


@validation_rule(
    rule_id="events.flow_step_completeness",
    phase="02_event_storming",
    description="Every step in a flow must have an event and an aggregate",
    severity_on_fail=ValidationSeverity.WARNING,
)
def flow_step_completeness(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    events_artifact = artifacts.get("events")
    if events_artifact is None:
        return []

    results: list[ValidationResult] = []
    incomplete_steps = []

    for flow in events_artifact.flows:
        for i, step in enumerate(flow.steps):
            if not step.event or not step.aggregate:
                incomplete_steps.append((flow.name, i))

    if incomplete_steps:
        for flow_name, step_idx in incomplete_steps:
            results.append(
                ValidationResult(
                    rule_id="events.flow_step_completeness",
                    severity=ValidationSeverity.WARNING,
                    phase="02_event_storming",
                    message=f"Flow '{flow_name}' has incomplete step at index {step_idx} (missing event or aggregate)",
                    source_element=flow_name,
                    suggestion="Ensure every step defines both an event and an aggregate",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="events.flow_step_completeness",
                severity=ValidationSeverity.PASS,
                phase="02_event_storming",
                message="All flow steps have an event and aggregate",
            )
        )
    return results

