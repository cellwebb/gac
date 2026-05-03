"""Base configured provider class to eliminate code duplication."""

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from gac.ai_utils import count_tokens
from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.providers.protocol import ProviderProtocol
from gac.utils import get_ssl_verify


@dataclass
class ParsedResponse:
    """Structured result from parsing an API response.

    ``completion_tokens`` excludes reasoning tokens.  The provider APIs
    return ``completion_tokens`` inclusive of reasoning; we subtract
    ``reasoning_tokens`` at parse time so downstream code always gets two
    distinct, non-overlapping numbers.
    """

    content: str
    prompt_tokens: int = -1
    completion_tokens: int = -1  # output tokens only (excludes reasoning)
    reasoning_tokens: int = 0


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

    config: ProviderConfig

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
    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse the API response and extract content plus token counts.

        Args:
            response: Response dictionary from API

        Returns:
            ParsedResponse with content and optional token counts.
            Set prompt_tokens/completion_tokens to -1 to request estimation.
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
    ) -> tuple[str, int, int, int, int]:
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
            Tuple of (content, prompt_tokens, completion_tokens, duration_ms, reasoning_tokens)

        Raises:
            AIError: For any API-related errors (via decorator)
        """
        logger.debug(f"Generating with {self.config.name} provider (model={model})")

        url = self._get_api_url(model)
        headers = self._build_headers()
        body = self._build_request_body(messages, temperature, max_tokens, model, **kwargs)

        if "model" not in body:
            body["model"] = model

        start = time.perf_counter()
        response_data = self._make_http_request(url, body, headers)
        duration_ms = int((time.perf_counter() - start) * 1000)

        parsed = self._parse_response(response_data)
        prompt_tokens = parsed.prompt_tokens if parsed.prompt_tokens >= 0 else count_tokens(messages, model)
        completion_tokens = (
            parsed.completion_tokens if parsed.completion_tokens >= 0 else count_tokens(parsed.content, model)
        )

        return (parsed.content, prompt_tokens, completion_tokens, duration_ms, parsed.reasoning_tokens)


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

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse OpenAI-style response."""
        choices = response.get("choices")
        if not choices or not isinstance(choices, list):
            raise AIError.model_error("Invalid response: missing choices")
        content = choices[0].get("message", {}).get("content")
        if content is None:
            raise AIError.model_error("Invalid response: null content")
        if content == "":
            raise AIError.model_error("Invalid response: empty content")
        usage = response.get("usage")
        prompt_tokens = -1
        completion_tokens = -1
        reasoning_tokens = 0
        if isinstance(usage, dict):
            pt = usage.get("prompt_tokens", -1)
            ct = usage.get("completion_tokens", -1)
            prompt_tokens = pt if isinstance(pt, int) else -1
            completion_tokens = ct if isinstance(ct, int) else -1
            details = usage.get("completion_tokens_details")
            if isinstance(details, dict):
                rt = details.get("reasoning_tokens", 0)
                reasoning_tokens = rt if isinstance(rt, int) else 0
        return ParsedResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            # Normalize: API completion_tokens includes reasoning; subtract it
            # so downstream gets two distinct, non-overlapping numbers.
            completion_tokens=max(completion_tokens - reasoning_tokens, 0)
            if completion_tokens >= 0
            else completion_tokens,
            reasoning_tokens=reasoning_tokens,
        )


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

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Parse Anthropic-style response."""
        content = response.get("content")
        if not content or not isinstance(content, list):
            raise AIError.model_error("Invalid response: missing content")

        text_content = content[0].get("text")
        if text_content is None:
            raise AIError.model_error("Invalid response: null content")
        if text_content == "":
            raise AIError.model_error("Invalid response: empty content")
        usage = response.get("usage")
        prompt_tokens = -1
        completion_tokens = -1
        if isinstance(usage, dict):
            pt = usage.get("input_tokens", -1)
            ct = usage.get("output_tokens", -1)
            prompt_tokens = pt if isinstance(pt, int) else -1
            completion_tokens = ct if isinstance(ct, int) else -1
        return ParsedResponse(content=text_content, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)


class GenericHTTPProvider(BaseConfiguredProvider):
    """Base class for completely custom providers."""

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float, max_tokens: int, model: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Default implementation - override this in subclasses."""
        return {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, **kwargs}

    def _parse_response(self, response: dict[str, Any]) -> ParsedResponse:
        """Default implementation - override this in subclasses."""
        usage = response.get("usage")
        prompt_tokens: int = -1
        completion_tokens: int = -1
        reasoning_tokens: int = 0
        if isinstance(usage, dict):
            pt = usage.get("prompt_tokens", usage.get("input_tokens", -1))
            ct = usage.get("completion_tokens", usage.get("output_tokens", -1))
            prompt_tokens = pt if isinstance(pt, int) else -1
            completion_tokens = ct if isinstance(ct, int) else -1
            details = usage.get("completion_tokens_details")
            if isinstance(details, dict):
                rt = details.get("reasoning_tokens", 0)
                reasoning_tokens = rt if isinstance(rt, int) else 0

        # Normalize: API completion_tokens includes reasoning; subtract it
        # so downstream gets two distinct, non-overlapping numbers.
        norm_completion = max(completion_tokens - reasoning_tokens, 0) if completion_tokens >= 0 else completion_tokens

        choices = response.get("choices")
        if choices and isinstance(choices, list):
            content = choices[0].get("message", {}).get("content")
            if content:
                return ParsedResponse(
                    content=content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=norm_completion,
                    reasoning_tokens=reasoning_tokens,
                )

        content = response.get("content")
        if content and isinstance(content, list):
            return ParsedResponse(
                content=content[0].get("text", ""),
                prompt_tokens=prompt_tokens,
                completion_tokens=norm_completion,
                reasoning_tokens=reasoning_tokens,
            )

        message = response.get("message", {})
        if "content" in message:
            ollama_prompt = response.get("prompt_eval_count", -1)
            ollama_completion = response.get("eval_count", -1)
            return ParsedResponse(
                content=message["content"],
                prompt_tokens=ollama_prompt if isinstance(ollama_prompt, int) else -1,
                completion_tokens=ollama_completion if isinstance(ollama_completion, int) else -1,
            )

        for value in response.values():
            if isinstance(value, str) and len(value) > 10:
                return ParsedResponse(content=value, prompt_tokens=-1, completion_tokens=-1)

        raise AIError.model_error("Could not extract content from response")


__all__ = [
    "AnthropicCompatibleProvider",
    "BaseConfiguredProvider",
    "GenericHTTPProvider",
    "OpenAICompatibleProvider",
    "ParsedResponse",
    "ProviderConfig",
]
