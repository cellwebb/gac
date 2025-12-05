"""OpenAI API provider for gac."""

from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig
from gac.providers.error_handler import handle_provider_errors


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI API provider with model-specific adjustments."""

    config = ProviderConfig(
        name="OpenAI", api_key_env="OPENAI_API_KEY", base_url="https://api.openai.com/v1/chat/completions"
    )

    def _build_request_body(
        self, messages: list[dict], temperature: float, max_tokens: int, model: str, **kwargs
    ) -> dict[str, Any]:
        """Build OpenAI-specific request body."""
        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)

        # OpenAI uses max_completion_tokens instead of max_tokens
        data["max_completion_tokens"] = data.pop("max_tokens")

        # Handle optional parameters
        if "response_format" in kwargs:
            data["response_format"] = kwargs["response_format"]
        if "stop" in kwargs:
            data["stop"] = kwargs["stop"]

        return data


def _get_openai_provider() -> OpenAIProvider:
    """Lazy getter to initialize OpenAI provider at call time."""
    return OpenAIProvider(OpenAIProvider.config)


@handle_provider_errors("OpenAI")
def call_openai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call OpenAI API directly."""
    provider = _get_openai_provider()
    return provider.generate(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
