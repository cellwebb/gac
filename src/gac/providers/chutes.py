"""Chutes.ai API provider for gac."""

import os

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class ChutesProvider(OpenAICompatibleProvider):
    """Chutes.ai OpenAI-compatible provider with custom base URL."""

    config = ProviderConfig(
        name="Chutes",
        api_key_env="CHUTES_API_KEY",
        base_url="",  # Will be set in __init__
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with base URL from environment or default."""
        base_url = os.getenv("CHUTES_BASE_URL", "https://llm.chutes.ai")
        config.base_url = f"{base_url.rstrip('/')}/v1/chat/completions"
        super().__init__(config)


def _get_chutes_provider() -> ChutesProvider:
    """Lazy getter to initialize provider at call time."""
    return ChutesProvider(ChutesProvider.config)


@handle_provider_errors("Chutes")
def call_chutes_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Chutes.ai API directly.

    Chutes.ai provides an OpenAI-compatible API for serverless, decentralized AI compute.

    Args:
        model: The model to use (e.g., 'deepseek-ai/DeepSeek-V3-0324')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    provider = _get_chutes_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
