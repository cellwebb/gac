"""Z.AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


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


def _get_zai_provider() -> ZAIProvider:
    """Lazy getter to initialize Z.AI provider at call time."""
    return ZAIProvider(ZAIProvider.config)


def _get_zai_coding_provider() -> ZAICodingProvider:
    """Lazy getter to initialize Z.AI coding provider at call time."""
    return ZAICodingProvider(ZAICodingProvider.config)


@handle_provider_errors("Z.AI")
def call_zai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Z.AI regular API directly."""
    provider = _get_zai_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)


@handle_provider_errors("Z.AI Coding")
def call_zai_coding_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Z.AI coding API directly."""
    provider = _get_zai_coding_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
