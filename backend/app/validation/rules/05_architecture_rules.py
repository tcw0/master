"""
Validation rules for Phase 5: Technical Architecture.

Cross-phase checks ensuring the architecture covers all bounded contexts.
"""

from collections import Counter

from pydantic import BaseModel

from validation import validation_rule
from validation.models import ValidationResult, ValidationSeverity


@validation_rule(
    rule_id="architecture.elements_unique_per_layer",
    phase="05_architecture",
    description="Element names within each architectural layer must be unique",
    severity_on_fail=ValidationSeverity.WARNING,
)
def elements_unique_per_layer(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
    arch_artifact = artifacts.get("architecture")
    if arch_artifact is None:
        return []

    results: list[ValidationResult] = []
    duplicates_found = []

    layers = ["domain_layer", "application_layer", "presentation_layer", "infrastructure_layer"]

    for arch in arch_artifact.architectures:
        for layer in layers:
            elements = getattr(arch, layer, [])
            el_names = [e.name.strip().lower() for e in elements]
            counts = Counter(el_names)
            dups = [name for name, count in counts.items() if count > 1]
            if dups:
                duplicates_found.append((arch.bounded_context, layer, dups))

    if duplicates_found:
        for context, layer, dups in duplicates_found:
            for dup in dups:
                results.append(
                    ValidationResult(
                        rule_id="architecture.elements_unique_per_layer",
                        severity=ValidationSeverity.WARNING,
                        phase="05_architecture",
                        message=f"Duplicate element '{dup}' in {layer} of context '{context}'",
                        source_element=context,
                        suggestion=f"Ensure all elements in {layer} have unique names",
                    )
                )
    else:
        results.append(
            ValidationResult(
                rule_id="architecture.elements_unique_per_layer",
                severity=ValidationSeverity.PASS,
                phase="05_architecture",
                message="All elements are unique within their respective layers",
            )
        )
    return results


