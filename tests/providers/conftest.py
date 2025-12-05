"""Shared test fixtures and base classes for provider tests."""

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError


class BaseProviderTest(ABC):
    """Base test class defining standard test scenarios all providers should implement.

    Subclasses must define:
    - provider_name: Name of the provider (e.g., "openai")
    - provider_module: Module path (e.g., "gac.providers.openai")
    - api_function: The provider's API call function
    - api_key_env_var: Environment variable for API key (optional, None if not required)
    - model_name: Default model to use in tests
    - success_response: Mock response for successful API call
    - empty_content_response: Mock response with empty content

    Optional:
    - auth_context(): Override to provide custom authentication context (e.g., for OAuth providers)
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'openai')."""
        pass

    @property
    @abstractmethod
    def provider_module(self) -> str:
        """Module path for patching (e.g., 'gac.providers.openai')."""
        pass

    @property
    @abstractmethod
    def api_function(self) -> Callable:
        """The provider's API call function."""
        pass

    @property
    @abstractmethod
    def api_key_env_var(self) -> str | None:
        """Environment variable for API key, or None if not required."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Default model name for tests."""
        pass

    @property
    @abstractmethod
    def success_response(self) -> dict[str, Any]:
        """Mock response for successful API call."""
        pass

    @property
    @abstractmethod
    def empty_content_response(self) -> dict[str, Any]:
        """Mock response with empty content."""
        pass

    @contextmanager
    def auth_context(self):
        """Context manager for authentication setup.

        Override this for OAuth-only providers that don't use environment variables.
        Default implementation uses api_key_env_var to set up environment.
        """
        if self.api_key_env_var:
            with patch.dict(os.environ, {self.api_key_env_var: "test-key"}):
                yield
        else:
            yield

    def _create_mock_response(self, response_data: dict[str, Any]) -> MagicMock:
        """Create a mock HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        return mock_response

    def test_successful_api_call(self):
        """Test that the provider successfully processes a valid API response."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                result = self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

            assert result == "feat: Add new feature"
            mock_post.assert_called_once()

    def test_empty_content_handling(self):
        """Test that the provider raises an error for empty content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.empty_content_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(Exception) as exc_info:
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

                error_msg = str(exc_info.value).lower()
                assert "empty content" in error_msg or "missing" in error_msg

    def test_http_401_authentication_error(self):
        """Test that the provider handles HTTP 401 authentication errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_429_rate_limit_error(self):
        """Test that the provider handles HTTP 429 rate limit errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_post.side_effect = httpx.HTTPStatusError(
                "429 Rate limit exceeded", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_500_server_error(self):
        """Test that the provider handles HTTP 500 server errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.side_effect = httpx.HTTPStatusError(
                "500 Internal server error", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_http_503_service_unavailable(self):
        """Test that the provider handles HTTP 503 service unavailable errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service unavailable"
            mock_post.side_effect = httpx.HTTPStatusError(
                "503 Service unavailable", request=MagicMock(), response=mock_response
            )

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_connection_error(self):
        """Test that the provider handles connection errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_timeout_error(self):
        """Test that the provider handles timeout errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_malformed_json_response(self):
        """Test that the provider handles malformed JSON responses."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with self.auth_context():
                with pytest.raises((AIError, ValueError, KeyError, TypeError)):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)
