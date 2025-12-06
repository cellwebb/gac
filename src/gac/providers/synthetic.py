"""Synthetic.new API provider for gac."""

import os
from typing import Any

from gac.errors import AIError
from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class SyntheticProvider(OpenAICompatibleProvider):
    """Synthetic.new OpenAI-compatible provider with alternative env vars and model preprocessing."""

    config = ProviderConfig(
        name="Synthetic",
        api_key_env="SYNTHETIC_API_KEY",
        base_url="https://api.synthetic.new/openai/v1/chat/completions",
    )

    def _get_api_key(self) -> str:
        """Get API key from environment with fallback to SYN_API_KEY."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            api_key = os.getenv("SYN_API_KEY")
        if not api_key:
            raise AIError.authentication_error("SYNTHETIC_API_KEY or SYN_API_KEY not found in environment variables")
        return api_key

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build request body with model name preprocessing and max_completion_tokens."""
        # Auto-add hf: prefix if not present
        if not model.startswith("hf:"):
            model = f"hf:{model}"

        data = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        data["max_completion_tokens"] = data.pop("max_tokens")
        # Ensure the prefixed model is used
        data["model"] = model
        return data
