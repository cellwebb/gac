"""Azure OpenAI provider for gac.

This provider provides native support for Azure OpenAI Service with proper
endpoint construction and API version handling.
"""

import json
import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_azure_openai_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Azure OpenAI Service API.

    Environment variables:
        AZURE_OPENAI_API_KEY: Azure OpenAI API key (required)
        AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL (required)
            Example: https://your-resource.openai.azure.com
        AZURE_OPENAI_API_VERSION: Azure OpenAI API version (required)
            Example: 2025-01-01-preview
            Example: 2024-02-15-preview

    Args:
        model: The deployment name in Azure OpenAI (e.g., 'gpt-4o', 'gpt-35-turbo')
        messages: List of message dictionaries with 'role' and 'content' keys
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        The generated commit message

    Raises:
        AIError: If authentication fails, API errors occur, or response is invalid
    """
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise AIError.authentication_error("AZURE_OPENAI_API_KEY environment variable not set")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise AIError.model_error("AZURE_OPENAI_ENDPOINT environment variable not set")

    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    if not api_version:
        raise AIError.model_error("AZURE_OPENAI_API_VERSION environment variable not set")

    # Build Azure OpenAI URL with proper structure
    endpoint = endpoint.rstrip("/")
    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"

    headers = {"api-key": api_key, "Content-Type": "application/json"}

    data = {"messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()

        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Unexpected response format from Azure OpenAI API. Response: {json.dumps(response_data)}")
            raise AIError.model_error(
                f"Azure OpenAI API returned unexpected format. Expected response with "
                f"'choices[0].message.content', but got: {type(e).__name__}. Check logs for full response structure."
            ) from e

        if content is None:
            raise AIError.model_error("Azure OpenAI API returned null content")
        if content == "":
            raise AIError.model_error("Azure OpenAI API returned empty content")
        return content
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"Azure OpenAI API connection failed: {str(e)}") from e
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_text = e.response.text

        if status_code == 401:
            raise AIError.authentication_error(f"Azure OpenAI API authentication failed: {error_text}") from e
        elif status_code == 429:
            raise AIError.rate_limit_error(f"Azure OpenAI API rate limit exceeded: {error_text}") from e
        else:
            raise AIError.model_error(f"Azure OpenAI API error: {status_code} - {error_text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Azure OpenAI API request timed out: {str(e)}") from e
    except AIError:
        raise
    except Exception as e:
        raise AIError.model_error(f"Error calling Azure OpenAI API: {str(e)}") from e
