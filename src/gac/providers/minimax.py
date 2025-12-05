"""MiniMax API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class MinimaxProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="MiniMax",
        api_key_env="MINIMAX_API_KEY",
        base_url="https://api.minimaxi.com/v1/chat/completions",
    )


def _get_minimax_provider() -> MinimaxProvider:
    """Lazy getter to initialize MiniMax provider at call time."""
    return MinimaxProvider(MinimaxProvider.config)


@handle_provider_errors("MiniMax")
def call_minimax_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call MiniMax API directly."""
    provider = _get_minimax_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
