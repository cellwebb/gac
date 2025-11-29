"""Kimi Coding AI provider implementation."""

import json
import logging
import os

import httpx

from gac.errors import AIError

logger = logging.getLogger(__name__)


def call_kimi_coding_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Kimi Coding API using OpenAI-compatible endpoint."""
    api_key = os.getenv("KIMI_CODING_API_KEY")
    if not api_key:
        raise AIError.authentication_error("KIMI_CODING_API_KEY not found in environment variables")

    base_url = "https://api.kimi.com/coding/v1"
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Use standard OpenAI format - no message conversion needed
    data = {"model": model, "messages": messages, "temperature": temperature, "max_completion_tokens": max_tokens}

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        response_data = response.json()

        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Unexpected response format from Kimi Coding API. Response: {json.dumps(response_data)}")
            raise AIError.model_error(
                f"Kimi Coding API returned unexpected format. Expected OpenAI-compatible response with "
                f"'choices[0].message.content', but got: {type(e).__name__}. Check logs for full response structure."
            ) from e

        if content is None:
            raise AIError.model_error("Kimi Coding API returned null content")
        if content == "":
            raise AIError.model_error("Kimi Coding API returned empty content")
        return content
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"Kimi Coding API connection failed: {str(e)}") from e
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_text = e.response.text

        if status_code == 401:
            raise AIError.authentication_error(f"Kimi Coding API authentication failed: {error_text}") from e
        elif status_code == 429:
            raise AIError.rate_limit_error(f"Kimi Coding API rate limit exceeded: {error_text}") from e
        else:
            raise AIError.model_error(f"Kimi Coding API error: {status_code} - {error_text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Kimi Coding API request timed out: {str(e)}") from e
    except AIError:
        raise
    except Exception as e:
        raise AIError.model_error(f"Error calling Kimi Coding API: {str(e)}") from e
