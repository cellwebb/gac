"""Wafer.ai provider implementation."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class WaferProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Wafer.ai",
        api_key_env="WAFER_API_KEY",
        base_url="https://pass.Wafer.ai/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Wafer.ai API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
