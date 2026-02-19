"""
Validation engine for the DDD pipeline.

Provides:
- ValidationEngine: orchestrates rule execution, collects results
- Rule registry organized by phase for efficient per-phase validation

Design principles:
- Rules are registered via the @validation_rule decorator (see __init__.py)
- The engine receives the full artifact dict so cross-phase rules can access
  any previously generated artifact
- Deterministic only: no LLM calls, pure logic checks
"""

import logging
from collections import defaultdict
from typing import Any, Callable

from pydantic import BaseModel

from validation.models import (
    ValidationReport,
    ValidationResult,
    ValidationSeverity,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rule descriptor — lightweight wrapper around a decorated function
# ---------------------------------------------------------------------------

class RegisteredRule:
    """
    A validation rule registered in the engine.

    Wraps a callable that accepts ``artifacts: dict[str, BaseModel]``
    and returns a list of ``ValidationResult``.
    """

    __slots__ = ("rule_id", "description", "phase", "severity_on_fail", "fn")

    def __init__(
        self,
        rule_id: str,
        description: str,
        phase: str,
        severity_on_fail: ValidationSeverity,
        fn: Callable[[dict[str, BaseModel]], list[ValidationResult]],
    ) -> None:
        self.rule_id = rule_id
        self.description = description
        self.phase = phase
        self.severity_on_fail = severity_on_fail
        self.fn = fn

    def __repr__(self) -> str:
        return f"RegisteredRule({self.rule_id!r}, phase={self.phase!r})"


# ---------------------------------------------------------------------------
# Global rule registry — populated by the @validation_rule decorator
# ---------------------------------------------------------------------------

_RULE_REGISTRY: list[RegisteredRule] = []


def _register_rule(rule: RegisteredRule) -> None:
    """Append a rule to the global registry (called by the decorator)."""
    _RULE_REGISTRY.append(rule)


def get_registered_rules() -> list[RegisteredRule]:
    """Return a snapshot of all globally registered rules."""
    return list(_RULE_REGISTRY)


# ---------------------------------------------------------------------------
# Validation engine
# ---------------------------------------------------------------------------

class ValidationEngine:
    """
    Orchestrates validation rule execution across pipeline phases.

    Usage::

        engine = ValidationEngine()          # picks up all decorated rules
        report = engine.validate_phase("01_glossary", state.artifacts)
        all_reports = engine.validate_all(state.artifacts)
    """

    def __init__(self) -> None:
        # Index rules by phase for efficient lookup
        self._rules_by_phase: dict[str, list[RegisteredRule]] = defaultdict(list)
        for rule in get_registered_rules():
            self._rules_by_phase[rule.phase].append(rule)

        total = sum(len(v) for v in self._rules_by_phase.values())
        phases = len(self._rules_by_phase)
        logger.info(
            f"ValidationEngine initialized: {total} rules across {phases} phases"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_phase(
        self,
        phase_id: str,
        artifacts: dict[str, BaseModel],
    ) -> ValidationReport:
        """
        Run all rules registered for *phase_id* against *artifacts*.

        Rules whose required artifact keys are not yet present in *artifacts*
        are silently skipped (relevant for cross-phase rules executed early).

        Returns a ``ValidationReport`` for the phase.
        """
        results: list[ValidationResult] = []

        for rule in self._rules_by_phase.get(phase_id, []):
            try:
                rule_results = rule.fn(artifacts)
                results.extend(rule_results)
            except Exception:
                logger.exception(f"Rule {rule.rule_id} raised an exception")
                results.append(
                    ValidationResult(
                        rule_id=rule.rule_id,
                        severity=ValidationSeverity.WARNING,
                        phase=phase_id,
                        message=f"Rule {rule.rule_id} failed with an internal error",
                    )
                )

        return ValidationReport(phase=phase_id, results=results)

    def validate_all(
        self,
        artifacts: dict[str, BaseModel],
    ) -> dict[str, ValidationReport]:
        """
        Run every registered rule, grouped by phase.

        Returns a dict mapping ``phase_id → ValidationReport``.
        """
        reports: dict[str, ValidationReport] = {}
        for phase_id in sorted(self._rules_by_phase.keys()):
            reports[phase_id] = self.validate_phase(phase_id, artifacts)
        return reports

    def get_rules_for_phase(self, phase_id: str) -> list[RegisteredRule]:
        """List all rules registered for a given phase."""
        return list(self._rules_by_phase.get(phase_id, []))

    @property
    def rule_count(self) -> int:
        """Total number of registered rules."""
        return sum(len(v) for v in self._rules_by_phase.values())
