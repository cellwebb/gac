"""Anthropic AI provider for gac."""

from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class AnthropicProvider(AnthropicCompatibleProvider):
    config = ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com/v1/messages",
    )


def _get_anthropic_provider() -> AnthropicProvider:
    """Lazy getter to initialize Anthropic provider at call time."""
    return AnthropicProvider(AnthropicProvider.config)


@handle_provider_errors("Anthropic")
def call_anthropic_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Anthropic API directly."""
    provider = _get_anthropic_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
