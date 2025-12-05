"""MiniMax API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class MinimaxProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="MiniMax",
        api_key_env="MINIMAX_API_KEY",
        base_url="https://api.minimaxi.com/v1/chat/completions",
    )


# Create provider instance for backward compatibility
minimax_provider = MinimaxProvider(MinimaxProvider.config)


@handle_provider_errors("MiniMax")
def call_minimax_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call MiniMax API directly.

    Args:
        model: Model name
        messages: List of message dictionaries
        temperature: Temperature parameter
        max_tokens: Maximum tokens in response

    Returns:
        Generated text content

    Raises:
        AIError: For any API-related errors
    """
    return minimax_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
