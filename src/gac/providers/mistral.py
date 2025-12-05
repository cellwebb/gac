"""Mistral API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class MistralProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Mistral",
        api_key_env="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1/chat/completions",
    )


# Create provider instance for backward compatibility
mistral_provider = MistralProvider(MistralProvider.config)


@handle_provider_errors("Mistral")
def call_mistral_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Mistral API directly.

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
    return mistral_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
