"""StreamLake (Vanchin) API provider for gac."""

import os

import httpx

from gac.errors import AIError
from gac.utils import get_ssl_verify


def call_streamlake_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call StreamLake (Vanchin) chat completions API."""
    api_key = os.getenv("STREAMLAKE_API_KEY") or os.getenv("VC_API_KEY")
    if not api_key:
        raise AIError.authentication_error(
            "STREAMLAKE_API_KEY not found in environment variables (VC_API_KEY alias also not set)"
        )

    url = "https://vanchin.streamlake.ai/api/gateway/v1/endpoints/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

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
        choices = response_data.get("choices")
        if not choices:
            raise AIError.model_error("StreamLake API returned no choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if content is None:
            raise AIError.model_error("StreamLake API returned null content")
        if content == "":
            raise AIError.model_error("StreamLake API returned empty content")

        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"StreamLake API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"StreamLake API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"StreamLake API request timed out: {str(e)}") from e
    except Exception as e:  # noqa: BLE001 - convert to AIError
        raise AIError.model_error(f"Error calling StreamLake API: {str(e)}") from e
