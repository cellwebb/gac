"""DeepSeek API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class DeepSeekProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="DeepSeek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get DeepSeek API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
