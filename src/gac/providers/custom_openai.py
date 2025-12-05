"""Custom OpenAI-compatible API provider for gac.

This provider allows users to specify a custom OpenAI-compatible endpoint
while using the same model capabilities as the standard OpenAI provider.
"""

import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class CustomOpenAIProvider(OpenAICompatibleProvider):
    """Custom OpenAI-compatible provider with configurable base URL."""

    config = ProviderConfig(
        name="Custom OpenAI",
        api_key_env="CUSTOM_OPENAI_API_KEY",
        base_url="",  # Will be set in __init__
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with base URL from environment."""
        base_url = os.getenv("CUSTOM_OPENAI_BASE_URL")
        if not base_url:
            raise AIError.model_error("CUSTOM_OPENAI_BASE_URL environment variable not set")

        if "/chat/completions" not in base_url:
            base_url = base_url.rstrip("/")
            url = f"{base_url}/chat/completions"
        else:
            url = base_url

        config.base_url = url
        super().__init__(config)

    def _build_request_body(
        self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs
    ) -> dict[str, Any]:
        """Build request body with max_completion_tokens instead of max_tokens."""
        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        data["max_completion_tokens"] = data.pop("max_tokens")
        return data


def _get_custom_openai_provider() -> CustomOpenAIProvider:
    """Lazy getter to initialize provider at call time."""
    return CustomOpenAIProvider(CustomOpenAIProvider.config)


@handle_provider_errors("Custom OpenAI")
def call_custom_openai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call a custom OpenAI-compatible API endpoint.

    This provider is useful for:
    - OpenAI-compatible proxies or gateways
    - Self-hosted OpenAI-compatible services
    - Other services implementing the OpenAI Chat Completions API

    Environment variables:
        CUSTOM_OPENAI_API_KEY: API key for authentication (required)
        CUSTOM_OPENAI_BASE_URL: Base URL for the API endpoint (required)
            Example: https://your-proxy.example.com/v1
            Example: https://your-custom-endpoint.com

    Args:
        model: The model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    provider = _get_custom_openai_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
