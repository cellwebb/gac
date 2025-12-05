"""Moonshot AI provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class MoonshotProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Moonshot",
        api_key_env="MOONSHOT_API_KEY",
        base_url="https://api.moonshot.cn/v1/chat/completions",
    )


def _get_moonshot_provider() -> MoonshotProvider:
    """Lazy getter to initialize Moonshot provider at call time."""
    return MoonshotProvider(MoonshotProvider.config)


@handle_provider_errors("Moonshot")
def call_moonshot_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Moonshot AI API directly."""
    provider = _get_moonshot_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
