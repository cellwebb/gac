"""OpenAI API provider for gac."""

from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI API provider with model-specific adjustments."""

    config = ProviderConfig(name="OpenAI", api_key_env="OPENAI_API_KEY", base_url="https://api.openai.com/v1")

    def _get_api_url(self, model: str | None = None) -> str:
        """Get OpenAI API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
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
