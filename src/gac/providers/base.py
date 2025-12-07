"""Base configured provider class to eliminate code duplication."""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.providers.protocol import ProviderProtocol
from gac.utils import get_ssl_verify

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for AI providers."""

    name: str
    api_key_env: str
    base_url: str
    timeout: int = ProviderDefaults.HTTP_TIMEOUT
    headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize default headers if not provided."""
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


class BaseConfiguredProvider(ABC, ProviderProtocol):
    """Base class for configured AI providers.

    This class eliminates code duplication by providing:
    - Standardized HTTP handling with httpx
    - Common error handling patterns
    - Flexible configuration via ProviderConfig
    - Template methods for customization

    Implements ProviderProtocol for type safety.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._api_key: str | None = None  # Lazy load

    @property
    def api_key(self) -> str:
        """Lazy-load API key when needed."""
        if self.config.api_key_env:
            # Always check environment for fresh value to support test isolation
            return self._get_api_key()
        return ""

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self.config.name

    @property
    def api_key_env(self) -> str:
        """Get the environment variable name for the API key."""
        return self.config.api_key_env

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self.config.base_url

    @property
    def timeout(self) -> int:
        """Get the timeout in seconds."""
        return self.config.timeout

    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise AIError.authentication_error(f"{self.config.api_key_env} not found in environment variables")
        return api_key

    @abstractmethod
    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build the request body for the API call.

        Args:
            messages: List of message dictionaries
            temperature: Temperature parameter
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Request body dictionary
        """
        pass

    @abstractmethod
    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse the API response and extract content.

        Args:
            response: Response dictionary from API

        Returns:
            Generated text content
        """
        pass

    def _build_headers(self) -> dict[str, str]:
        """Build headers for the API request.

        Can be overridden by subclasses to add provider-specific headers.
        """
        headers = self.config.headers.copy() if self.config.headers else {}
        return headers

    def _get_api_url(self, model: str | None = None) -> str:
        """Get the API URL for the request.

        Can be overridden by subclasses for dynamic URLs.

        Args:
            model: Model name (for providers that need model-specific URLs)

        Returns:
            API URL string
        """
        return self.config.base_url

    def _make_http_request(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        """Make the HTTP request.

        Error handling is delegated to the @handle_provider_errors decorator
        which wraps the provider's API function. This avoids duplicate exception
        handling and ensures consistent error classification across all providers.

        Args:
            url: API URL
            body: Request body
            headers: Request headers

        Returns:
            Response JSON dictionary

        Raises:
            httpx.HTTPStatusError: For HTTP errors (handled by decorator)
            httpx.TimeoutException: For timeout errors (handled by decorator)
            httpx.RequestError: For network errors (handled by decorator)
        """
        response = httpx.post(url, json=body, headers=headers, timeout=self.config.timeout, verify=get_ssl_verify())
        response.raise_for_status()
        return response.json()

    def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Generate text using the AI provider.

        Error handling is delegated to the @handle_provider_errors decorator
        which wraps the provider's API function. This ensures consistent error
        classification across all providers.

        Args:
            model: Model name to use
            messages: List of message dictionaries
            temperature: Temperature parameter (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text content

        Raises:
            AIError: For any API-related errors (via decorator)
        """
        logger.debug(f"Generating with {self.config.name} provider (model={model})")

        # Build request components
        url = self._get_api_url(model)
        headers = self._build_headers()
        body = self._build_request_body(messages, temperature, max_tokens, model, **kwargs)

        # Add model to body if not already present
        if "model" not in body:
            body["model"] = model

        # Make HTTP request
        response_data = self._make_http_request(url, body, headers)

        # Parse response
        return self._parse_response(response_data)


class OpenAICompatibleProvider(BaseConfiguredProvider):
    """Base class for OpenAI-compatible providers.

    Handles standard OpenAI API format with minimal customization needed.
    """

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build OpenAI-style request body.

        Note: Subclasses should override this if they need max_completion_tokens
        instead of max_tokens (like OpenAI provider does).
        """
        return {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}

    def _build_headers(self) -> dict[str, str]:
        """Build headers with OpenAI-style authorization."""
        headers = super()._build_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse OpenAI-style response."""
        choices = response.get("choices")
        if not choices or not isinstance(choices, list):
            raise AIError.model_error("Invalid response: missing choices")
        content = choices[0].get("message", {}).get("content")
        if content is None:
            raise AIError.model_error("Invalid response: null content")
        if content == "":
            raise AIError.model_error("Invalid response: empty content")
        return content


class AnthropicCompatibleProvider(BaseConfiguredProvider):
    """Base class for Anthropic-compatible providers."""

    def _build_headers(self) -> dict[str, str]:
        """Build headers with Anthropic-style authorization."""
        headers = super()._build_headers()
        api_key = self._get_api_key()
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
        return headers

    def _get_api_url(self, model: str | None = None) -> str:
        """Get Anthropic API URL with /messages endpoint."""
        if self.config.base_url.endswith("messages"):
            return self.config.base_url
        if self.config.base_url.endswith("/"):
            return f"{self.config.base_url}messages"
        return f"{self.config.base_url}/messages"

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Build Anthropic-style request body."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = ""

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        body = {"messages": anthropic_messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}

        if system_message:
            body["system"] = system_message

        return body

    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse Anthropic-style response."""
        content = response.get("content")
        if not content or not isinstance(content, list):
            raise AIError.model_error("Invalid response: missing content")

        text_content = content[0].get("text")
        if text_content is None:
            raise AIError.model_error("Invalid response: null content")
        if text_content == "":
            raise AIError.model_error("Invalid response: empty content")
        return text_content


class GenericHTTPProvider(BaseConfiguredProvider):
    """Base class for completely custom providers."""

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Default implementation - override this in subclasses."""
        return {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}

    def _parse_response(self, response: dict[str, Any]) -> str:
        """Default implementation - override this in subclasses."""
        # Try OpenAI-style first
        choices = response.get("choices")
        if choices and isinstance(choices, list):
            content = choices[0].get("message", {}).get("content")
            if content:
                return content

        # Try Anthropic-style
        content = response.get("content")
        if content and isinstance(content, list):
            return content[0].get("text", "")

        # Try Ollama-style
        message = response.get("message", {})
        if "content" in message:
            return message["content"]

        # Fallback - try to find any string content
        for value in response.values():
            if isinstance(value, str) and len(value) > 10:  # Assume longer strings are content
                return value

        raise AIError.model_error("Could not extract content from response")


__all__ = [
    "AnthropicCompatibleProvider",
    "BaseConfiguredProvider",
    "GenericHTTPProvider",
    "OpenAICompatibleProvider",
    "ProviderConfig",
]
