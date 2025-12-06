"""Fireworks AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class FireworksProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Fireworks",
        api_key_env="FIREWORKS_API_KEY",
        base_url="https://api.fireworks.ai/inference/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Fireworks API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
