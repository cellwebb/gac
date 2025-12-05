"""Azure OpenAI provider for gac.

This provider provides native support for Azure OpenAI Service with proper
endpoint construction and API version handling.
"""

import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


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
        self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs
    ) -> dict[str, Any]:
        """Build request body for Azure OpenAI."""
        return {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}


def _get_azure_openai_provider() -> AzureOpenAIProvider:
    """Lazy getter to initialize provider at call time."""
    return AzureOpenAIProvider(AzureOpenAIProvider.config)


@handle_provider_errors("Azure OpenAI")
def call_azure_openai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Azure OpenAI Service API.

    Environment variables:
        AZURE_OPENAI_API_KEY: Azure OpenAI API key (required)
        AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL (required)
            Example: https://your-resource.openai.azure.com
        AZURE_OPENAI_API_VERSION: Azure OpenAI API version (required)
            Example: 2025-01-01-preview
            Example: 2024-02-15-preview

    Args:
        model: The deployment name in Azure OpenAI (e.g., 'gpt-4o', 'gpt-35-turbo')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    provider = _get_azure_openai_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
