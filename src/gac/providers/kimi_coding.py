"""Kimi Coding AI provider implementation."""

from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class KimiCodingProvider(OpenAICompatibleProvider):
    """Kimi Coding API provider using OpenAI-compatible format."""

    config = ProviderConfig(
        name="Kimi Coding",
        api_key_env="KIMI_CODING_API_KEY",
        base_url="https://api.kimi.com/coding/v1/chat/completions",
    )

    def _build_request_body(
        self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs
    ) -> dict[str, Any]:
        """Build request body with max_completion_tokens instead of max_tokens."""
        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        data["max_completion_tokens"] = data.pop("max_tokens")
        return data


def _get_kimi_coding_provider() -> KimiCodingProvider:
    """Lazy getter to initialize provider at call time."""
    return KimiCodingProvider(KimiCodingProvider.config)


@handle_provider_errors("Kimi Coding")
def call_kimi_coding_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Kimi Coding API using OpenAI-compatible endpoint."""
    provider = _get_kimi_coding_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
