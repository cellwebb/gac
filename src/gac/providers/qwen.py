"""Qwen API provider for gac with OAuth-only support."""

from gac.errors import AIError
from gac.oauth import QwenOAuthProvider, TokenStore
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors

QWEN_DEFAULT_API_URL = "https://chat.qwen.ai/api/v1/chat/completions"


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
        self._auth_token, resolved_url = self._get_oauth_token()
        self.config.base_url = resolved_url

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
                if not resource_url.endswith("/chat/completions"):
                    resource_url = resource_url.rstrip("/") + "/v1/chat/completions"
                api_url = resource_url
            else:
                api_url = QWEN_DEFAULT_API_URL
            return token["access_token"], api_url

        raise AIError.authentication_error("Qwen OAuth token not found. Run 'gac auth qwen login' to authenticate.")

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OAuth token."""
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
    """Call Qwen API with OAuth authentication."""
    provider = _get_qwen_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
