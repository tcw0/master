"""
Pipeline Service — DDD artifact generation orchestration.

Handles:
- LCEL chain construction with structured outputs
- Phase execution with retry logic and validation
- Full workflow orchestration across all 5 phases

Design principles:
- Depends on LLMService and ArtifactService via constructor injection
- Raises exceptions instead of sys.exit() — callers handle errors
- Supports both full-pipeline and single-phase execution
- Validation failures consume retry attempts automatically
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableSerializable,
)
from pydantic import BaseModel, ValidationError

from pipeline_config import (
    PhaseConfig,
    PHASES,
    PROMPTS_DIR,
    WorkflowState,
)
from services.llm_service import LLMService
from services.artifact_service import ArtifactService
from validation import ValidationEngine
from validation.models import ValidationReport

logger = logging.getLogger(__name__)


def _read_file(path: Path) -> str:
    """Read file contents with descriptive error on missing files."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Required file not found: {path}")


class PipelineService:
    """
    Orchestrates the 5-phase DDD artifact generation pipeline.

    Uses LCEL chains with structured outputs enforced via Pydantic schemas.
    Each phase consumes previously produced artifacts (not raw chat history).

    Usage::

        llm_svc = LLMService(provider="openrouter", model="openai/gpt-4o")
        art_svc = ArtifactService()
        pipeline = PipelineService(llm_svc, art_svc)
        state = pipeline.run_workflow(Path("requirements.txt"))
    """

    def __init__(
        self,
        llm_service: LLMService,
        artifact_service: ArtifactService | None = None,
        validation_engine: ValidationEngine | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.artifact_service = artifact_service
        self.validation_engine = validation_engine or ValidationEngine()

    # =================================================================
    # Public API
    # =================================================================

    def run_workflow(
        self,
        requirements_path: Path,
        max_retries: int = 2,
        phases: list[PhaseConfig] | None = None,
    ) -> WorkflowState:
        """
        Execute the complete DDD workflow pipeline.

        Args:
            requirements_path: Path to requirements document.
            max_retries: Max retries per phase on failure.
            phases: Optional subset of phases to run (defaults to all 5).

        Returns:
            WorkflowState with all generated artifacts.

        Raises:
            FileNotFoundError: If requirements file or prompt templates are missing.
        """
        target_phases = phases or PHASES
        self._ensure_prompts_present(target_phases)

        domain = requirements_path.stem.lower()

        state = WorkflowState(
            domain=domain,
            provider=self.llm_service.provider,
            model=self.llm_service.model,
            requirements_path=requirements_path,
        )

        self._print_workflow_header(state)

        successful = 0
        for phase in target_phases:
            artifact, raw_or_error, report = self.run_phase(
                phase, state, max_retries=max_retries,
            )

            if artifact is not None:
                # Success: store artifact and raw response
                state.artifacts[phase.output_key] = artifact
                if raw_or_error:
                    state.raw_responses[phase.output_key] = raw_or_error
                if report is not None:
                    state.validation_reports[phase.id] = report

                # Persist to disk (when ArtifactService is available)
                if self.artifact_service:
                    self.artifact_service.save_artifact(
                        domain, self.llm_service.provider,
                        self.llm_service.model, phase, artifact, raw_or_error,
                    )
                    if report is not None:
                        self.artifact_service.save_validation_report(
                            domain, self.llm_service.provider,
                            self.llm_service.model, phase, report,
                        )
                successful += 1
            else:
                # Failure: create error artifact to allow pipeline to continue
                state.errors[phase.output_key] = raw_or_error or "Unknown error"
                if self.artifact_service:
                    error_artifact = self.artifact_service.create_error_artifact(
                        phase, raw_or_error or "Unknown error",
                    )
                    state.artifacts[phase.output_key] = error_artifact
                    self.artifact_service.save_artifact(
                        domain, self.llm_service.provider,
                        self.llm_service.model, phase, error_artifact,
                    )
                logger.error(f"✗ {phase.name} failed: {raw_or_error}")

            print()  # Blank line between phases

        self._print_workflow_summary(state, successful, len(target_phases))

        return state

    def run_phase(
        self,
        phase: PhaseConfig,
        state: WorkflowState,
        max_retries: int = 2,
    ) -> tuple[BaseModel | None, str | None, ValidationReport | None]:
        """
        Execute a single phase with retry logic.

        Two-stage validation per attempt:
        1. Structural: LLM output must parse into the expected Pydantic schema.
        2. Semantic: deterministic DDD validation rules.
           FAILURE-severity violations consume a retry attempt.

        Args:
            phase: Phase configuration.
            state: Workflow state with existing artifacts.
            max_retries: Maximum retry attempts.

        Returns:
            Tuple of (artifact, raw_response, validation_report).
            On failure: (None, error_message, None).
        """
        logger.info(f"--- Phase {phase.phase_number}: {phase.name} ---")

        chain = self._build_structured_chain(phase, state, include_raw=True)

        last_error = None
        raw_response = None

        for attempt in range(max_retries + 1):
            try:
                result = chain.invoke({})

                # Handle both dict (with raw) and direct model returns
                if isinstance(result, dict):
                    artifact = result.get("parsed")
                    raw_msg = result.get("raw")
                    raw_response = self._extract_raw_response(raw_msg)
                else:
                    artifact = result
                    raw_response = None

                # Validate we got the expected type
                if artifact is None:
                    raise ValueError("LLM returned None")

                if not isinstance(artifact, phase.output_schema):
                    raise TypeError(
                        f"Expected {phase.output_schema.__name__}, "
                        f"got {type(artifact).__name__}"
                    )

                self._log_artifact_summary(phase, artifact)

                # --- Stage 2: Semantic validation ---
                if self.validation_engine is not None:
                    temp_artifacts = {
                        **state.artifacts, phase.output_key: artifact,
                    }
                    report = self.validation_engine.validate_phase(
                        phase.id, temp_artifacts,
                    )

                    self._log_validation_summary(phase, report)

                    if report.has_failures() and attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}: {report.failure_count} "
                            f"validation failure(s). Retrying..."
                        )
                        continue  # consume a retry attempt

                    return artifact, raw_response, report

                return artifact, raw_response, None

            except (ValidationError, TypeError, ValueError) as e:
                last_error = str(e)
                if attempt < max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {last_error}. Retrying...",
                    )
                else:
                    logger.error(
                        f"Phase {phase.id} failed after "
                        f"{max_retries + 1} attempts: {last_error}",
                    )

        return None, last_error, None

    # =================================================================
    # Chain Building (LCEL)
    # =================================================================

    def _build_context_builder(
        self,
        phase: PhaseConfig,
        state: WorkflowState,
    ) -> Callable[[Any], dict[str, str]]:
        """Create a context builder function that assembles prompt variables."""

        def build_context(_: Any) -> dict[str, str]:
            ctx: dict[str, str] = {}
            for inp in phase.inputs:
                if inp == "requirements":
                    ctx["requirements"] = state.get_requirements_content()
                else:
                    ctx[inp] = state.get_artifact_as_json(inp)
            return ctx

        return build_context

    def _build_prompt(self, phase: PhaseConfig) -> ChatPromptTemplate:
        """
        Build a ChatPromptTemplate for a phase.

        Uses system + human message format for better LLM guidance.
        """
        template_path = PROMPTS_DIR / phase.prompt_file
        task_template = _read_file(template_path)

        messages = []
        if phase.system_prompt:
            messages.append(
                SystemMessagePromptTemplate.from_template(phase.system_prompt),
            )
        messages.append(
            HumanMessagePromptTemplate.from_template(task_template),
        )

        return ChatPromptTemplate.from_messages(messages)

    def _build_structured_chain(
        self,
        phase: PhaseConfig,
        state: WorkflowState,
        include_raw: bool = True,
    ) -> RunnableSerializable:
        """
        Build an LCEL chain with structured output enforcement.

        Chain structure:
        1. RunnablePassthrough (accepts empty input)
        2. Context builder (assembles prompt variables from workflow state)
        3. Prompt template (formats the messages)
        4. Structured LLM (enforces schema output via selected method)
        """
        prompt = self._build_prompt(phase)
        context_builder = self._build_context_builder(phase, state)

        structured_llm = self.llm_service.llm.with_structured_output(
            phase.output_schema,
            method=self.llm_service.structured_output_method,
            include_raw=include_raw,
        )

        chain = (
            RunnablePassthrough()
            | RunnableLambda(context_builder)
            | prompt
            | structured_llm
        )

        return chain

    # =================================================================
    # Helpers
    # =================================================================

    @staticmethod
    def _extract_raw_response(raw_msg: Any) -> str | None:
        """Extract raw response string from LLM message for debugging."""
        if raw_msg is None:
            return None

        content = getattr(raw_msg, "content", None)
        if isinstance(content, str) and content:
            return content
        elif isinstance(content, list) and content:
            return json.dumps(content, indent=2, default=str)
        elif hasattr(raw_msg, "tool_calls") and raw_msg.tool_calls:
            return json.dumps(raw_msg.tool_calls, indent=2, default=str)
        else:
            return str(raw_msg)

    @staticmethod
    def _log_validation_summary(
        phase: PhaseConfig, report: ValidationReport,
    ) -> None:
        """Log a compact summary of validation results."""
        parts = []
        if report.failure_count:
            parts.append(f"{report.failure_count} failure(s)")
        if report.warning_count:
            parts.append(f"{report.warning_count} warning(s)")
        if report.pass_count:
            parts.append(f"{report.pass_count} passed")
        summary = ", ".join(parts) if parts else "no rules executed"

        icon = "✗" if report.has_failures() else (
            "⚠" if report.has_warnings() else "✓"
        )
        logger.info(f"  {icon} Validation [{phase.name}]: {summary}")

    @staticmethod
    def _log_artifact_summary(
        phase: PhaseConfig, artifact: BaseModel,
    ) -> None:
        """Log a summary of the generated artifact."""
        summary_parts = []

        if hasattr(artifact, "terms"):
            summary_parts.append(f"{len(artifact.terms)} terms")
        if hasattr(artifact, "domain_events"):
            summary_parts.append(f"{len(artifact.domain_events)} events")
        if hasattr(artifact, "commands"):
            summary_parts.append(f"{len(artifact.commands)} commands")
        if hasattr(artifact, "bounded_contexts"):
            summary_parts.append(f"{len(artifact.bounded_contexts)} contexts")
        if hasattr(artifact, "context_relationships"):
            summary_parts.append(f"{len(artifact.context_relationships)} relationships")
        if hasattr(artifact, "aggregates"):
            summary_parts.append(f"{len(artifact.aggregates)} aggregates")
        if hasattr(artifact, "architectures"):
            summary_parts.append(f"{len(artifact.architectures)} architectures")

        summary = ", ".join(summary_parts) if summary_parts else "completed"
        logger.info(f"✓ {phase.name}: {summary}")

    def _print_workflow_header(self, state: WorkflowState) -> None:
        """Print workflow configuration banner."""
        print()
        print("=" * 60)
        print("DDD Artifact Generation Pipeline (Structured Output)")
        print("=" * 60)
        print(f"  Run ID       : {state.run_id}")
        print(f"  Domain       : {state.domain}")
        print(f"  Provider     : {self.llm_service.provider}")
        print(f"  Model        : {self.llm_service.model}")
        print(f"  Temperature  : {self.llm_service.temperature}")
        print(f"  Struct. Out  : {self.llm_service.structured_output_method}")
        print(f"  Requirements : {state.requirements_path.name}")
        print(f"  Req. Hash    : {state.get_requirements_hash()}")
        print("=" * 60)
        print()

    @staticmethod
    def _print_workflow_summary(
        state: WorkflowState,
        successful: int,
        total: int,
    ) -> None:
        """Print pipeline completion summary."""
        total_failures = sum(
            r.failure_count for r in state.validation_reports.values()
        )
        total_warnings = sum(
            r.warning_count for r in state.validation_reports.values()
        )
        print("=" * 60)
        print(f"Pipeline Complete: {successful}/{total} phases successful")
        if total_failures or total_warnings:
            print(
                f"Validation: {total_failures} failure(s), "
                f"{total_warnings} warning(s)",
            )
        if state.errors:
            print(f"Errors: {list(state.errors.keys())}")
        print("=" * 60)

    @staticmethod
    def _ensure_prompts_present(
        phases: list[PhaseConfig] | None = None,
    ) -> None:
        """Verify all required prompt templates exist."""
        target = phases or PHASES
        missing = [
            PROMPTS_DIR / phase.prompt_file
            for phase in target
            if not (PROMPTS_DIR / phase.prompt_file).exists()
        ]
        if missing:
            missing_str = "\n".join(f"  - {p}" for p in missing)
            raise FileNotFoundError(
                f"Missing prompt templates:\n{missing_str}",
            )
