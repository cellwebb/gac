"""Moonshot AI provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MoonshotProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Moonshot",
        api_key_env="MOONSHOT_API_KEY",
        base_url="https://api.moonshot.cn/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Moonshot API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
