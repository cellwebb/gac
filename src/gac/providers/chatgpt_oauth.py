"""ChatGPT OAuth API provider for gac.

This provider allows users with ChatGPT subscriptions to use their OAuth tokens
to access the Codex API (chatgpt.com/backend-api/codex) instead of paying for
the OpenAI API.
"""

import logging
from typing import Any

from gac.errors import AIError
from gac.oauth.chatgpt import (
    CHATGPT_OAUTH_CONFIG,
    load_stored_token,
    load_stored_tokens,
    refresh_token_if_expired,
)
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig

logger = logging.getLogger(__name__)


class ChatGPTOAuthProvider(OpenAICompatibleProvider):
    """ChatGPT OAuth provider for Codex API access."""

    config = ProviderConfig(
        name="ChatGPT OAuth",
        api_key_env="CHATGPT_OAUTH_API_KEY",
        base_url="https://chatgpt.com/backend-api/codex",
    )

    def _get_api_key(self) -> str:
        """Get OAuth token from token store, refreshing if needed."""
        if not refresh_token_if_expired(quiet=True):
            raise AIError.authentication_error(
                "ChatGPT OAuth token not found or expired. Run 'gac auth chatgpt login' to authenticate."
            )

        token = load_stored_token()
        if token:
            return token

        raise AIError.authentication_error(
            "ChatGPT OAuth authentication not found. Run 'gac auth chatgpt login' to authenticate."
        )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Codex API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth Bearer token and Codex-specific headers."""
        headers = super()._build_headers()
        # Replace the standard API key header with Bearer token
        if "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.api_key}"
        # Remove x-api-key if present (OpenAI compat adds it)
        headers.pop("x-api-key", None)

        # Add Codex-specific headers from stored extra metadata
        tokens = load_stored_tokens()
        account_id = tokens.get("account_id", "") if tokens else ""

        originator = CHATGPT_OAUTH_CONFIG.get("originator", "codex_cli_rs")
        client_version = CHATGPT_OAUTH_CONFIG.get("client_version", "0.72.0")

        if account_id:
            headers["ChatGPT-Account-Id"] = account_id
        headers["originator"] = originator
        headers["User-Agent"] = f"{originator}/{client_version}"

        return headers

    def _build_request_body(
        self,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build Codex API request body.

        The Codex API uses the same format as OpenAI's chat completions,
        but with max_completion_tokens instead of max_tokens.
        """
        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        # Codex API uses max_completion_tokens
        if "max_tokens" in data:
            data["max_completion_tokens"] = data.pop("max_tokens")
        return data
