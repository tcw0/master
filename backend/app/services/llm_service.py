"""
LLM Service — Provider management and model initialization.

Handles:
- Provider detection (Ollama, OpenRouter)
- Model family detection for structured output method selection
- LLM instance creation with provider-specific configuration

Design principles:
- Raises exceptions instead of sys.exit() — callers decide how to handle errors
- Lazy initialization — LLM is created on first access
- Stateless static helpers for model detection (usable without instantiation)
"""

import logging
import os

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# =============================================================================
# Provider Constants
# =============================================================================

PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENROUTER = "openrouter"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_HEADERS = {
    "HTTP-Referer": "http://localhost",
    "X-Title": "DDD Pipeline Runner",
}


class LLMService:
    """
    Manages LLM provider configuration and initialization.

    Supports:
    - ollama: Local Ollama instance (requires running Ollama server)
    - openrouter: Cloud models via OpenRouter (OpenAI, Claude, Gemini, etc.)

    Usage::

        llm_service = LLMService(provider="openrouter", model="openai/gpt-4o")
        llm = llm_service.llm  # lazily initialized
        method = llm_service.structured_output_method  # 'json_schema'
    """

    def __init__(
        self,
        provider: str,
        model: str,
        temperature: float = 0.3,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.base_url = base_url
        self._llm: BaseChatModel | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def llm(self) -> BaseChatModel:
        """Lazily initialize and return the LLM instance."""
        if self._llm is None:
            self._llm = self._init_llm()
        return self._llm

    @property
    def model_family(self) -> str:
        """Detect model family from the configured model name."""
        return self.detect_model_family(self.model)

    @property
    def structured_output_method(self) -> str:
        """Select the optimal structured output enforcement method."""
        return self.get_structured_output_method(self.provider, self.model)

    # ------------------------------------------------------------------
    # Static helpers (usable without instantiation)
    # ------------------------------------------------------------------

    @staticmethod
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
            if prefix in (
                "openai", "anthropic", "google",
                "meta-llama", "mistralai", "deepseek",
            ):
                return prefix
        # Fallback heuristics for bare model names
        if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
            return "openai"
        if "claude" in model_lower:
            return "anthropic"
        if "gemini" in model_lower:
            return "google"
        return "unknown"

    @staticmethod
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
        family = LLMService.detect_model_family(model)
        if family == "openai":
            return "json_schema"
        # Claude, Gemini, and others: function calling via OpenRouter
        return "json_schema"

    # ------------------------------------------------------------------
    # Private initialization methods
    # ------------------------------------------------------------------

    def _init_llm(self) -> BaseChatModel:
        """Initialize LLM based on provider selection."""
        if self.provider == PROVIDER_OLLAMA:
            return self._init_ollama()
        elif self.provider == PROVIDER_OPENROUTER:
            return self._init_openrouter()
        else:
            raise ValueError(
                f"Unknown provider: '{self.provider}'. "
                f"Supported: '{PROVIDER_OLLAMA}', '{PROVIDER_OPENROUTER}'."
            )

    def _init_ollama(self, num_predict: int = 8192) -> ChatOllama:
        """
        Initialize local Ollama LLM with connection validation.

        Args:
            num_predict: Maximum tokens for response.

        Raises:
            ConnectionError: If Ollama server is unreachable.
        """
        url = self.base_url or "http://localhost:11434"
        try:
            llm = ChatOllama(
                model=self.model,
                base_url=url,
                temperature=self.temperature,
                num_predict=num_predict,
            )
            # Validate connection with minimal request
            test_chain = llm | StrOutputParser()
            _ = test_chain.invoke("ping")
            logger.info(f"Connected to Ollama: {self.model} @ {url}")
            return llm
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}") from e

    def _init_openrouter(self, max_tokens: int = 16384) -> ChatOpenAI:
        """
        Initialize OpenRouter LLM via OpenAI-compatible API.

        Args:
            max_tokens: Maximum tokens for response.

        Raises:
            ValueError: If no API key is available.
            ConnectionError: If the provider fails to initialize.
        """
        resolved_key = self.api_key or os.getenv("OPENROUTER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY in your .env file or pass api_key."
            )

        try:
            llm = ChatOpenAI(
                model=self.model,
                api_key=resolved_key,
                base_url=OPENROUTER_BASE_URL,
                temperature=self.temperature,
                max_tokens=max_tokens,
                default_headers=OPENROUTER_DEFAULT_HEADERS,
            )
            logger.info(
                f"Initialized OpenRouter: {self.model} "
                f"(family={self.model_family}, "
                f"structured_output={self.structured_output_method})"
            )
            return llm
        except Exception as e:
            raise ConnectionError(
                f"Failed to initialize OpenRouter: {e}"
            ) from e
