"""Qwen API provider for gac with OAuth support."""

import logging
import os

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.oauth import QwenOAuthProvider, TokenStore

logger = logging.getLogger(__name__)

QWEN_API_URL = "https://chat.qwen.ai/api/v1/chat/completions"


def get_qwen_auth() -> tuple[str, str]:
    """Get Qwen authentication (API key or OAuth token).

    Returns:
        Tuple of (token, api_url) for authentication.
    """
    api_key = os.getenv("QWEN_API_KEY")
    if api_key:
        return api_key, QWEN_API_URL

    oauth_provider = QwenOAuthProvider(TokenStore())
    token = oauth_provider.get_token()
    if token:
        resource_url = token.get("resource_url")
        if resource_url:
            if not resource_url.startswith(("http://", "https://")):
                resource_url = f"https://{resource_url}"
            if not resource_url.endswith("/chat/completions"):
                resource_url = resource_url.rstrip("/") + "/v1/chat/completions"
            api_url = resource_url
        else:
            api_url = QWEN_API_URL
        return token["access_token"], api_url

    raise AIError.authentication_error(
        "Qwen authentication not found. Set QWEN_API_KEY or run 'gac auth qwen login' for OAuth."
    )


def call_qwen_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
    """Call Qwen API with OAuth or API key authentication."""
    auth_token, api_url = get_qwen_auth()

    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

    data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    logger.debug(f"Calling Qwen API with model={model}")

    try:
        response = httpx.post(api_url, headers=headers, json=data, timeout=ProviderDefaults.HTTP_TIMEOUT)
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if content is None:
            raise AIError.model_error("Qwen API returned null content")
        if content == "":
            raise AIError.model_error("Qwen API returned empty content")
        logger.debug("Qwen API response received successfully")
        return content
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise AIError.authentication_error(f"Qwen authentication failed: {e.response.text}") from e
        if e.response.status_code == 429:
            raise AIError.rate_limit_error(f"Qwen API rate limit exceeded: {e.response.text}") from e
        raise AIError.model_error(f"Qwen API error: {e.response.status_code} - {e.response.text}") from e
    except httpx.TimeoutException as e:
        raise AIError.timeout_error(f"Qwen API request timed out: {str(e)}") from e
    except Exception as e:
        raise AIError.model_error(f"Error calling Qwen API: {str(e)}") from e
