"""Z.AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class ZAIProvider(OpenAICompatibleProvider):
    """Z.AI regular API provider with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Z.AI",
        api_key_env="ZAI_API_KEY",
        base_url="https://api.z.ai/api/paas/v4/chat/completions",
    )


class ZAICodingProvider(OpenAICompatibleProvider):
    """Z.AI coding API provider with OpenAI-compatible format."""

    config = ProviderConfig(
        name="Z.AI Coding",
        api_key_env="ZAI_API_KEY",
        base_url="https://api.z.ai/api/coding/paas/v4/chat/completions",
    )
