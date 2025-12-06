"""Cerebras AI provider implementation."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class CerebrasProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Cerebras",
        api_key_env="CEREBRAS_API_KEY",
        base_url="https://api.cerebras.ai/v1/chat/completions",
    )
