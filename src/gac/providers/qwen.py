"""Qwen API provider for gac with OAuth-only support."""

from gac.errors import AIError
from gac.oauth import QwenOAuthProvider, TokenStore
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig

QWEN_DEFAULT_API_URL = "https://chat.qwen.ai/api/v1"


class QwenProvider(OpenAICompatibleProvider):
    """Qwen provider with OAuth-only authentication."""

    config = ProviderConfig(
        name="Qwen",
        api_key_env="",
        base_url=QWEN_DEFAULT_API_URL,
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with OAuth authentication."""
        super().__init__(config)
        self._auth_token, self._resolved_base_url = self._get_oauth_token()

    def _get_api_key(self) -> str:
        """Return placeholder for parent class compatibility (OAuth is used instead)."""
        return "oauth-token"

    def _get_oauth_token(self) -> tuple[str, str]:
        """Get Qwen OAuth token from token store.

        Returns:
            Tuple of (access_token, api_url) for authentication.

        Raises:
            AIError: If no OAuth token is found.
        """
        oauth_provider = QwenOAuthProvider(TokenStore())
        token = oauth_provider.get_token()
        if token:
            resource_url = token.get("resource_url")
            if resource_url:
                if not resource_url.startswith(("http://", "https://")):
                    resource_url = f"https://{resource_url}"
                if not resource_url.endswith("/v1"):
                    resource_url = resource_url.rstrip("/") + "/v1"
                base_url = resource_url
            else:
                base_url = QWEN_DEFAULT_API_URL
            return token["access_token"], base_url

        raise AIError.authentication_error("Qwen OAuth token not found. Run 'gac auth qwen login' to authenticate.")

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth token."""
        headers = super()._build_headers()
        # Replace Bearer token with the stored auth token
        if "Authorization" in headers:
            del headers["Authorization"]
        headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Qwen API URL with /chat/completions endpoint."""
        return f"{self._resolved_base_url}/chat/completions"
