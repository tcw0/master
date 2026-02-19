"""
Validation framework for the DDD pipeline.

Public API:
- ``validation_rule``: decorator to register validation rule functions
- ``ValidationEngine``: orchestrates rule execution
- ``ValidationReport``, ``ValidationResult``, ``ValidationSeverity``: data models

Usage::

    from validation import validation_rule, ValidationSeverity

    @validation_rule(
        rule_id="glossary.no_duplicate_terms",
        phase="01_glossary",
        description="No two glossary terms should share the same name",
        severity_on_fail=ValidationSeverity.FAILURE,
    )
    def no_duplicate_terms(artifacts):
        ...
"""

from typing import Callable

from pydantic import BaseModel

from validation.engine import RegisteredRule, ValidationEngine, _register_rule
from validation.models import (
    ValidationReport,
    ValidationResult,
    ValidationSeverity,
)


def validation_rule(
    *,
    rule_id: str,
    phase: str,
    description: str,
    severity_on_fail: ValidationSeverity = ValidationSeverity.WARNING,
) -> Callable:
    """
    Decorator that registers a function as a validation rule.

    The decorated function must have the signature::

        def my_rule(artifacts: dict[str, BaseModel]) -> list[ValidationResult]:
            ...

    Args:
        rule_id: Unique dotted identifier (e.g., ``glossary.no_duplicate_terms``).
        phase: Phase this rule applies to (e.g., ``01_glossary``).
        description: Human-readable description of what the rule checks.
        severity_on_fail: Default severity when the rule detects a violation.
    """

    def decorator(fn: Callable[[dict[str, BaseModel]], list["ValidationResult"]]) -> Callable:
        rule = RegisteredRule(
            rule_id=rule_id,
            description=description,
            phase=phase,
            severity_on_fail=severity_on_fail,
            fn=fn,
        )
        _register_rule(rule)
        return fn

    return decorator


# Import rule modules so that decorators fire at import time.
# This must happen AFTER the decorator is defined.
import validation.rules  # noqa: E402, F401


__all__ = [
    "validation_rule",
    "ValidationEngine",
    "ValidationReport",
    "ValidationResult",
    "ValidationSeverity",
]
