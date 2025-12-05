"""Gemini AI provider implementation."""

import os
from typing import Any

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def call_gemini_api(model: str, messages: list[dict[str, Any]], temperature: float, max_tokens: int) -> str:
    """Call Gemini API directly."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIError.authentication_error("GEMINI_API_KEY not found in environment variables")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    # Build Gemini request payload, converting roles to supported values.
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

    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }

    if system_instruction_parts:
        payload["systemInstruction"] = {"role": "system", "parts": system_instruction_parts}

    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=120, verify=get_ssl_verify())
        response.raise_for_status()
        response_data = response.json()

        # Check for candidates and proper response structure
        candidates = response_data.get("candidates")
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

        return content_text
    except AIError:
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Gemini API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Gemini API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Gemini API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Gemini API: {str(e)}") from e
