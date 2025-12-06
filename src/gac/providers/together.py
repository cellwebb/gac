"""Together AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class TogetherProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Together",
        api_key_env="TOGETHER_API_KEY",
        base_url="https://api.together.xyz/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Together API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
