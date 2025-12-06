"""Together AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class TogetherProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Together",
        api_key_env="TOGETHER_API_KEY",
        base_url="https://api.together.xyz/v1/chat/completions",
    )
