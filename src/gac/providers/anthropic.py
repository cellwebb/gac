"""Anthropic AI provider implementation."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_anthropic_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Anthropic API directly."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise AIError.authentication_error("ANTHROPIC_API_KEY not found in environment variables")

    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}

    # Convert messages to Anthropic format
    anthropic_messages = []
    system_message = ""

    for msg in messages:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

    data = {"model": model, "messages": anthropic_messages, "temperature": temperature, "max_tokens": max_tokens}

    if system_message:
        data["system"] = system_message

    logger.debug(f"Calling Anthropic API with model={model}")

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()
        content = response_data["content"][0]["text"]
        if content is None:
            raise AIError.model_error("Anthropic API returned null content")
        if content == "":
            raise AIError.model_error("Anthropic API returned empty content")
        logger.debug("Anthropic API response received successfully")
        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Anthropic API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Anthropic API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Anthropic API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Anthropic API: {str(e)}") from e
