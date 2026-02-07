"""Pluggable LLM provider factory for recipe extraction."""

import os

from .base import RecipeProvider

_provider: RecipeProvider | None = None


def get_provider() -> RecipeProvider:
    """Get the configured LLM provider (cached singleton).

    Reads LLM_PROVIDER and LLM_MODEL from environment variables.
    Defaults to Gemini if LLM_PROVIDER is not set.
    """
    global _provider
    if _provider is not None:
        return _provider

    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("LLM_MODEL") or None

    if provider_name == "gemini":
        from .gemini import GeminiProvider

        _provider = GeminiProvider(model=model)
    elif provider_name == "openai":
        try:
            from .openai import OpenAIProvider
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for the OpenAI provider. "
                'Install with: pip install "uncluttered[openai]"'
            ) from None
        _provider = OpenAIProvider(model=model)
    elif provider_name == "anthropic":
        try:
            from .anthropic import AnthropicProvider
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for the Anthropic provider. "
                'Install with: pip install "uncluttered[anthropic]"'
            ) from None
        _provider = AnthropicProvider(model=model)
    elif provider_name == "ollama":
        try:
            from .ollama import OllamaProvider
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for the Ollama provider. "
                'Install with: pip install "uncluttered[ollama]"'
            ) from None
        _provider = OllamaProvider(model=model)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider_name}'. "
            f"Must be one of: gemini, openai, anthropic, ollama"
        )

    return _provider
