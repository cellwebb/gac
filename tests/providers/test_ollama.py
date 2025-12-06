"""Tests for Ollama provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_import_success
from tests.providers.conftest import BaseProviderTest

call_ollama_api = PROVIDER_REGISTRY["ollama"]


class TestOllamaImports:
    """Test that Ollama provider can be imported."""

    def test_import_provider(self):
        """Test that Ollama provider module can be imported."""
        from gac.providers import ollama  # noqa: F401

    def test_provider_in_registry(self):
        """Test that Ollama provider is in the registry."""
        assert "ollama" in PROVIDER_REGISTRY
        assert_import_success(PROVIDER_REGISTRY["ollama"])


class TestOllamaProviderMocked(BaseProviderTest):
    """Mocked tests for Ollama provider."""

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def provider_module(self) -> str:
        return "gac.providers.ollama"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["ollama"]

    @property
    def api_key_env_var(self) -> str | None:
        return "OLLAMA_API_KEY"

    @property
    def model_name(self) -> str:
        return "llama2"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"response": "feat: Add new feature"}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"response": ""}


class TestOllamaEdgeCases:
    """Test edge cases for Ollama provider."""

    def test_ollama_message_content_format(self):
        """Test response with message.content format."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"message": {"content": "test response"}}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_ollama_api("llama2", [], 0.7, 1000)
            assert result == "test response"

    def test_ollama_response_format(self):
        """Test response with response field format."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "test response"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_ollama_api("llama2", [], 0.7, 1000)
            assert result == "test response"

    def test_ollama_fallback_string_format(self):
        """Test fallback to string conversion for unexpected format."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"other_field": "some value"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_ollama_api("llama2", [], 0.7, 1000)
            assert "other_field" in result

    def test_ollama_null_content(self):
        """Test handling of null content in message."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"message": {"content": None}}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_ollama_api("llama2", [], 0.7, 1000)

            assert "null content" in str(exc_info.value).lower()

    def test_ollama_custom_api_url(self):
        """Test custom OLLAMA_API_URL environment variable."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "test response"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"OLLAMA_API_URL": "http://custom:8080"}):
                result = call_ollama_api("llama2", [], 0.7, 1000)

            # Verify custom URL was used
            call_args = mock_post.call_args
            assert "http://custom:8080/api/chat" in call_args[0][0]
            assert result == "test response"

    def test_ollama_with_api_key(self):
        """Test that API key is included in headers when provided."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "test response"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"OLLAMA_API_KEY": "test-key"}):
                result = call_ollama_api("llama2", [], 0.7, 1000)

            # Verify Authorization header was included
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-key"
            assert result == "test response"

    def test_ollama_connection_error(self):
        """Test handling of connection error when Ollama is not running."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(AIError) as exc_info:
                call_ollama_api("llama2", [], 0.7, 1000)

            error_msg = str(exc_info.value).lower()
            assert "network error" in error_msg or "connection" in error_msg


@pytest.mark.integration
class TestOllamaIntegration:
    """Integration tests for Ollama provider."""

    def test_real_api_call(self):
        """Test actual Ollama API call with local instance."""
        api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        try:
            response = httpx.get(f"{api_url.rstrip('/')}/api/tags", timeout=2)
            if response.status_code != 200:
                pytest.skip("Ollama is not running - skipping real API test")
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Ollama is not running - skipping real API test")

        try:
            messages = [{"role": "user", "content": "Say 'test success' and nothing else."}]
            response = call_ollama_api(model="gpt-oss:20b", messages=messages, temperature=1.0, max_tokens=50)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except AIError as e:
            error_str = str(e).lower()
            if "not found" in error_str:
                pytest.skip(f"Ollama model not found - skipping real API test: {e}")
            raise
