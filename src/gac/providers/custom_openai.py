"""Custom OpenAI-compatible API provider for gac.

This provider allows users to specify a custom OpenAI-compatible endpoint
while using the same model capabilities as the standard OpenAI provider.
"""

import json
import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_custom_openai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call a custom OpenAI-compatible API endpoint.

    This provider is useful for:
    - OpenAI-compatible proxies or gateways
    - Self-hosted OpenAI-compatible services
    - Other services implementing the OpenAI Chat Completions API

    Environment variables:
        CUSTOM_OPENAI_API_KEY: API key for authentication (required)
        CUSTOM_OPENAI_BASE_URL: Base URL for the API endpoint (required)
            Example: https://your-proxy.example.com/v1
            Example: https://your-custom-endpoint.com

    Args:
        model: The model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    api_key = os.getenv("CUSTOM_OPENAI_API_KEY")
    if not api_key:
        raise AIError.authentication_error("CUSTOM_OPENAI_API_KEY environment variable not set")

    base_url = os.getenv("CUSTOM_OPENAI_BASE_URL")
    if not base_url:
        raise AIError.model_error("CUSTOM_OPENAI_BASE_URL environment variable not set")

    if "/chat/completions" not in base_url:
        base_url = base_url.rstrip("/")
        url = f"{base_url}/chat/completions"
    else:
        url = base_url

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": model, "messages": messages, "temperature": temperature, "max_completion_tokens": max_tokens}

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()

        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Unexpected response format from Custom OpenAI API. Response: {json.dumps(response_data)}")
            raise AIError.model_error(
                f"Custom OpenAI API returned unexpected format. Expected OpenAI-compatible response with "
                f"'choices[0].message.content', but got: {type(e).__name__}. Check logs for full response structure."
            ) from e

        if content is None:
            raise AIError.model_error("Custom OpenAI API returned null content")
        if content == "":
            raise AIError.model_error("Custom OpenAI API returned empty content")
        return content
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"Custom OpenAI API connection failed: {str(e)}") from e
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_text = e.response.text

        if status_code == 401:
            raise AIError.authentication_error(f"Custom OpenAI API authentication failed: {error_text}") from e
        elif status_code == 429:
            raise AIError.rate_limit_error(f"Custom OpenAI API rate limit exceeded: {error_text}") from e
        else:
            raise AIError.model_error(f"Custom OpenAI API error: {status_code} - {error_text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Custom OpenAI API request timed out: {str(e)}") from e
    except AIError:
        raise
    except Exception as e:
        raise AIError.model_error(f"Error calling Custom OpenAI API: {str(e)}") from e
