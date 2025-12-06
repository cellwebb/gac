"""Anthropic AI provider for gac."""

from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig


class AnthropicProvider(AnthropicCompatibleProvider):
    """Anthropic Claude API provider."""

    config = ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com/v1/messages",
    )
