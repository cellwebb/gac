"""Gemini AI provider implementation."""

from typing import Any

from gac.errors import AIError
from gac.providers.base import GenericHTTPProvider, ParsedResponse, ProviderConfig


class GeminiProvider(GenericHTTPProvider):
    """Google Gemini provider with custom format and role conversion."""

    config = ProviderConfig(
        name="Gemini",
        api_key_env="GEMINI_API_KEY",
        base_url="https://generativelanguage.googleapis.com/v1beta",
    )

    def _get_api_url(self, model: str | None = None) -> str:
        """Build Gemini URL with model in path."""
        if model is None:
            return super()._get_api_url(model)
        return f"{self.config.base_url}/models/{model}:generateContent"

    def _build_headers(self) -> dict[str, str]:
        """Build headers with Google API key."""
        headers = super()._build_headers()
        # Remove any Authorization header
        if "Authorization" in headers:
            del headers["Authorization"]
        headers["x-goog-api-key"] = self.api_key
        return headers

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build Gemini-format request with role conversion and system instruction extraction."""
        contents: list[dict[str, Any]] = []
        system_instruction_parts: list[dict[str, str]] = []

        for msg in messages:
            role = msg.get("role")
            content_value = msg.get("content")
            content = "" if content_value is None else str(content_value)

            if role == "system":
                if content.strip():
                    system_instruction_parts.append({"text": content})
                continue

            if role == "assistant":
                gemini_role = "model"
            elif role == "user":
                gemini_role = "user"
            else:
                raise AIError.model_error(f"Unsupported message role for Gemini API: {role}")

            contents.append({"role": gemini_role, "parts": [{"text": content}]})

        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }

        if system_instruction_parts:
            body["systemInstruction"] = {"role": "system", "parts": system_instruction_parts}

        return body

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse Gemini response format: candidates[0].content.parts[0].text."""
        from gac.ai_utils import normalize_reasoning_tokens
        from gac.postprocess import extract_think_tag_text

        candidates = response.get("candidates")
        if not candidates:
            raise AIError.model_error("Gemini API response missing candidates")

        candidate = candidates[0]
        if "content" not in candidate or "parts" not in candidate["content"] or not candidate["content"]["parts"]:
            raise AIError.model_error("Gemini API response has invalid content structure")

        parts = candidate["content"]["parts"]
        content_text: str | None = None
        for part in parts:
            if isinstance(part, dict):
                part_text = part.get("text")
                if isinstance(part_text, str) and part_text:
                    content_text = part_text
                    break
        if content_text is None:
            raise AIError.model_error("Gemini API response missing text content")

        usage_meta = response.get("usageMetadata")
        prompt_tokens = -1
        completion_tokens = -1
        reasoning_tokens: int | None = None  # None = not reported by API
        if isinstance(usage_meta, dict):
            pt = usage_meta.get("promptTokenCount", -1)
            ct = usage_meta.get("candidatesTokenCount", -1)
            prompt_tokens = pt if isinstance(pt, int) else -1
            raw_completion = ct if isinstance(ct, int) else -1
            if "thoughtsTokenCount" in usage_meta:
                rt = usage_meta["thoughtsTokenCount"]
                reasoning_tokens = rt if isinstance(rt, int) else None
            # Normalize: candidatesTokenCount includes thoughts; subtract
            # so completion = output tokens only (excludes reasoning).
            if reasoning_tokens is not None:
                completion_tokens = max(raw_completion - reasoning_tokens, 0) if raw_completion >= 0 else raw_completion
            else:
                completion_tokens = raw_completion
        else:
            completion_tokens = -1

        # Estimate reasoning tokens from <think> tags when the API
        # doesn't report them explicitly.
        thinking_text = extract_think_tag_text(content_text)
        reasoning_tokens = normalize_reasoning_tokens(reasoning_tokens, thinking_text)

        # Recompute completion_tokens with the final reasoning_tokens value.
        if isinstance(usage_meta, dict):
            ct = usage_meta.get("candidatesTokenCount", -1)
            raw_completion = ct if isinstance(ct, int) else -1
            completion_tokens = max(raw_completion - reasoning_tokens, 0) if raw_completion >= 0 else raw_completion

        return ParsedResponse(
            content=content_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
        )
