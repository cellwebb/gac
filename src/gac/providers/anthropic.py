"""Anthropic AI provider for gac."""

from gac.providers.base import AnthropicCompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class AnthropicProvider(AnthropicCompatibleProvider):
    config = ProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com/v1/messages",
    )


# Create provider instance for backward compatibility
anthropic_provider = AnthropicProvider(AnthropicProvider.config)


@handle_provider_errors("Anthropic")
def call_anthropic_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Anthropic API directly.

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
    return anthropic_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
