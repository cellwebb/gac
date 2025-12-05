"""OpenRouter API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class OpenRouterProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="OpenRouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1/chat/completions",
    )

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OpenRouter-style authorization and HTTP-Referer."""
        headers = super()._build_headers()
        # OpenRouter recommends including an HTTP-Referer header
        headers["HTTP-Referer"] = "https://github.com/codeindolence/gac"
        return headers


def _get_openrouter_provider() -> OpenRouterProvider:
    """Lazy getter to initialize OpenRouter provider at call time."""
    return OpenRouterProvider(OpenRouterProvider.config)


@handle_provider_errors("OpenRouter")
def call_openrouter_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call OpenRouter API directly."""
    provider = _get_openrouter_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
