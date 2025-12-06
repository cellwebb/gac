"""Ollama API provider for gac."""

import os
from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ProviderConfig


class OllamaProvider(OpenAICompatibleProvider):
    """Ollama provider for local LLM models with optional authentication."""

    config = ProviderConfig(
        name="Ollama",
        api_key_env="OLLAMA_API_KEY",
        base_url="http://localhost:11434",
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with configurable URL from environment."""
        super().__init__(config)
        # Allow URL override via environment variable
        api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        self.config.base_url = api_url.rstrip("/")

    def _build_headers(self) -> dict[str, str]:
        """Build headers with optional API key."""
        headers = super()._build_headers()
        api_key = os.getenv("OLLAMA_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build Ollama request body with stream disabled."""
        return {
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            **kwargs,
        }

    def _get_api_url(self, model: str | None = None) -> str:
        """Get API URL with /api/chat endpoint."""
        return f"{self.config.base_url}/api/chat"

    def _get_api_key(self) -> str:
        """Get optional API key for Ollama."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            return ""  # Optional API key
        return api_key

    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse Ollama response with flexible format support."""
        from gac.errors import AIError

        # Handle different response formats from Ollama
        if "message" in response and "content" in response["message"]:
            content = response["message"]["content"]
        elif "response" in response:
            content = response["response"]
        else:
            # Fallback: try to serialize response
            content = str(response) if response else ""

        if content is None:
            raise AIError.model_error("Ollama API returned null content")
        if content == "":
            raise AIError.model_error("Ollama API returned empty content")

        return content
