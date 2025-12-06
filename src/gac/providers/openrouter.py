"""OpenRouter API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class OpenRouterProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="OpenRouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1/chat/completions",
    )

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OpenRouter-style authorization and HTTP-Referer."""
        headers = super()._build_headers()
        headers["HTTP-Referer"] = "https://github.com/codeindolence/gac"
        return headers
