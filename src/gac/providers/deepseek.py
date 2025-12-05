"""DeepSeek API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class DeepSeekProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="DeepSeek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com/v1/chat/completions",
    )


# Create provider instance for backward compatibility
deepseek_provider = DeepSeekProvider(DeepSeekProvider.config)


@handle_provider_errors("DeepSeek")
def call_deepseek_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call DeepSeek API directly.

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
    return deepseek_provider.generate(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
