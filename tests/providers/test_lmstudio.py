"""Tests for LM Studio provider."""

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY
from tests.provider_test_utils import assert_import_success, temporarily_set_env_var
from tests.providers.conftest import BaseProviderTest

call_lmstudio_api = PROVIDER_REGISTRY["lm-studio"]


class TestLMStudioImports:
    """Test that LM Studio provider can be imported."""

    def test_import_provider(self):
        """Test that LM Studio provider module can be imported."""
        from gac.providers import lmstudio  # noqa: F401

    def test_provider_in_registry(self):
        """Test that LM Studio provider is in the registry."""
        assert "lm-studio" in PROVIDER_REGISTRY
        assert_import_success(PROVIDER_REGISTRY["lm-studio"])


class TestLMStudioProviderMocked(BaseProviderTest):
    """Mocked tests for LM Studio provider."""

    @property
    def provider_name(self) -> str:
        return "lmstudio"

    @property
    def provider_module(self) -> str:
        return "gac.providers.lmstudio"

    @property
    def api_function(self) -> Callable:
        return PROVIDER_REGISTRY["lm-studio"]

    @property
    def api_key_env_var(self) -> str | None:
        return "LMSTUDIO_API_KEY"

    @property
    def model_name(self) -> str:
        return "local-model"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}


class TestLMStudioEdgeCases:
    """Test edge cases for LM Studio provider."""

    def test_lmstudio_missing_choices(self):
        """Test handling of response without choices field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"some_other_field": "value"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_lmstudio_api("local-model", [], 0.7, 1000)

            assert "missing choices" in str(exc_info.value).lower()

    def test_lmstudio_empty_choices(self):
        """Test handling of empty choices array."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_lmstudio_api("local-model", [], 0.7, 1000)

            assert "missing choices" in str(exc_info.value).lower()

    def test_lmstudio_missing_message_and_text(self):
        """Test handling of choice without message or text field."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"other_field": "value"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with pytest.raises(AIError) as exc_info:
                call_lmstudio_api("local-model", [], 0.7, 1000)

            assert "missing content" in str(exc_info.value).lower()

    def test_lmstudio_text_field_fallback(self):
        """Test fallback to text field when message.content not present."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"text": "test response"}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            result = call_lmstudio_api("local-model", [], 0.7, 1000)
            assert result == "test response"

    def test_lmstudio_custom_api_url(self):
        """Test custom LMSTUDIO_API_URL environment variable."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"LMSTUDIO_API_URL": "http://custom:8080"}):
                result = call_lmstudio_api("local-model", [], 0.7, 1000)

            # Verify custom URL was used
            call_args = mock_post.call_args
            assert "http://custom:8080/v1/chat/completions" in call_args[0][0]
            assert result == "test response"

    def test_lmstudio_with_api_key(self):
        """Test that API key is included in headers when provided."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"LMSTUDIO_API_KEY": "test-key"}):
                result = call_lmstudio_api("local-model", [], 0.7, 1000)

            # Verify Authorization header was included
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-key"
            assert result == "test response"

    def test_lmstudio_without_api_key(self):
        """Test that Authorization header is not included when no API key."""
        with patch("gac.providers.base.httpx.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            # Ensure LMSTUDIO_API_KEY is not set
            with patch.dict(os.environ, {}, clear=False):
                if "LMSTUDIO_API_KEY" in os.environ:
                    del os.environ["LMSTUDIO_API_KEY"]
                result = call_lmstudio_api("local-model", [], 0.7, 1000)

            # Verify Authorization header was not included
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert "Authorization" not in headers
            assert result == "test response"


@pytest.mark.integration
class TestLMStudioIntegration:
    """Integration tests for LM Studio provider."""

    def test_connection_error(self):
        """Test that call_lmstudio_api raises connection error when server is unreachable."""
        with temporarily_set_env_var("LMSTUDIO_API_URL", "http://127.0.0.1:9"):
            with pytest.raises(AIError) as exc_info:
                messages = [{"role": "user", "content": "test prompt"}]
                call_lmstudio_api(model="local-model", messages=messages, temperature=1.0, max_tokens=20)
            assert "network error" in str(exc_info.value).lower() or "connection" in str(exc_info.value).lower()
