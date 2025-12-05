"""Groq API provider for gac."""

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class GroqProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Groq",
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1/chat/completions",
    )


def _get_groq_provider() -> GroqProvider:
    """Lazy getter to initialize Groq provider at call time."""
    return GroqProvider(GroqProvider.config)


@handle_provider_errors("Groq")
def call_groq_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Groq API directly."""
    provider = _get_groq_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
