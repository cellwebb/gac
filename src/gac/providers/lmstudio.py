"""LM Studio API provider for gac."""

import os
from typing import Any

from gac.providers.base import OpenAICompatibleProvider, ParsedResponse, ProviderConfig


class LMStudioProvider(OpenAICompatibleProvider):
    """LM Studio provider for local OpenAI-compatible models."""

    config = ProviderConfig(
        name="LM Studio",
        api_key_env="LMSTUDIO_API_KEY",
        base_url="http://localhost:1234/v1",
    )

    def __init__(self, config: ProviderConfig):
        """Initialize with configurable URL from environment."""
        super().__init__(config)
        # Allow URL override via environment variable
        api_url = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234")
        api_url = api_url.rstrip("/")
        self.config.base_url = f"{api_url}/v1"

    def _get_api_key(self) -> str:
        """Get optional API key for LM Studio."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            return ""  # Optional API key
        return api_key

    def _build_headers(self) -> dict[str, str]:
        """Build headers with optional API key."""
        headers = super()._build_headers()
        # Remove Bearer token from parent if it was added
        if "Authorization" in headers:
            del headers["Authorization"]
        # Add optional Authorization
        api_key = os.getenv("LMSTUDIO_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _get_api_url(self, model: str | None = None) -> str:
        """Get LM Studio API URL with /chat/completions endpoint."""
        return f"{self.config.base_url}/chat/completions"

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build OpenAI-compatible request body with stream disabled."""
        body = super()._build_request_body(messages, temperature, max_tokens, model, **kwargs)
        body["stream"] = False
        return body

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse OpenAI-compatible response with text field fallback."""
        from gac.ai_utils import normalize_reasoning_tokens
        from gac.errors import AIError
        from gac.postprocess import extract_think_tag_text

        usage = response.get("usage")
        prompt_tokens = -1
        completion_tokens = -1
        reasoning_tokens: int | None = None  # None = not reported by API
        if isinstance(usage, dict):
            pt = usage.get("prompt_tokens", -1)
            ct = usage.get("completion_tokens", -1)
            prompt_tokens = pt if isinstance(pt, int) else -1
            completion_tokens = ct if isinstance(ct, int) else -1
            details = usage.get("completion_tokens_details")
            if isinstance(details, dict) and "reasoning_tokens" in details:
                rt = details["reasoning_tokens"]
                reasoning_tokens = rt if isinstance(rt, int) else None

        choices = response.get("choices")
        if not choices or not isinstance(choices, list):
            raise AIError.model_error("Invalid response: missing choices")

        choice = choices[0]
        content = choice.get("message", {}).get("content")
        if content is None:
            content = choice.get("text")

        if content is None:
            raise AIError.model_error("Invalid response: missing content")
        if content == "":
            raise AIError.model_error("Invalid response: empty content")

        # Estimate reasoning tokens from <tool_call>...</think> tags when the API
        # doesn't report them explicitly (e.g. local thinking models).
        thinking_text = extract_think_tag_text(content)
        reasoning_tokens = normalize_reasoning_tokens(reasoning_tokens, thinking_text)

        return ParsedResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=(
                max(completion_tokens - reasoning_tokens, 0) if completion_tokens >= 0 else completion_tokens
            ),
            reasoning_tokens=reasoning_tokens,
        )
