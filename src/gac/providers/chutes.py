"""Chutes.ai API provider for gac."""

import os

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def call_chutes_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Chutes.ai API directly.

    Chutes.ai provides an OpenAI-compatible API for serverless, decentralized AI compute.

    Args:
        model: The model to use (e.g., 'deepseek-ai/DeepSeek-V3-0324')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    api_key = os.getenv("CHUTES_API_KEY")
    if not api_key:
        raise AIError.authentication_error("CHUTES_API_KEY environment variable not set")

    base_url = os.getenv("CHUTES_BASE_URL", "https://llm.chutes.ai")
    url = f"{base_url}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=120, verify=get_ssl_verify())
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content is None:
            raise AIError.model_error("Chutes.ai API returned null content")
        if content == "":
            raise AIError.model_error("Chutes.ai API returned empty content")
        return content
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_text = e.response.text

        if status_code == 429:
            raise AIError.rate_limit_error(f"Chutes.ai API rate limit exceeded: {error_text}") from e
        elif status_code in (502, 503):
            raise AIError.connection_error(f"Chutes.ai API service unavailable: {status_code} - {error_text}") from e
        else:
            raise AIError.model_error(f"Chutes.ai API error: {status_code} - {error_text}") from e
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"Chutes.ai API connection error: {str(e)}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Chutes.ai API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Chutes.ai API: {str(e)}") from e
