"""GitHub Copilot API provider for gac.

Uses the Copilot OAuth token obtained via Device Flow to access the Copilot API.
The Copilot API is OpenAI-compatible, so we extend OpenAICompatibleProvider.
"""

import logging

from gac.errors import AIError
from gac.oauth.copilot import (
    COPILOT_OAUTH_CONFIG,
    get_api_endpoint,
    get_valid_session_token,
    load_stored_tokens,
)
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig

logger = logging.getLogger(__name__)


class CopilotProvider(OpenAICompatibleProvider):
    """GitHub Copilot provider — OpenAI-compatible API via Copilot session tokens."""

    config = ProviderConfig(
        name="Copilot",
        api_key_env="COPILOT_OAUTH_TOKEN",
        base_url="https://api.githubcopilot.com",
    )

    def _get_api_key(self) -> str:
        """Get a valid Copilot session token, refreshing if needed."""
        tokens = load_stored_tokens()
        if not tokens:
            raise AIError.authentication_error(
                "Copilot authentication not found. Run 'gac auth copilot login' to authenticate."
            )

        oauth_token = tokens.get("access_token")
        host = tokens.get("host", "github.com")

        if not oauth_token:
            raise AIError.authentication_error(
                "Copilot OAuth token missing. Run 'gac auth copilot login' to authenticate."
            )

        session_token = get_valid_session_token(oauth_token, host)
        if not session_token:
            raise AIError.authentication_error(
                "Could not obtain Copilot session token. Your GitHub account may not have Copilot access, "
                "or the OAuth token has been revoked. Run 'gac auth copilot login' to re-authenticate."
            )

        return session_token

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Copilot API URL with /chat/completions endpoint."""
        tokens = load_stored_tokens()
        host = tokens.get("host", "github.com") if tokens else "github.com"
        base = get_api_endpoint(host)
        return f"{base}/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with Copilot session token and required headers."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Editor-Version": COPILOT_OAUTH_CONFIG["editor_version"],
            "Editor-Plugin-Version": COPILOT_OAUTH_CONFIG["editor_plugin_version"],
            "Copilot-Integration-Id": COPILOT_OAUTH_CONFIG["copilot_integration_id"],
            "Openai-Intent": COPILOT_OAUTH_CONFIG["openai_intent"],
        }
        return headers
