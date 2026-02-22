"""
CLI entry point for the DDD pipeline runner.

Thin wrapper that parses command-line arguments and delegates
to PipelineService. All business logic lives in the service layer.

Usage::

    python cli.py --provider openrouter --model openai/gpt-4o
    python cli.py --requirements data/requirements/SecuMails.txt
    python cli.py --help
"""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables BEFORE any LangChain imports.
# This enables LangSmith tracing when LANGCHAIN_TRACING_V2=true is set.
load_dotenv()

from pipeline_config import REQUIREMENTS_DIR  # noqa: E402
from services.llm_service import LLMService  # noqa: E402
from services.artifact_service import ArtifactService  # noqa: E402
from services.pipeline_service import PipelineService  # noqa: E402
from validation import ValidationEngine  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """CLI entry point for the DDD pipeline runner."""
    parser = argparse.ArgumentParser(
        description="Run the DDD artifact generation pipeline with structured outputs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default=str(REQUIREMENTS_DIR / "SecuRooms.txt"),
        help="Path to requirements text file",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="ollama",
        choices=["ollama", "openrouter"],
        help="LLM provider: 'ollama' for local models, 'openrouter' for cloud models",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2",
        help=(
            "Model name. "
            "Ollama: 'llama3.2', 'mistral', etc. "
            "OpenRouter: 'openai/gpt-4o', 'anthropic/claude-sonnet-4-20250514', "
            "'google/gemini-2.5-flash', etc."
        ),
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for OpenRouter (overrides OPENROUTER_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Ollama server URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="LLM temperature (lower = more deterministic)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Maximum retries per phase on failure",
    )

    args = parser.parse_args()

    try:
        # Initialize services via dependency injection
        llm_service = LLMService(
            provider=args.provider,
            model=args.model,
            temperature=args.temperature,
            api_key=args.api_key,
            base_url=args.base_url,
        )

        artifact_service = ArtifactService()
        validation_engine = ValidationEngine()

        pipeline = PipelineService(
            llm_service=llm_service,
            artifact_service=artifact_service,
            validation_engine=validation_engine,
        )

        pipeline.run_workflow(
            requirements_path=Path(args.requirements),
            max_retries=args.max_retries,
        )
    except (ValueError, FileNotFoundError, ConnectionError) as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
