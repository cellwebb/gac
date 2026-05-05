"""Ollama API provider for gac."""

import os
from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ParsedResponse, ProviderConfig


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

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse Ollama response with flexible format support."""
        from gac.ai_utils import normalize_reasoning_tokens
        from gac.errors import AIError
        from gac.postprocess import extract_think_tag_text

        prompt_tokens = response.get("prompt_eval_count", -1)
        completion_tokens = response.get("eval_count", -1)
        if not isinstance(prompt_tokens, int):
            prompt_tokens = -1
        if not isinstance(completion_tokens, int):
            completion_tokens = -1

        if "message" in response and "content" in response["message"]:
            content = response["message"]["content"]
        elif "response" in response:
            content = response["response"]
        else:
            content = str(response) if response else ""

        if content is None:
            raise AIError.model_error("Ollama API returned null content")
        if content == "":
            raise AIError.model_error("Ollama API returned empty content")

        # Estimate reasoning tokens from ``<think>``...``</think>`` tags when the API
        # does not report them (common for local thinking models).
        thinking_text = extract_think_tag_text(content)
        reasoning_tokens = normalize_reasoning_tokens(None, thinking_text)

        # Normalize: subtract reasoning from completion so they are non-overlapping.
        if reasoning_tokens > 0 and completion_tokens >= 0:
            completion_tokens = max(completion_tokens - reasoning_tokens, 0)

        return ParsedResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
        )
