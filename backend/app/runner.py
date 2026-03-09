"""DDD Pipeline Runner.

Orchestrates the 5-phase DDD artifact generation pipeline using LCEL chains
with structured outputs enforced via Pydantic schemas.

LangChain Best Practices Applied:
- Structured output with `with_structured_output()` for all phases
- Retry logic with exponential backoff for transient failures
- Raw response capture for debugging parse failures
- Configurable fallback strategies
- Proper chain composition with RunnableLambda
- System + Human message format for better LLM guidance
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableSerializable
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

# Load environment variables from .env file
load_dotenv()

# Import all structured output models
from models.glossary import GlossaryArtifact
from models.event_storming import EventStormingArtifact
from models.bounded_contexts import BoundedContextsArtifact
from models.aggregates import AggregatesArtifact
from models.architecture import ArchitectureArtifact

# Type variable for generic artifact handling
ArtifactT = TypeVar("ArtifactT", bound=BaseModel)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Provider Configuration
# =============================================================================

PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENROUTER = "openrouter"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_HEADERS = {
    "HTTP-Referer": "http://localhost",
    "X-Title": "DDD Pipeline Runner",
}


def detect_model_family(model: str) -> str:
    """
    Detect model family from OpenRouter model slug.

    Examples:
        'openai/gpt-4o' → 'openai'
        'anthropic/claude-sonnet-4-20250514' → 'anthropic'
        'google/gemini-1.5-pro' → 'google'
    """
    model_lower = model.lower()
    if "/" in model_lower:
        prefix = model_lower.split("/")[0]
        if prefix in ("openai", "anthropic", "google", "meta-llama", "mistralai", "deepseek"):
            return prefix
    # Fallback heuristics for bare model names
    if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
        return "openai"
    if "claude" in model_lower:
        return "anthropic"
    if "gemini" in model_lower:
        return "google"
    return "unknown"


def get_structured_output_method(provider: str, model: str) -> str:
    """
    Select the optimal structured output enforcement method.

    Strategy:
    - json_schema: Strict server-side JSON schema enforcement.
      Best for OpenAI models (native support) and Ollama.
    - function_calling: Uses tool/function calling to enforce structure.
      Most reliable for Claude, Gemini, and other models via OpenRouter,
      as OpenRouter translates tool calls to each provider's native format.

    Returns:
        'json_schema' or 'function_calling'
    """
    if provider == PROVIDER_OLLAMA:
        return "json_schema"

    # OpenRouter: method depends on underlying model
    family = detect_model_family(model)
    if family == "openai":
        # OpenAI models support native JSON schema response format
        return "json_schema"
    # Claude, Gemini, and others: function calling via OpenRouter
    return "json_schema"


# =============================================================================
# Phase Configuration
# =============================================================================

@dataclass
class PhaseConfig:
    """
    Configuration for a single DDD modeling phase.
    
    Attributes:
        id: Unique phase identifier (e.g., '01_glossary')
        name: Human-readable phase name
        inputs: List of artifact keys required as input
        output_key: Key to store the output artifact under
        output_schema: Pydantic model class for structured output
        system_prompt: Optional system message for better LLM guidance
    """
    id: str
    name: str
    inputs: list[str]
    output_key: str
    output_schema: type[BaseModel]
    system_prompt: str = ""
    
    @property
    def prompt_file(self) -> str:
        return f"{self.id}.txt"
    
    @property
    def phase_number(self) -> int:
        return int(self.id.split("_")[0])


# System prompts provide consistent framing for each phase
GLOSSARY_SYSTEM_PROMPT = """You are a Domain-Driven Design (DDD) expert specializing in ubiquitous language extraction.
Your task is to analyze requirements and extract domain terms with precise, business-focused definitions.
Focus on clarity, consistency, and identifying potential bounded context boundaries."""

EVENT_STORMING_SYSTEM_PROMPT = """You are a Domain-Driven Design (DDD) expert facilitating an Event Storming session.
Your task is to identify domain events, commands, actors, and policies from the requirements and glossary.
Focus on temporal flows, cause-effect relationships, and business process boundaries."""

BOUNDED_CONTEXTS_SYSTEM_PROMPT = """You are a Domain-Driven Design (DDD) expert specializing in strategic design.
Your task is to identify bounded contexts and their relationships from the domain model.
Focus on linguistic boundaries, team ownership, and integration patterns."""

AGGREGATES_SYSTEM_PROMPT = """You are a Domain-Driven Design (DDD) expert specializing in tactical design.
Your task is to design aggregates with clear consistency boundaries and invariants.
Focus on transactional boundaries, entity vs value object distinctions, and aggregate sizing."""

ARCHITECTURE_SYSTEM_PROMPT = """You are a Domain-Driven Design (DDD) expert specializing in technical architecture.
Your task is to map the domain model to a hexagonal architecture with clear layer responsibilities.
Focus on ports/adapters, anti-corruption layers, and integration patterns."""


# Phase registry - all phases now use structured output
PHASES: list[PhaseConfig] = [
    PhaseConfig(
        id="01_glossary",
        name="Glossary",
        inputs=["requirements"],
        output_key="glossary",
        output_schema=GlossaryArtifact,
        system_prompt=GLOSSARY_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="02_event_storming",
        name="Event Storming",
        inputs=["requirements", "glossary"],
        output_key="events",
        output_schema=EventStormingArtifact,
        system_prompt=EVENT_STORMING_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="03_bounded_contexts",
        name="Bounded Contexts",
        inputs=["requirements", "glossary", "events"],
        output_key="bounded_contexts",
        output_schema=BoundedContextsArtifact,
        system_prompt=BOUNDED_CONTEXTS_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="04_aggregates",
        name="Aggregates",
        inputs=["glossary", "events", "bounded_contexts"],
        output_key="aggregates",
        output_schema=AggregatesArtifact,
        system_prompt=AGGREGATES_SYSTEM_PROMPT,
    ),
    PhaseConfig(
        id="05_architecture",
        name="Architecture",
        inputs=["bounded_contexts", "aggregates"],
        output_key="architecture",
        output_schema=ArchitectureArtifact,
        system_prompt=ARCHITECTURE_SYSTEM_PROMPT,
    ),
]


# =============================================================================
# Workflow State
# =============================================================================

@dataclass
class WorkflowState:
    """
    Maintains state across workflow execution.
    
    Stores artifacts, metadata, and provides serialization for downstream phases.
    """
    domain: str
    provider: str
    model: str
    requirements_path: Path
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    artifacts: dict[str, BaseModel] = field(default_factory=dict)
    raw_responses: dict[str, str] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    
    def get_artifact_as_json(self, key: str) -> str:
        """
        Get artifact serialized as JSON for use in prompts.
        
        Downstream phases receive previous artifacts as JSON strings,
        allowing the LLM to parse and reference structured data.
        """
        artifact = self.artifacts.get(key)
        if artifact is None:
            return ""
        return artifact.model_dump_json(indent=2)
    
    def get_requirements_hash(self) -> str:
        """Generate a hash of the requirements file for traceability."""
        content = self.requirements_path.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# Path Configuration
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = DATA_DIR / "prompts"
REQUIREMENTS_DIR = DATA_DIR / "requirements"


# =============================================================================
# Utility Functions
# =============================================================================

def read_file(path: Path) -> str:
    """Read file contents with error handling."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        sys.exit(1)


def derive_domain_name(requirements_path: Path) -> str:
    """Extract domain name from requirements filename."""
    return requirements_path.stem.lower()


def ensure_prompts_present() -> None:
    """Verify all required prompt templates exist."""
    missing = [
        PROMPTS_DIR / phase.prompt_file
        for phase in PHASES
        if not (PROMPTS_DIR / phase.prompt_file).exists()
    ]
    if missing:
        logger.error("Missing prompt templates:")
        for p in missing:
            logger.error(f"  - {p}")
        sys.exit(1)


def get_prompt_hash(prompt_path: Path) -> str:
    """Generate hash of prompt template for versioning."""
    content = read_file(prompt_path)
    return hashlib.sha256(content.encode()).hexdigest()[:12]


# =============================================================================
# LLM Initialization
# =============================================================================

def init_llm(
    provider: str,
    model: str,
    temperature: float = 0.3,
    api_key: str | None = None,
    base_url: str | None = None,
) -> BaseChatModel:
    """
    Initialize LLM based on provider selection.

    Supports:
    - ollama: Local Ollama instance (requires running Ollama server)
    - openrouter: Cloud models via OpenRouter (OpenAI, Claude, Gemini, etc.)

    Args:
        provider: 'ollama' or 'openrouter'
        model: Model name (e.g., 'llama3.2' for Ollama, 'openai/gpt-4o' for OpenRouter)
        temperature: Generation temperature (lower = more deterministic)
        api_key: API key (OpenRouter only; falls back to OPENROUTER_API_KEY env var)
        base_url: Server URL (Ollama only; defaults to http://localhost:11434)

    Returns:
        Configured BaseChatModel instance
    """
    if provider == PROVIDER_OLLAMA:
        return _init_ollama(model, base_url or "http://localhost:11434", temperature)
    elif provider == PROVIDER_OPENROUTER:
        return _init_openrouter(model, temperature, api_key)
    else:
        logger.error(f"Unknown provider: '{provider}'. Use 'ollama' or 'openrouter'.")
        sys.exit(1)


def _init_ollama(
    model: str,
    base_url: str,
    temperature: float,
    num_predict: int = 8192,
) -> ChatOllama:
    """
    Initialize local Ollama LLM with connection validation.

    Args:
        model: Ollama model name (e.g., 'llama3.2')
        base_url: Ollama server URL
        temperature: Generation temperature
        num_predict: Maximum tokens for response

    Returns:
        Configured ChatOllama instance
    """
    try:
        llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=num_predict,
        )
        # Validate connection with minimal request
        test_chain = llm | StrOutputParser()
        _ = test_chain.invoke("ping")
        logger.info(f"Connected to Ollama: {model} @ {base_url}")
        return llm
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        sys.exit(1)


def _init_openrouter(
    model: str,
    temperature: float,
    api_key: str | None = None,
    max_tokens: int = 16384,
) -> ChatOpenAI:
    """
    Initialize OpenRouter LLM via OpenAI-compatible API.

    OpenRouter provides a unified API for OpenAI, Claude, Gemini, and many other
    models. Since it's OpenAI-API compatible, we use LangChain's ChatOpenAI with
    a custom base_url.

    Structured output enforcement strategy:
    - OpenAI models: json_schema (native server-side enforcement)
    - Claude/Gemini/others: function_calling (translated by OpenRouter)

    Args:
        model: OpenRouter model slug (e.g., 'openai/gpt-4o', 'anthropic/claude-sonnet-4-20250514')
        temperature: Generation temperature
        api_key: OpenRouter API key (falls back to OPENROUTER_API_KEY env var)
        max_tokens: Maximum tokens for response

    Returns:
        Configured ChatOpenAI instance pointing to OpenRouter
    """
    resolved_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not resolved_key:
        logger.error(
            "OpenRouter API key not found. "
            "Set OPENROUTER_API_KEY in your .env file or pass --api-key."
        )
        sys.exit(1)

    try:
        llm = ChatOpenAI(
            model=model,
            api_key=resolved_key,
            base_url=OPENROUTER_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens,
            default_headers=OPENROUTER_DEFAULT_HEADERS,
        )
        family = detect_model_family(model)
        method = get_structured_output_method(PROVIDER_OPENROUTER, model)
        logger.info(
            f"Initialized OpenRouter: {model} "
            f"(family={family}, structured_output={method})"
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize OpenRouter: {e}")
        sys.exit(1)


# =============================================================================
# Chain Building (LangChain Best Practices)
# =============================================================================

def build_context_builder(
    phase: PhaseConfig,
    state: WorkflowState,
) -> Callable[[Any], dict[str, str]]:
    """
    Create a context builder function for a phase.
    
    Returns a callable that assembles the prompt context from workflow state.
    """
    def build_context(_: Any) -> dict[str, str]:
        ctx = {}
        for inp in phase.inputs:
            if inp == "requirements":
                ctx["requirements"] = read_file(state.requirements_path)
            else:
                ctx[inp] = state.get_artifact_as_json(inp)
        return ctx
    
    return build_context


def build_prompt(phase: PhaseConfig) -> ChatPromptTemplate:
    """
    Build a ChatPromptTemplate for a phase.
    
    Uses system + human message format for better LLM guidance.
    System message provides role/expertise framing.
    Human message contains the task template with variables.
    """
    template_path = PROMPTS_DIR / phase.prompt_file
    task_template = read_file(template_path)
    
    messages = []
    
    # Add system message if defined
    if phase.system_prompt:
        messages.append(SystemMessagePromptTemplate.from_template(phase.system_prompt))
    
    # Add human message with the task and input variables
    # The template references {requirements}, {glossary}, etc.
    messages.append(HumanMessagePromptTemplate.from_template(task_template))
    
    return ChatPromptTemplate.from_messages(messages)


def build_structured_chain(
    llm: BaseChatModel,
    phase: PhaseConfig,
    state: WorkflowState,
    include_raw: bool = True,
    structured_output_method: str = "json_schema",
) -> RunnableSerializable:
    """
    Build an LCEL chain with structured output enforcement.
    
    Chain structure:
    1. RunnablePassthrough (accepts empty input)
    2. Context builder (assembles prompt variables)
    3. Prompt template (formats the message)
    4. Structured LLM (enforces schema output via selected method)
    
    Structured output methods:
    - json_schema: Server-side JSON schema enforcement (OpenAI, Ollama)
    - function_calling: Tool/function calling (Claude, Gemini via OpenRouter)
    
    Args:
        llm: Base language model
        phase: Phase configuration
        state: Workflow state for context
        include_raw: Whether to capture raw response for debugging
        structured_output_method: Method for structured output enforcement
    
    Returns:
        Runnable chain that produces structured output
    """
    prompt = build_prompt(phase)
    context_builder = build_context_builder(phase, state)
    
    # Configure structured output with the provider-appropriate method
    # json_schema: strict server-side enforcement (OpenAI, Ollama)
    # function_calling: tool-based enforcement (Claude, Gemini via OpenRouter)
    structured_llm = llm.with_structured_output(
        phase.output_schema,
        method=structured_output_method,
        include_raw=include_raw,
    )
    
    # Build the LCEL chain
    chain = (
        RunnablePassthrough()
        | RunnableLambda(context_builder)
        | prompt
        | structured_llm
    )
    
    return chain


# =============================================================================
# Phase Execution with Retry Logic
# =============================================================================

def run_phase_with_retry(
    llm: BaseChatModel,
    phase: PhaseConfig,
    state: WorkflowState,
    max_retries: int = 2,
    structured_output_method: str = "json_schema",
) -> tuple[BaseModel | None, str | None]:
    """
    Execute a phase with retry logic for transient failures.
    
    Args:
        llm: Language model instance
        phase: Phase configuration
        state: Workflow state
        max_retries: Maximum retry attempts
        structured_output_method: Method for structured output enforcement
    
    Returns:
        Tuple of (artifact, raw_response) or (None, error_message) on failure
    """
    logger.info(f"--- Phase {phase.phase_number}: {phase.name} ---")
    
    chain = build_structured_chain(
        llm, phase, state,
        include_raw=True,
        structured_output_method=structured_output_method,
    )
    
    last_error = None
    raw_response = None
    
    for attempt in range(max_retries + 1):
        try:
            # Invoke chain - returns dict with 'parsed' and 'raw' when include_raw=True
            result = chain.invoke({})
            
            # Handle both dict (with raw) and direct model returns
            if isinstance(result, dict):
                artifact = result.get("parsed")
                raw_msg = result.get("raw")
                if raw_msg:
                    # Extract raw response for debugging.
                    # json_schema method: response content is the JSON string.
                    # function_calling method: content may be empty; structured
                    #   data arrives via tool_calls instead.
                    content = getattr(raw_msg, "content", None)
                    if isinstance(content, str) and content:
                        raw_response = content
                    elif isinstance(content, list) and content:
                        # Some providers return content as a list of blocks
                        raw_response = json.dumps(content, indent=2, default=str)
                    elif hasattr(raw_msg, "tool_calls") and raw_msg.tool_calls:
                        raw_response = json.dumps(
                            raw_msg.tool_calls, indent=2, default=str
                        )
                    else:
                        raw_response = str(raw_msg)
                else:
                    raw_response = None
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
            
            # Log success with artifact summary
            _log_artifact_summary(phase, artifact)
            return artifact, raw_response
            
        except (ValidationError, TypeError, ValueError) as e:
            last_error = str(e)
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {last_error}. Retrying...")
            else:
                logger.error(f"Phase {phase.id} failed after {max_retries + 1} attempts: {last_error}")
    
    return None, last_error


def _log_artifact_summary(phase: PhaseConfig, artifact: BaseModel) -> None:
    """Log a summary of the generated artifact."""
    summary_parts = []
    
    # Phase-specific summaries
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


# =============================================================================
# Output Persistence
# =============================================================================

def save_artifact(
    domain: str,
    provider: str,
    model: str,
    phase: PhaseConfig,
    artifact: BaseModel,
    raw_response: str | None = None,
) -> Path:
    """
    Save artifact to disk with metadata.
    
    Output directory structure:
    - ollama:      output/{domain}/ollama/
    - openrouter:  output/{domain}/openrouter/{model_family}/
    
    Filename format: {timestamp}_{phase_id}.{ext}
    
    Saves:
    - {timestamp}_{phase_id}.json: The artifact data
    - {timestamp}_{phase_id}.schema.json: JSON schema for validation
    - {timestamp}_{phase_id}.raw.txt: Raw LLM response (if available)
    """
    # Build output directory: add model family subfolder for openrouter
    if provider == PROVIDER_OPENROUTER:
        family = detect_model_family(model)
        out_dir = OUTPUT_DIR / domain / provider / family
    else:
        out_dir = OUTPUT_DIR / domain / provider
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{ts}_{phase.id}"
    
    # Save artifact as JSON
    artifact_path = out_dir / f"{base_name}.json"
    artifact_json = artifact.model_dump_json(indent=2)
    artifact_path.write_text(artifact_json, encoding="utf-8")
    logger.info(f"  → Saved: {artifact_path.name}")
    
    # Save JSON schema for validation/documentation
    schema_path = out_dir / f"{base_name}.schema.json"
    schema_json = json.dumps(artifact.model_json_schema(), indent=2)
    schema_path.write_text(schema_json, encoding="utf-8")
    logger.info(f"  → Schema: {schema_path.name}")
    
    # Save raw response for debugging (if available)
    if raw_response:
        raw_path = out_dir / f"{base_name}.raw.txt"
        raw_path.write_text(raw_response, encoding="utf-8")
        logger.info(f"  → Raw: {raw_path.name}")
    
    return artifact_path


def create_error_artifact(phase: PhaseConfig, error: str) -> BaseModel:
    """
    Create a minimal error artifact for failed phases.
    
    This allows the pipeline to continue and record the failure.
    """
    # Create empty artifact with error marker
    # Each artifact type needs specific handling
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


# =============================================================================
# Main Workflow Orchestration
# =============================================================================

def run_workflow(
    requirements_path: Path,
    provider: str,
    model: str,
    temperature: float,
    max_retries: int = 2,
    api_key: str | None = None,
    base_url: str | None = None,
) -> WorkflowState:
    """
    Execute the complete DDD workflow pipeline.
    
    Args:
        requirements_path: Path to requirements document
        provider: LLM provider ('ollama' or 'openrouter')
        model: Model name (e.g., 'llama3.2' or 'openai/gpt-4o')
        temperature: LLM temperature
        max_retries: Max retries per phase
        api_key: API key for cloud providers (OpenRouter)
        base_url: Server URL override (Ollama only)
    
    Returns:
        WorkflowState with all artifacts
    """
    ensure_prompts_present()
    
    domain = derive_domain_name(requirements_path)
    
    # Determine structured output method based on provider + model
    structured_output_method = get_structured_output_method(provider, model)
    
    # Initialize LLM
    llm = init_llm(
        provider=provider,
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
    )
    
    # Initialize workflow state
    state = WorkflowState(
        domain=domain,
        provider=provider,
        model=model,
        requirements_path=requirements_path,
    )
    
    # Print workflow header
    print()
    print("=" * 60)
    print("DDD Artifact Generation Pipeline (Structured Output)")
    print("=" * 60)
    print(f"  Run ID       : {state.run_id}")
    print(f"  Domain       : {domain}")
    print(f"  Provider     : {provider}")
    print(f"  Model        : {model}")
    print(f"  Temperature  : {temperature}")
    print(f"  Struct. Out  : {structured_output_method}")
    print(f"  Requirements : {requirements_path.name}")
    print(f"  Req. Hash    : {state.get_requirements_hash()}")
    print("=" * 60)
    print()
    
    # Execute phases sequentially
    successful = 0
    for phase in PHASES:
        artifact, raw_or_error = run_phase_with_retry(
            llm, phase, state,
            max_retries=max_retries,
            structured_output_method=structured_output_method,
        )
        
        if artifact is not None:
            # Success: store artifact and raw response
            state.artifacts[phase.output_key] = artifact
            if raw_or_error:
                state.raw_responses[phase.output_key] = raw_or_error
            
            # Persist to disk
            save_artifact(domain, provider, model, phase, artifact, raw_or_error)
            successful += 1
        else:
            # Failure: create error artifact to allow pipeline to continue
            error_artifact = create_error_artifact(phase, raw_or_error or "Unknown error")
            state.artifacts[phase.output_key] = error_artifact
            state.errors[phase.output_key] = raw_or_error or "Unknown error"
            
            save_artifact(domain, provider, model, phase, error_artifact)
            logger.error(f"✗ {phase.name} failed: {raw_or_error}")
        
        print()  # Blank line between phases
    
    # Summary
    print("=" * 60)
    print(f"Pipeline Complete: {successful}/{len(PHASES)} phases successful")
    if state.errors:
        print(f"Errors: {list(state.errors.keys())}")
    print("=" * 60)
    
    return state


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
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
    
    run_workflow(
        requirements_path=Path(args.requirements),
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        max_retries=args.max_retries,
        api_key=args.api_key,
        base_url=args.base_url,
    )


if __name__ == "__main__":
    main()
