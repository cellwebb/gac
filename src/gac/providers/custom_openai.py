"""Custom OpenAI-compatible API provider for gac.

This provider allows users to specify a custom OpenAI-compatible endpoint
while using the same model capabilities as the standard OpenAI provider.
"""

import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


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
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build request body with max_completion_tokens instead of max_tokens."""
        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        data["max_completion_tokens"] = data.pop("max_tokens")
        return data
