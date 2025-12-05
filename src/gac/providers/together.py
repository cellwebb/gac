"""Together AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class TogetherProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Together",
        api_key_env="TOGETHER_API_KEY",
        base_url="https://api.together.xyz/v1/chat/completions",
    )


def _get_together_provider() -> TogetherProvider:
    """Lazy getter to initialize Together provider at call time."""
    return TogetherProvider(TogetherProvider.config)


@handle_provider_errors("Together")
def call_together_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Together AI API directly."""
    provider = _get_together_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
