"""Tests for Custom OpenAI provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError
from gac.providers.custom_openai import call_custom_openai_api
from tests.provider_test_utils import assert_missing_api_key_error, temporarily_remove_env_var
from tests.providers.conftest import BaseProviderTest


class TestCustomOpenAIImports:
    """Test that Custom OpenAI provider can be imported."""

    def test_import_provider(self):
        """Test that Custom OpenAI provider module can be imported."""

    def test_import_api_function(self):
        """Test that Custom OpenAI API function can be imported."""


class TestCustomOpenAIAPIKeyValidation:
    """Test Custom OpenAI API key validation."""

    def test_missing_api_key_error(self):
        """Test that Custom OpenAI raises error when API key is missing."""
        with temporarily_remove_env_var("CUSTOM_OPENAI_API_KEY"):
            with patch.dict(os.environ, {"CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}):
                with pytest.raises(AIError) as exc_info:
                    call_custom_openai_api("gpt-4", [], 0.7, 1000)

                assert_missing_api_key_error(exc_info, "custom openai", "CUSTOM_OPENAI_API_KEY")

    def test_missing_base_url_error(self):
        """Test that Custom OpenAI raises error when base URL is missing."""
        with temporarily_remove_env_var("CUSTOM_OPENAI_BASE_URL"):
            with patch.dict(os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key"}):
                with pytest.raises(AIError) as exc_info:
                    call_custom_openai_api("gpt-4", [], 0.7, 1000)

                assert exc_info.value.error_type == "model"
                assert "CUSTOM_OPENAI_BASE_URL" in str(exc_info.value)


class TestCustomOpenAIProviderMocked(BaseProviderTest):
    """Mocked tests for Custom OpenAI provider."""

    @property
    def provider_name(self) -> str:
        return "custom-openai"

    @property
    def provider_module(self) -> str:
        return "gac.providers.custom_openai"

    @property
    def api_function(self) -> Callable:
        return call_custom_openai_api

    @property
    def api_key_env_var(self) -> str | None:
        return "CUSTOM_OPENAI_API_KEY"

    @property
    def model_name(self) -> str:
        return "gpt-4"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    def test_successful_api_call(self):
        """Test that the provider successfully processes a valid API response."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.success_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
                result = self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

            assert result == "feat: Add new feature"
            mock_post.assert_called_once()

    def test_empty_content_handling(self):
        """Test that the provider raises an error for empty content."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.return_value = self._create_mock_response(self.empty_content_response)

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
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

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
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

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
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

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
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

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_connection_error(self):
        """Test that the provider handles connection errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
                with pytest.raises(AIError):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)

    def test_timeout_error(self):
        """Test that the provider handles timeout errors."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            messages = [{"role": "user", "content": "Generate a commit message"}]

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
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

            with patch.dict(
                os.environ, {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
            ):
                with pytest.raises((AIError, ValueError, KeyError, TypeError)):
                    self.api_function(model=self.model_name, messages=messages, temperature=0.7, max_tokens=100)


class TestCustomOpenAIEdgeCases:
    """Test edge cases for Custom OpenAI provider."""

    def test_custom_openai_null_content(self):
        """Test handling of null content."""
        with patch.dict(
            "os.environ", {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com"}
        ):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_custom_openai_api("gpt-4", [], 0.7, 1000)

                assert "null content" in str(exc_info.value).lower()

    def test_base_url_trailing_slash_handling(self):
        """Test that trailing slashes in base URL are handled correctly."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_OPENAI_API_KEY": "test-key", "CUSTOM_OPENAI_BASE_URL": "https://api.example.com/"},
        ):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_openai_api("gpt-4", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                assert called_url == "https://api.example.com/chat/completions"

    def test_base_url_with_full_path_included(self):
        """Test that full endpoint path in base URL is preserved."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_OPENAI_API_KEY": "test-key",
                "CUSTOM_OPENAI_BASE_URL": "https://api.example.com/v1/chat/completions",
            },
        ):
            with patch("httpx.post") as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                call_custom_openai_api("gpt-4", [], 0.7, 1000)

                called_url = mock_post.call_args[0][0]
                assert called_url == "https://api.example.com/v1/chat/completions"


@pytest.mark.integration
class TestCustomOpenAIIntegration:
    """Integration tests for Custom OpenAI provider."""

    def test_real_api_call(self):
        """Test actual Custom OpenAI API call with valid credentials."""
        api_key = os.getenv("CUSTOM_OPENAI_API_KEY")
        base_url = os.getenv("CUSTOM_OPENAI_BASE_URL")

        if not api_key or not base_url:
            pytest.skip("CUSTOM_OPENAI_API_KEY and CUSTOM_OPENAI_BASE_URL not set - skipping real API test")

        messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
        # Use synthetic.new endpoint with GLM-4.6 model
        response = call_custom_openai_api(
            model="hf:zai-org/GLM-4.6", messages=messages, temperature=1.0, max_tokens=1024
        )

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
