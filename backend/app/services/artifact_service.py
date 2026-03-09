"""
Artifact Service — Persistence for DDD artifacts and validation reports.

Handles saving and loading of artifacts in a filesystem-based store.
Designed with a clear interface so it can be replaced with a
database-backed implementation in Phase C.

Design principles:
- Single responsibility: only persistence, no orchestration
- Raises exceptions instead of sys.exit()
- Output directory structure mirrors provider/model hierarchy
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from models.glossary import GlossaryArtifact
from models.event_storming import EventStormingArtifact
from models.bounded_contexts import BoundedContextsArtifact
from models.aggregates import AggregatesArtifact
from models.architecture import ArchitectureArtifact
from pipeline_config import PhaseConfig, OUTPUT_DIR
from services.llm_service import LLMService
from validation.models import ValidationReport

logger = logging.getLogger(__name__)


class ArtifactService:
    """
    File-based artifact persistence.

    Output directory structure:
    - ollama:      output/{domain}/ollama/
    - openrouter:  output/{domain}/openrouter/{model_family}/

    Usage::

        service = ArtifactService()
        path = service.save_artifact(domain, provider, model, phase, artifact)
    """

    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_artifact(
        self,
        domain: str,
        provider: str,
        model: str,
        phase: PhaseConfig,
        artifact: BaseModel,
        raw_response: str | None = None,
    ) -> Path:
        """
        Save artifact to disk with schema and optional raw response.

        Saves:
        - {timestamp}_{phase_id}.json: The artifact data
        - {timestamp}_{phase_id}.schema.json: JSON schema for validation
        - {timestamp}_{phase_id}.raw.txt: Raw LLM response (if available)

        Returns:
            Path to the saved artifact JSON file.
        """
        out_dir = self._get_output_dir(domain, provider, model)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{ts}_{phase.id}"

        # Save artifact as JSON
        artifact_path = out_dir / f"{base_name}.json"
        artifact_path.write_text(
            artifact.model_dump_json(indent=2), encoding="utf-8",
        )
        logger.info(f"  → Saved: {artifact_path.name}")

        # Save JSON schema for validation/documentation
        schema_path = out_dir / f"{base_name}.schema.json"
        schema_path.write_text(
            json.dumps(artifact.model_json_schema(), indent=2), encoding="utf-8",
        )
        logger.info(f"  → Schema: {schema_path.name}")

        # Save raw response for debugging (if available)
        if raw_response:
            raw_path = out_dir / f"{base_name}.raw.txt"
            raw_path.write_text(raw_response, encoding="utf-8")
            logger.info(f"  → Raw: {raw_path.name}")

        return artifact_path

    def save_validation_report(
        self,
        domain: str,
        provider: str,
        model: str,
        phase: PhaseConfig,
        report: ValidationReport,
    ) -> Path:
        """Save a validation report to disk alongside its artifact."""
        out_dir = self._get_output_dir(domain, provider, model)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{ts}_{phase.id}"

        report_path = out_dir / f"{base_name}.validation.json"
        report_path.write_text(
            report.model_dump_json(indent=2), encoding="utf-8",
        )
        logger.info(f"  → Validation: {report_path.name}")

        return report_path

    @staticmethod
    def create_error_artifact(phase: PhaseConfig, error: str) -> BaseModel:
        """
        Create a minimal error artifact for failed phases.

        This allows the pipeline to continue and record the failure
        rather than aborting entirely.
        """
        schema = phase.output_schema

        if schema == GlossaryArtifact:
            return schema.model_construct(
                terms=[],
                bounded_context_hints=[],
            )
        elif schema == EventStormingArtifact:
            return schema.model_construct(
                commands=[],
                domain_events=[],
                policies=[],
                flows=[],
                ambiguities=[f"[ERROR: {error}]"],
            )
        elif schema == BoundedContextsArtifact:
            return schema.model_construct(
                bounded_contexts=[],
                context_relationships=[],
                term_overlaps=[],
            )
        elif schema == AggregatesArtifact:
            return schema.model_construct(
                aggregates=[],
                design_decisions=[f"[ERROR: {error}]"],
            )
        elif schema == ArchitectureArtifact:
            return schema.model_construct(
                architectures=[],
                anti_corruption_layers=[],
                published_interfaces=[],
                technical_patterns=[],
            )
        else:
            raise ValueError(f"Unknown artifact type: {schema}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_output_dir(
        self, domain: str, provider: str, model: str,
    ) -> Path:
        """Build and create output directory based on provider hierarchy."""
        if provider == "openrouter":
            family = LLMService.detect_model_family(model)
            out_dir = self.output_dir / domain / provider / family
        else:
            out_dir = self.output_dir / domain / provider
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
