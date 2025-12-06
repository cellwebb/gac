"""Mistral API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class MistralProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Mistral",
        api_key_env="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1/chat/completions",
    )
