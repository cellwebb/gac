"""Ollama AI provider implementation."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_ollama_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Ollama API directly."""
    api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    api_key = os.getenv("OLLAMA_API_KEY")

    url = f"{api_url.rstrip('/')}/api/chat"
    data = {"model": model, "messages": messages, "temperature": temperature, "stream": False}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    logger.debug(f"Calling Ollama API with model={model}")

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()

        content = None
        # Handle different response formats from Ollama
        if "message" in response_data and "content" in response_data["message"]:
            content = response_data["message"]["content"]
        elif "response" in response_data:
            content = response_data["response"]
        else:
            # Fallback: return the full response as string
            content = str(response_data)

        if content is None:
            raise AIError.model_error("Ollama API returned null content")
        if content == "":
            raise AIError.model_error("Ollama API returned empty content")
        logger.debug("Ollama API response received successfully")
        return content
    except httpx.ConnectError as e:
        raise AIError.connection_error(f"Ollama connection failed. Make sure Ollama is running: {str(e)}") from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Ollama API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Ollama API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Ollama API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Ollama API: {str(e)}") from e
