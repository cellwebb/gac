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


# Create provider instance for backward compatibility
openrouter_provider = OpenRouterProvider(OpenRouterProvider.config)


@handle_provider_errors("OpenRouter")
def call_openrouter_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call OpenRouter API directly.

    Args:
        model: Model name
        messages: List of message dictionaries
        temperature: Temperature parameter
        max_tokens: Maximum tokens in response

    Returns:
        Generated text content

    Raises:
        AIError: For any API-related errors
    """
    return openrouter_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
