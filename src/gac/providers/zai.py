"""Z.AI API provider for gac."""

import os

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def _call_zai_api_impl(
    url: str, api_name: str, model: str, messages: list[dict], temperature: float, max_tokens: int
) -> str:
    """Internal implementation for Z.AI API calls."""
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        raise AIError.authentication_error("ZAI_API_KEY not found in environment variables")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=120, verify=get_ssl_verify())
        response.raise_for_status()
        response_data = response.json()

        # Handle different possible response structures
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                if content is None:
                    raise AIError.model_error(f"{api_name} API returned null content")
                if content == "":
                    raise AIError.model_error(f"{api_name} API returned empty content")
                return content
            else:
                raise AIError.model_error(f"{api_name} API response missing content: {response_data}")
        else:
            raise AIError.model_error(f"{api_name} API unexpected response structure: {response_data}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"{api_name} API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"{api_name} API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"{api_name} API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling {api_name} API: {str(e)}") from e


def call_zai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Z.AI regular API directly."""
    url = "https://api.z.ai/api/paas/v4/chat/completions"
    return _call_zai_api_impl(url, "Z.AI", model, messages, temperature, max_tokens)


def call_zai_coding_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Z.AI coding API directly."""
    url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
    return _call_zai_api_impl(url, "Z.AI coding", model, messages, temperature, max_tokens)
