"""Qwen API provider for gac with OAuth support."""

import os

from gac.errors import AIError
from gac.oauth import QwenOAuthProvider, TokenStore
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors

QWEN_DEFAULT_API_URL = "https://chat.qwen.ai/api/v1/chat/completions"


class QwenProvider(OpenAICompatibleProvider):
    """Qwen provider with OAuth token and API key support."""

    config = ProviderConfig(
        name="Qwen",
        api_key_env="QWEN_API_KEY",
        base_url=QWEN_DEFAULT_API_URL,
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with OAuth or API key authentication."""
        super().__init__(config)
        # Resolve authentication and API URL
        self._auth_token, resolved_url = self._get_qwen_auth()
        self.config.base_url = resolved_url

    def _get_api_key(self) -> str:
        """Get API key from environment (for compatibility with parent class)."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            # Will use OAuth in _get_qwen_auth instead
            return "oauth-token"
        return api_key

    def _get_qwen_auth(self) -> tuple[str, str]:
        """Get Qwen authentication (API key or OAuth token).

        Returns:
            Tuple of (token, api_url) for authentication.
        """
        api_key = os.getenv("QWEN_API_KEY")
        if api_key:
            return api_key, QWEN_DEFAULT_API_URL

        # Try OAuth
        oauth_provider = QwenOAuthProvider(TokenStore())
        token = oauth_provider.get_token()
        if token:
            resource_url = token.get("resource_url")
            if resource_url:
                if not resource_url.startswith(("http://", "https://")):
                    resource_url = f"https://{resource_url}"
                if not resource_url.endswith("/chat/completions"):
                    resource_url = resource_url.rstrip("/") + "/v1/chat/completions"
                api_url = resource_url
            else:
                api_url = QWEN_DEFAULT_API_URL
            return token["access_token"], api_url

        raise AIError.authentication_error(
            "Qwen authentication not found. Set QWEN_API_KEY or run 'gac auth qwen login' for OAuth."
        )

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth or API key token."""
        headers = super()._build_headers()
        # Replace Bearer token with the stored auth token
        if "Authorization" in headers:
            del headers["Authorization"]
        headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers


def _get_qwen_provider() -> QwenProvider:
    """Lazy getter to initialize Qwen provider at call time."""
    return QwenProvider(QwenProvider.config)


@handle_provider_errors("Qwen")
def call_qwen_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Qwen API with OAuth or API key authentication."""
    provider = _get_qwen_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
