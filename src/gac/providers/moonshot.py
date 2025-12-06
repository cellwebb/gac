"""Moonshot AI provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MoonshotProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Moonshot",
        api_key_env="MOONSHOT_API_KEY",
        base_url="https://api.moonshot.cn/v1/chat/completions",
    )
