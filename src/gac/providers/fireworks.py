"""Fireworks AI API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class FireworksProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Fireworks",
        api_key_env="FIREWORKS_API_KEY",
        base_url="https://api.fireworks.ai/inference/v1/chat/completions",
    )


# Create provider instance for backward compatibility
fireworks_provider = FireworksProvider(FireworksProvider.config)


@handle_provider_errors("Fireworks")
def call_fireworks_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Fireworks AI API directly.

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
    return fireworks_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
