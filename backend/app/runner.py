"""DDD Pipeline Runner.

Orchestrates the 5-phase DDD artifact generation pipeline using LCEL chains.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_ollama import ChatOllama

# Import structured output models
from models.glossary import GlossaryArtifact


@dataclass
class Phase:
    """Represents a DDD modeling phase with dependencies."""
    id: str
    name: str
    inputs: list[str]
    output_key: str
    output_schema: Optional[type[BaseModel]] = None  # Pydantic model for structured output

    @property
    def prompt_file(self) -> str:
        return f"{self.id}.txt"

    @property
    def is_structured(self) -> bool:
        """Whether this phase uses structured (JSON) output."""
        return self.output_schema is not None


# Phase registry with structured output schemas where applicable
PHASES = [
    Phase("01_glossary", "Glossary", ["requirements"], "glossary", output_schema=GlossaryArtifact),
    Phase("02_event_storming", "Event Storming", ["glossary", "requirements"], "events"),
    Phase("03_bounded_contexts", "Bounded Contexts", ["glossary", "events", "requirements"], "bounded_contexts"),
    Phase("04_aggregates", "Aggregates", ["glossary", "events", "bounded_contexts"], "aggregates"),
    Phase("05_architecture", "Architecture", ["bounded_contexts", "aggregates"], "architecture"),
]


@dataclass
class WorkflowState:
    """Maintains state across workflow execution."""
    domain: str
    provider: str
    model: str
    requirements_path: Path
    artifacts: Dict[str, Union[str, BaseModel]] = field(default_factory=dict)

    def get_artifact(self, key: str) -> str:
        """Get artifact by key as string (serializes structured artifacts to JSON)."""
        artifact = self.artifacts.get(key)
        if artifact is None:
            return ""
        if isinstance(artifact, BaseModel):
            # Serialize Pydantic model to formatted JSON for downstream phases
            return artifact.model_dump_json(indent=2)
        return artifact


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = DATA_DIR / "prompts"
REQUIREMENTS_DIR = DATA_DIR / "requirements"


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)


def derive_domain_name(requirements_path: Path) -> str:
    # Use filename (lowercase, no extension) as domain identifier
    return requirements_path.stem.lower()


def ensure_prompts_present():
    """Verify all required prompt templates exist."""
    missing = []
    for phase in PHASES:
        p = PROMPTS_DIR / phase.prompt_file
        if not p.exists():
            missing.append(p)
    if missing:
        print("The following prompt templates are missing:")
        for p in missing:
            print(f" - {p}")
        print("\nPlease add the bachelor's prompts to these files and rerun.")
        sys.exit(1)


def init_llm(model: str, base_url: str, temperature: float = 0.5):
    """Initialize a local, free chat model via Ollama with retry logic."""
    try:
        llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=4096,  # Max tokens for response
        )
        # Smoke test with a tiny prompt to catch connection issues early
        test_chain = llm | StrOutputParser()
        _ = test_chain.invoke("ok")
        return llm
    except Exception as e:
        print("\nFailed to connect to Ollama.\n")
        print(f"\nDetails: {e}\n")
        sys.exit(1)


def save_output(
        domain: str,
        provider: str,
        phase: Phase,
        content: Union[str, BaseModel]
) -> Path:
    """
    Save phase output to disk with timestamp.
    """
    out_dir = OUTPUT_DIR / domain / provider
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if isinstance(content, BaseModel):
        # Structured output: save JSON + schema
        out_path = out_dir / f"{phase.id}_{ts}.json"
        json_content = content.model_dump_json(indent=2)
        out_path.write_text(json_content, encoding="utf-8")
        print(f"✓ Saved: {out_path}")

        # Also save the schema for reproducibility and validation
        schema_path = out_dir / f"{phase.id}_{ts}.schema.json"
        schema_json = json.dumps(content.model_json_schema(), indent=2)
        schema_path.write_text(schema_json, encoding="utf-8")
        print(f"✓ Schema: {schema_path}")
    else:
        # Text output: save as .txt
        out_path = out_dir / f"{phase.id}_{ts}.txt"
        out_path.write_text(content, encoding="utf-8")
        print(f"✓ Saved: {out_path}")

    return out_path


def build_context_func(phase: Phase, state: WorkflowState):
    """Create a context builder function for a phase."""

    def build_context(_: Any) -> Dict[str, str]:
        """Build phase-specific context from workflow state."""
        ctx = {}
        for inp in phase.inputs:
            if inp == "requirements":
                ctx["requirements"] = read_file(state.requirements_path)
            else:
                ctx[inp] = state.get_artifact(inp)
        return ctx

    return build_context


def build_phase_chain(llm, phase: Phase, state: WorkflowState) -> RunnableSerializable:
    """
    Build a LangChain LCEL chain for a single phase.
    Uses RunnablePassthrough to cleanly inject context into the prompt.
    """
    template_path = PROMPTS_DIR / phase.prompt_file
    template_text = read_file(template_path)
    prompt = PromptTemplate.from_template(template_text)

    build_context = build_context_func(phase, state)

    # LCEL chain: context builder -> prompt -> LLM -> string parser
    chain = (
            RunnablePassthrough()
            | build_context
            | prompt
            | llm
            | StrOutputParser()
    )

    return chain


def build_structured_phase_chain(
        llm,
        phase: Phase,
        state: WorkflowState
) -> RunnableSerializable:
    template_path = PROMPTS_DIR / phase.prompt_file
    template_text = read_file(template_path)
    prompt = PromptTemplate.from_template(template_text)

    build_context = build_context_func(phase, state)

    # Create structured LLM with JSON schema enforcement
    # method="json_schema" uses the model's native JSON mode with schema validation
    structured_llm = llm.with_structured_output(
        phase.output_schema,
        method="json_schema",
        include_raw=False,
    )

    # LCEL chain: context builder -> prompt -> structured LLM (returns Pydantic model)
    chain = (
            RunnablePassthrough()
            | build_context
            | prompt
            | structured_llm
    )

    return chain


def run_phase(llm, phase: Phase, state: WorkflowState) -> Union[str, BaseModel]:
    """
    Execute a single phase using LangChain composition.
    """
    output_type = "structured" if phase.is_structured else "text"
    print(f"--- Running {phase.name} ({phase.id}) [{output_type}] ---")

    try:
        if phase.is_structured:
            chain = build_structured_phase_chain(llm, phase, state)
            output = chain.invoke({})

            if output is None:
                raise ValueError(f"Phase {phase.id} produced None output")

            # Validate we got the expected type
            if not isinstance(output, phase.output_schema):
                raise ValueError(
                    f"Phase {phase.id} returned {type(output).__name__}, "
                    f"expected {phase.output_schema.__name__}"
                )

            print(f"✓ Parsed {len(output.terms)} terms" if hasattr(output, 'terms') else "✓ Parsed")
            return output
        else:
            chain = build_phase_chain(llm, phase, state)
            output = chain.invoke({})

            if not output or not output.strip():
                raise ValueError(f"Phase {phase.id} produced empty output")

            return output

    except Exception as e:
        print(f"✗ Phase {phase.id} failed: {e}")
        # For baseline, we'll continue with error marker rather than crash
        # This allows partial workflow completion for analysis
        if phase.is_structured:
            # Return a minimal valid artifact with error note
            return phase.output_schema.model_construct(
                terms=[],
                schema_version="1.0",
                clarification_questions=[f"[ERROR: {str(e)}]"]
            )
        return f"[ERROR: Phase {phase.id} failed - {str(e)}]"


def run_workflow(requirements_path: Path, model: str, base_url: str, temperature: float):
    """Execute the complete DDD workflow pipeline."""
    ensure_prompts_present()

    domain = derive_domain_name(requirements_path)
    provider = "ollama"

    llm = init_llm(model=model, base_url=base_url, temperature=temperature)

    # Initialize workflow state
    state = WorkflowState(
        domain=domain,
        provider=provider,
        model=model,
        requirements_path=requirements_path,
    )

    print("\n=== Baseline DDD Workflow (Structured + Text) ===")
    print(f"Domain       : {domain}")
    print(f"Provider     : {provider}")
    print(f"Model        : {model}")
    print(f"Temperature  : {temperature}")
    print(f"Requirements : {requirements_path}")
    print("=================================================\n")

    # Execute phases sequentially
    for i, phase in enumerate(PHASES, 1):
        print(f"[{i}/{len(PHASES)}] ", end="")

        output = run_phase(llm, phase, state)

        # Store output in state for subsequent phases
        state.artifacts[phase.output_key] = output

        # Persist to disk
        save_output(domain, provider, phase, output)
        print()  # Blank line between phases

    print("Workflow complete.\n")

    # Summary: count successful phases
    def is_successful(artifact: Union[str, BaseModel]) -> bool:
        if isinstance(artifact, BaseModel):
            # Check if it's an error artifact (has error in clarification_questions)
            if hasattr(artifact, 'clarification_questions'):
                return not any('[ERROR' in q for q in artifact.clarification_questions)
            return True
        return not str(artifact).startswith("[ERROR")

    successful = sum(1 for v in state.artifacts.values() if is_successful(v))
    print(f"Summary: {successful}/{len(PHASES)} phases completed successfully")

    return state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run baseline DDD workflow (text-based).")
    parser.add_argument(
        "--requirements",
        type=str,
        default=str(REQUIREMENTS_DIR / "SecuRooms.txt"),
        help="Path to requirements text file (default: SecuRooms.txt)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.2",
        help="Ollama model name (default: llama3.2)",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.5,
        help="LLM temperature for generation (default: 0.0 for deterministic)",
    )

    args = parser.parse_args()
    req_path = Path(args.requirements)

    run_workflow(
        requirements_path=req_path,
        model=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
    )
