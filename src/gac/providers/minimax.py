"""MiniMax API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MinimaxProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="MiniMax",
        api_key_env="MINIMAX_API_KEY",
        base_url="https://api.minimaxi.com/v1/chat/completions",
    )
