"""Groq API provider for gac."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


def call_groq_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Groq API directly."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIError.authentication_error("GROQ_API_KEY not found in environment variables")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    try:
        response = httpx.post(
            url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT, verify=get_ssl_verify()
        )
        response.raise_for_status()
        response_data = response.json()

        # Debug logging to understand response structure
        logger.debug(f"Groq API response: {response_data}")

        # Handle different response formats
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                logger.debug(f"Found content in message.content: {repr(content)}")
                if content is None:
                    raise AIError.model_error("Groq API returned null content")
                if content == "":
                    raise AIError.model_error("Groq API returned empty content")
                return content
            elif "text" in choice:
                content = choice["text"]
                logger.debug(f"Found content in choice.text: {repr(content)}")
                if content is None:
                    logger.warning("Groq API returned None content in choice.text")
                    return ""
                return content
            else:
                logger.warning(f"Unexpected choice structure: {choice}")

        # If we can't find content in the expected places, raise an error
        logger.error(f"Unexpected response format from Groq API: {response_data}")
        raise AIError.model_error(f"Unexpected response format from Groq API: {response_data}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Groq API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Groq API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Groq API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Groq API: {str(e)}") from e
