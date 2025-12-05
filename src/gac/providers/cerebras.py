"""Cerebras AI provider implementation."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class CerebrasProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Cerebras",
        api_key_env="CEREBRAS_API_KEY",
        base_url="https://api.cerebras.ai/v1/chat/completions",
    )


def _get_cerebras_provider() -> CerebrasProvider:
    """Lazy getter to initialize Cerebras provider at call time."""
    return CerebrasProvider(CerebrasProvider.config)


@handle_provider_errors("Cerebras")
def call_cerebras_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Cerebras API directly."""
    provider = _get_cerebras_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
