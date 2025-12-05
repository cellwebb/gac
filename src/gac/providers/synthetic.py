"""Synthetic.new API provider for gac."""

import os

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def call_synthetic_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Synthetic API directly."""
    # Handle model names without hf: prefix
    if not model.startswith("hf:"):
        model = f"hf:{model}"

    api_key = os.getenv("SYNTHETIC_API_KEY") or os.getenv("SYN_API_KEY")
    if not api_key:
        raise AIError.authentication_error("SYNTHETIC_API_KEY or SYN_API_KEY not found in environment variables")

    url = "https://api.synthetic.new/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": model, "messages": messages, "temperature": temperature, "max_completion_tokens": max_tokens}

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=120, verify=get_ssl_verify())
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content is None:
            raise AIError.model_error("Synthetic.new API returned null content")
        if content == "":
            raise AIError.model_error("Synthetic.new API returned empty content")
        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Synthetic.new API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Synthetic.new API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Synthetic.new API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Synthetic.new API: {str(e)}") from e
