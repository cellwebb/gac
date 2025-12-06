"""MiniMax API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MinimaxProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="MiniMax",
        api_key_env="MINIMAX_API_KEY",
        base_url="https://api.minimaxi.com/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get MiniMax API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"
