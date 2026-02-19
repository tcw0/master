"""
Validation data models for the DDD pipeline.

Provides:
- ValidationSeverity: outcome levels (PASS, WARNING, FAILURE)
- ValidationResult: a single rule check outcome
- ValidationReport: aggregated results for a phase or full run

Design principles:
- All models are Pydantic for serialization and storage alongside artifacts
- FAILURE severity triggers retry logic in the pipeline
- Reports are append-only and immutable once created
"""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class ValidationSeverity(str, Enum):
    """Outcome level for a validation check."""

    PASS = "pass"
    WARNING = "warning"
    FAILURE = "failure"


class ValidationResult(BaseModel):
    """
    Outcome of a single validation rule execution.

    Each result ties back to a specific rule_id and optionally
    identifies the offending element for targeted review/fix.
    """

    rule_id: str = Field(
        ...,
        description="Unique rule identifier (e.g., 'glossary.no_duplicate_terms')",
    )
    severity: ValidationSeverity = Field(
        ...,
        description="Outcome: pass, warning, or failure",
    )
    phase: str = Field(
        ...,
        description="Phase this check targets (e.g., '01_glossary')",
    )
    message: str = Field(
        ...,
        description="Human-readable explanation of the result",
    )
    source_element: str | None = Field(
        default=None,
        description="The specific element that triggered the violation (e.g., a term name)",
    )
    suggestion: str | None = Field(
        default=None,
        description="Optional remediation hint",
    )


class ValidationReport(BaseModel):
    """
    Aggregated validation results for a phase or a full pipeline run.

    Provides computed summary counts and an overall status derived
    from the worst severity found in the results.
    """

    phase: str = Field(
        ...,
        description="Phase identifier this report covers (or 'all' for full run)",
    )
    results: list[ValidationResult] = Field(
        default_factory=list,
        description="All individual validation results",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def failure_count(self) -> int:
        """Number of FAILURE-severity results."""
        return sum(1 for r in self.results if r.severity == ValidationSeverity.FAILURE)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def warning_count(self) -> int:
        """Number of WARNING-severity results."""
        return sum(1 for r in self.results if r.severity == ValidationSeverity.WARNING)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pass_count(self) -> int:
        """Number of PASS-severity results."""
        return sum(1 for r in self.results if r.severity == ValidationSeverity.PASS)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> str:
        """
        Overall report status derived from worst severity.

        Returns 'fail' if any FAILURE, 'warn' if any WARNING, else 'pass'.
        """
        if self.failure_count > 0:
            return "fail"
        if self.warning_count > 0:
            return "warn"
        return "pass"

    def has_failures(self) -> bool:
        """Check if this report contains any FAILURE results."""
        return self.failure_count > 0

    def has_warnings(self) -> bool:
        """Check if this report contains any WARNING results."""
        return self.warning_count > 0
