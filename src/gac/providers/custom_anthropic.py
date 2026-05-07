"""Custom Anthropic-compatible API provider for gac.

This provider allows users to specify a custom Anthropic-compatible endpoint
while using the same model capabilities as the standard Anthropic provider.
"""

import json
import logging
import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import AnthropicCompatibleProvider, ParsedResponse, ProviderConfig, _normalize_completion_tokens

logger = logging.getLogger(__name__)


class CustomAnthropicProvider(AnthropicCompatibleProvider):
    """Custom Anthropic-compatible provider with configurable endpoint and version."""

    config = ProviderConfig(
        name="Custom Anthropic",
        api_key_env="CUSTOM_ANTHROPIC_API_KEY",
        base_url="",  # Will be set in __init__ from environment
    )

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

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse response with support for extended format (e.g., MiniMax with thinking).

        Handles both:
        - Standard Anthropic format: content[0].text
        - Extended format: first item with type="text"
        """
        from gac.ai_utils import normalize_reasoning_tokens

        try:
            usage = response.get("usage")
            prompt_tokens = -1
            completion_tokens = -1
            reasoning_tokens: int | None = None  # None = not reported by API
            if isinstance(usage, dict):
                pt = usage.get("input_tokens", -1)
                ct = usage.get("output_tokens", -1)
                prompt_tokens = pt if isinstance(pt, int) else -1
                completion_tokens = ct if isinstance(ct, int) else -1

            content_list = response.get("content", [])
            if not content_list:
                raise AIError.model_error("Custom Anthropic API returned empty content array")

            if isinstance(content_list[0], dict) and "text" in content_list[0]:
                content = content_list[0]["text"]
            else:
                text_item = next(
                    (item for item in content_list if isinstance(item, dict) and item.get("type") == "text"),
                    None,
                )
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

            # Collect thinking text for reasoning token estimation.
            thinking_text = "\n".join(
                block.get("thinking", "")
                for block in content_list
                if isinstance(block, dict) and block.get("type") == "thinking"
            )
            reasoning_tokens = normalize_reasoning_tokens(reasoning_tokens, thinking_text)

            return ParsedResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=_normalize_completion_tokens(completion_tokens, reasoning_tokens),
                reasoning_tokens=reasoning_tokens,
            )
        except AIError:
            raise
        except (KeyError, IndexError, TypeError, StopIteration) as e:
            logger.error(f"Unexpected response format from Custom Anthropic API. Response: {json.dumps(response)}")
            raise AIError.model_error(
                f"Custom Anthropic API returned unexpected format. Expected Anthropic-compatible response with "
                f"'content[0].text' or items with type='text', but got: {type(e).__name__}. "
                f"Check logs for full response structure."
            ) from e
