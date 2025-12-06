"""Mistral API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MistralProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Mistral",
        api_key_env="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Mistral API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
