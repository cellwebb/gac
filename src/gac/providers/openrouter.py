"""OpenRouter API provider for gac."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_openrouter_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call OpenRouter API directly."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise AIError.authentication_error("OPENROUTER_API_KEY environment variable not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
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

    logger.debug(f"Calling OpenRouter API with model={model}")

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content is None:
            raise AIError.model_error("OpenRouter API returned null content")
        if content == "":
            raise AIError.model_error("OpenRouter API returned empty content")
        logger.debug("OpenRouter API response received successfully")
        return content
    except httpx.HTTPStatusError as e:
        # Handle specific HTTP status codes
        status_code = e.response.status_code
        error_text = e.response.text

        # Rate limiting
        if status_code == 429:
            raise AIError.rate_limit_error(f"OpenRouter API rate limit exceeded: {error_text}") from e
        # Service unavailable
        elif status_code in (502, 503):
            raise AIError.connection_error(f"OpenRouter API service unavailable: {status_code} - {error_text}") from e
        # Other HTTP errors
        else:
            raise AIError.model_error(f"OpenRouter API error: {status_code} - {error_text}") from e
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"OpenRouter API connection error: {str(e)}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"OpenRouter API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling OpenRouter API: {str(e)}") from e
