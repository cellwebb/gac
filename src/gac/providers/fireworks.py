"""Fireworks AI API provider for gac."""

from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig

# Fireworks has a non-streaming limit of 4096 tokens
FIREWORKS_MAX_TOKENS_NON_STREAMING = 4096


class FireworksProvider(OpenAICompatibleProvider):
    config = ProviderConfig(
        name="Fireworks",
        api_key_env="FIREWORKS_API_KEY",
        base_url="https://api.fireworks.ai/inference/v1",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Fireworks API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build OpenAI-style request body with Fireworks-specific requirements.

        Fireworks requires stream=true when max_tokens > 4096.
        Since we don't support streaming responses yet, cap max_tokens at 4096.
        See: https://docs.fireworks.ai/api-reference
        """
        # Cap max_tokens at Fireworks' non-streaming limit
        capped_max_tokens = min(max_tokens, FIREWORKS_MAX_TOKENS_NON_STREAMING)

        return super()._build_request_body(messages, temperature, capped_max_tokens, model, **kwargs)
