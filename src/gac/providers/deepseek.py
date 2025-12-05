"""DeepSeek API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class DeepSeekProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="DeepSeek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com/v1/chat/completions",
    )


def _get_deepseek_provider() -> DeepSeekProvider:
    """Lazy getter to initialize DeepSeek provider at call time."""
    return DeepSeekProvider(DeepSeekProvider.config)


@handle_provider_errors("DeepSeek")
def call_deepseek_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call DeepSeek API directly."""
    provider = _get_deepseek_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
