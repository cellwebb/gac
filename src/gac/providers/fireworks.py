"""Fireworks AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class FireworksProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Fireworks",
        api_key_env="FIREWORKS_API_KEY",
        base_url="https://api.fireworks.ai/inference/v1/chat/completions",
    )
