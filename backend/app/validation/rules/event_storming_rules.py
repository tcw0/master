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
    severity_on_fail=ValidationSeverity.FAILURE,
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
                    severity=ValidationSeverity.FAILURE,
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
