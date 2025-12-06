"""Anthropic AI provider for gac."""

from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig


class AnthropicProvider(AnthropicCompatibleProvider):
    """Anthropic Claude API provider."""

    config = ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Anthropic API URL with /messages endpoint."""
        return f"{self.config.base_url}/messages"
