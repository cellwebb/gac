"""Custom Anthropic-compatible API provider for gac.

This provider allows users to specify a custom Anthropic-compatible endpoint
while using the same model capabilities as the standard Anthropic provider.
"""

import json
import logging
import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors

logger = logging.getLogger(__name__)


class CustomAnthropicProvider(AnthropicCompatibleProvider):
    """Custom Anthropic-compatible provider with configurable endpoint and version."""

    def __init__(self, config: ProviderConfig):
        """Initialize the provider with custom configuration from environment variables.

        Environment variables:
            CUSTOM_ANTHROPIC_API_KEY: API key for authentication (required)
            CUSTOM_ANTHROPIC_BASE_URL: Base URL for the API endpoint (required)
            CUSTOM_ANTHROPIC_VERSION: API version header (optional, defaults to '2023-06-01')
        """
        # Get base_url from environment and normalize it
        base_url = os.getenv("CUSTOM_ANTHROPIC_BASE_URL")
        if not base_url:
            raise AIError.model_error("CUSTOM_ANTHROPIC_BASE_URL environment variable not set")

        base_url = base_url.rstrip("/")
        if base_url.endswith("/messages"):
            pass  # Already a complete endpoint URL
        elif base_url.endswith("/v1"):
            base_url = f"{base_url}/messages"
        else:
            base_url = f"{base_url}/v1/messages"

        # Update config with the custom base URL
        config.base_url = base_url

        # Store the custom version for use in headers
        self.custom_version = os.getenv("CUSTOM_ANTHROPIC_VERSION", "2023-06-01")

        super().__init__(config)

    def _build_headers(self) -> dict[str, str]:
        """Build headers with custom Anthropic version."""
        headers = super()._build_headers()
        headers["anthropic-version"] = self.custom_version
        return headers

    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse response with support for extended format (e.g., MiniMax with thinking).

        Handles both:
        - Standard Anthropic format: content[0].text
        - Extended format: first item with type="text"
        """
        try:
            content_list = response.get("content", [])
            if not content_list:
                raise AIError.model_error("Custom Anthropic API returned empty content array")

            # Try standard Anthropic format first: content[0].text
            if "text" in content_list[0]:
                content = content_list[0]["text"]
            else:
                # Extended format (e.g., MiniMax with thinking): find first item with type="text"
                text_item = next((item for item in content_list if item.get("type") == "text"), None)
                if text_item and "text" in text_item:
                    content = text_item["text"]
                else:
                    logger.error(
                        f"Unexpected response format from Custom Anthropic API. Response: {json.dumps(response)}"
                    )
                    raise AIError.model_error(
                        "Custom Anthropic API returned unexpected format. Expected 'text' field in content array."
                    )

            if content is None:
                raise AIError.model_error("Custom Anthropic API returned null content")
            if content == "":
                raise AIError.model_error("Custom Anthropic API returned empty content")
            return content
        except AIError:
            raise
        except (KeyError, IndexError, TypeError, StopIteration) as e:
            logger.error(f"Unexpected response format from Custom Anthropic API. Response: {json.dumps(response)}")
            raise AIError.model_error(
                f"Custom Anthropic API returned unexpected format. Expected Anthropic-compatible response with "
                f"'content[0].text' or items with type='text', but got: {type(e).__name__}. "
                f"Check logs for full response structure."
            ) from e


def _get_custom_anthropic_provider() -> CustomAnthropicProvider:
    """Get or create the Custom Anthropic provider instance (lazy initialization)."""
    return CustomAnthropicProvider(
        ProviderConfig(
            name="Custom Anthropic",
            api_key_env="CUSTOM_ANTHROPIC_API_KEY",
            base_url="",  # Will be set by __init__
        )
    )


@handle_provider_errors("Custom Anthropic")
def call_custom_anthropic_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call a custom Anthropic-compatible API endpoint.

    This provider is useful for:
    - Anthropic-compatible proxies or gateways
    - Self-hosted Anthropic-compatible services
    - Other services implementing the Anthropic Messages API

    Environment variables:
        CUSTOM_ANTHROPIC_API_KEY: API key for authentication (required)
        CUSTOM_ANTHROPIC_BASE_URL: Base URL for the API endpoint (required)
            Example: https://your-proxy.example.com
        CUSTOM_ANTHROPIC_VERSION: API version header (optional, defaults to '2023-06-01')

    Args:
        model: The model to use (e.g., 'claude-sonnet-4-5', 'claude-haiku-4-5')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    provider = _get_custom_anthropic_provider()
    return provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
