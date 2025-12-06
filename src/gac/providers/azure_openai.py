"""Azure OpenAI provider for gac.

This provider provides native support for Azure OpenAI Service with proper
endpoint construction and API version handling.
"""

import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class AzureOpenAIProvider(OpenAICompatibleProvider):
    """Azure OpenAI-compatible provider with custom URL construction and headers."""

    config = ProviderConfig(
        name="Azure OpenAI",
        api_key_env="AZURE_OPENAI_API_KEY",
        base_url="",  # Will be set in __init__
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with Azure-specific endpoint and API version."""
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise AIError.model_error("AZURE_OPENAI_ENDPOINT environment variable not set")

        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        if not api_version:
            raise AIError.model_error("AZURE_OPENAI_API_VERSION environment variable not set")

        self.api_version = api_version
        self.endpoint = endpoint.rstrip("/")
        config.base_url = ""  # Will be set dynamically in _get_api_url
        super().__init__(config)

    def _get_api_url(self, model: str | None = None) -> str:
        """Build Azure-specific URL with deployment name and API version."""
        if model is None:
            return super()._get_api_url(model)
        return f"{self.endpoint}/openai/deployments/{model}/chat/completions?api-version={self.api_version}"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with api-key instead of Bearer token."""
        headers = super()._build_headers()
        # Replace Bearer token with api-key
        if "Authorization" in headers:
            del headers["Authorization"]
        headers["api-key"] = self.api_key
        return headers

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build request body for Azure OpenAI."""
        return {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}
