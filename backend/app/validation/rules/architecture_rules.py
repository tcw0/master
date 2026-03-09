"""
Validation rules for Phase 5: Technical Architecture.

Cross-phase checks ensuring the architecture covers all bounded contexts.
"""

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="architecture.contexts_coverage",
    phase="05_architecture",
    description="Every bounded context from Phase 3 must have a corresponding architecture definition",
    severity_on_fail=ValidationSeverity.FAILURE,
)
def contexts_coverage(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    """
    Check that the architecture artifact defines a ContextArchitecture
    for every bounded context identified in Phase 3.

    Missing architecture definitions indicate incomplete technical mapping.
    """
    bc_artifact = artifacts.get("bounded_contexts")
    arch_artifact = artifacts.get("architecture")

    if bc_artifact is None or arch_artifact is None:
        return []

    results: list[ValidationResult] = []

    # Build lookup of architecture definitions (case-insensitive)
    arch_context_names = {
        ca.bounded_context.strip().lower()
        for ca in arch_artifact.architectures
    }

    # Check each bounded context has an architecture entry
    bc_names = [c.name.strip() for c in bc_artifact.bounded_contexts]
    missing = [
        name for name in bc_names if name.strip().lower() not in arch_context_names
    ]

    if missing:
        for name in missing:
            results.append(
                ValidationResult(
                    rule_id="architecture.contexts_coverage",
                    severity=ValidationSeverity.FAILURE,
                    phase="05_architecture",
                    message=f"Bounded context '{name}' has no architecture definition",
                    source_element=name,
                    suggestion=f"Add a ContextArchitecture entry for '{name}'",
                )
            )
    else:
        results.append(
            ValidationResult(
                rule_id="architecture.contexts_coverage",
                severity=ValidationSeverity.PASS,
                phase="05_architecture",
                message=f"All {len(bc_names)} bounded contexts have architecture definitions",
            )
        )

    return results
