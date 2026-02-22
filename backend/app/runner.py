"""DDD Pipeline Runner — backward compatibility wrapper.

DEPRECATED: This module is retained for backward compatibility.
Use ``cli.py`` for command-line usage, or import from the service layer directly::

    from services.pipeline_service import PipelineService
    from services.llm_service import LLMService
    from services.artifact_service import ArtifactService

This file delegates entirely to the new service-based architecture.
"""

import warnings

warnings.warn(
    "runner.py is deprecated. Use cli.py or import from services/ directly.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export configuration for backward compatibility
from pipeline_config import (  # noqa: F401, E402
    PhaseConfig,
    PHASES,
    WorkflowState,
    BASE_DIR,
    DATA_DIR,
    OUTPUT_DIR,
    PROMPTS_DIR,
    REQUIREMENTS_DIR,
)

# Re-export services
from services.llm_service import (  # noqa: F401, E402
    LLMService,
    PROVIDER_OLLAMA,
    PROVIDER_OPENROUTER,
)
from services.artifact_service import ArtifactService  # noqa: F401, E402
from services.pipeline_service import PipelineService  # noqa: F401, E402


# Legacy function-based API wrappers

def detect_model_family(model: str) -> str:
    """Legacy wrapper — use LLMService.detect_model_family() instead."""
    return LLMService.detect_model_family(model)


def get_structured_output_method(provider: str, model: str) -> str:
    """Legacy wrapper — use LLMService.get_structured_output_method() instead."""
    return LLMService.get_structured_output_method(provider, model)


def init_llm(provider, model, temperature=0.3, api_key=None, base_url=None):
    """Legacy wrapper — use LLMService instead."""
    svc = LLMService(
        provider=provider, model=model, temperature=temperature,
        api_key=api_key, base_url=base_url,
    )
    return svc.llm


def run_workflow(
    requirements_path, provider, model, temperature,
    max_retries=2, api_key=None, base_url=None,
):
    """Legacy wrapper — use PipelineService.run_workflow() instead."""
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv()

    llm_svc = LLMService(
        provider=provider, model=model, temperature=temperature,
        api_key=api_key, base_url=base_url,
    )
    art_svc = ArtifactService()
    pipeline = PipelineService(llm_svc, art_svc)
    return pipeline.run_workflow(Path(requirements_path), max_retries=max_retries)


def main():
    """Legacy entry point — delegates to cli.main()."""
    from cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
