"""Fireworks AI API provider for gac."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_fireworks_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Fireworks AI API directly."""
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        raise AIError.authentication_error("FIREWORKS_API_KEY not found in environment variables")

    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    logger.debug(f"Calling Fireworks AI API with model={model}")

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content is None:
            raise AIError.model_error("Fireworks AI API returned null content")
        if content == "":
            raise AIError.model_error("Fireworks AI API returned empty content")
        logger.debug("Fireworks AI API response received successfully")
        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Fireworks AI API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Fireworks AI API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Fireworks AI API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Fireworks AI API: {str(e)}") from e
