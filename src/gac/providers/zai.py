"""Z.AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class ZAIProvider(OpenAICompatibleProvider):
    """Z.AI regular API provider with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Z.AI",
        api_key_env="ZAI_API_KEY",
        base_url="https://api.z.ai/api/paas/v4",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Z.AI API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"


class ZAICodingProvider(OpenAICompatibleProvider):
    """Z.AI coding API provider with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Z.AI Coding",
        api_key_env="ZAI_API_KEY",
        base_url="https://api.z.ai/api/coding/paas/v4",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Z.AI Coding API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
