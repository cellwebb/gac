"""Tests for Qwen provider."""

import os
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.errors import AIError
from gac.providers.qwen import call_qwen_api
from tests.provider_test_utils import assert_import_success
from tests.providers.conftest import BaseProviderTest


class TestQwenImports:
    """Test that Qwen provider can be imported."""

    def test_import_provider(self):
        """Test that Qwen provider module can be imported."""
        from gac.providers import qwen  # noqa: F401

    def test_import_api_function(self):
        """Test that Qwen API function can be imported and is callable."""
        from gac.providers.qwen import call_qwen_api

        assert_import_success(call_qwen_api)


class TestQwenOAuthValidation:
    """Test Qwen OAuth validation."""

    def test_missing_oauth_token_error(self):
        """Test that Qwen raises error when no OAuth token is available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
                mock_provider = mock.Mock()
                mock_provider.get_token.return_value = None
                mock_provider_class.return_value = mock_provider

                with pytest.raises(AIError) as exc_info:
                    call_qwen_api("qwen3-coder-plus", [], 0.7, 1000)

                assert exc_info.value.error_type == "authentication"


class TestQwenProviderMocked(BaseProviderTest):
    """Mocked tests for Qwen provider."""

    @property
    def provider_name(self) -> str:
        return "qwen"

    @property
    def provider_module(self) -> str:
        return "gac.providers.qwen"

    @property
    def api_function(self) -> Callable:
        return call_qwen_api

    @property
    def api_key_env_var(self) -> str | None:
        return None

    @property
    def model_name(self) -> str:
        return "qwen3-coder-plus"

    @property
    def success_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": "feat: Add new feature"}}]}

    @property
    def empty_content_response(self) -> dict[str, Any]:
        return {"choices": [{"message": {"content": ""}}]}

    @contextmanager
    def auth_context(self):
        """Set up OAuth mock for Qwen (OAuth-only provider)."""
        with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
            mock_oauth_provider = mock.Mock()
            mock_oauth_provider.get_token.return_value = {
                "access_token": "test-oauth-token",
                "resource_url": "chat.qwen.ai",
            }
            mock_provider_class.return_value = mock_oauth_provider
            yield


class TestQwenEdgeCases:
    """Test edge cases for Qwen provider."""

    def test_qwen_with_oauth(self):
        """Test Qwen using OAuth authentication."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
                with patch("gac.providers.base.httpx.post") as mock_post:
                    mock_oauth_provider = mock.Mock()
                    mock_oauth_provider.get_token.return_value = {
                        "access_token": "oauth_token_123",
                        "resource_url": "portal.qwen.ai",
                    }
                    mock_provider_class.return_value = mock_oauth_provider

                    mock_response = MagicMock()
                    mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
                    mock_response.raise_for_status = MagicMock()
                    mock_post.return_value = mock_response

                    result = call_qwen_api("qwen3-coder-plus", [], 0.7, 1000)

                    # Verify OAuth token was used
                    call_args = mock_post.call_args
                    headers = call_args.kwargs["headers"]
                    assert "Authorization" in headers
                    assert headers["Authorization"] == "Bearer oauth_token_123"
                    assert result == "test response"

    def test_qwen_oauth_with_dynamic_url(self):
        """Test Qwen OAuth with dynamic resource URL."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
                with patch("gac.providers.base.httpx.post") as mock_post:
                    mock_oauth_provider = mock.Mock()
                    mock_oauth_provider.get_token.return_value = {
                        "access_token": "oauth_token",
                        "resource_url": "custom.qwen.ai",  # Custom resource URL
                    }
                    mock_provider_class.return_value = mock_oauth_provider

                    mock_response = MagicMock()
                    mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
                    mock_response.raise_for_status = MagicMock()
                    mock_post.return_value = mock_response

                    result = call_qwen_api("qwen3-coder-plus", [], 0.7, 1000)

                    # Verify custom URL was used
                    call_args = mock_post.call_args
                    url = call_args[0][0]
                    assert "https://custom.qwen.ai/v1/chat/completions" == url
                    assert result == "test response"

    def test_qwen_missing_choices(self):
        """Test handling of response without choices field."""
        with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_oauth_provider = mock.Mock()
                mock_oauth_provider.get_token.return_value = {
                    "access_token": "test-oauth-token",
                    "resource_url": "chat.qwen.ai",
                }
                mock_provider_class.return_value = mock_oauth_provider

                mock_response = MagicMock()
                mock_response.json.return_value = {"some_other_field": "value"}
                mock_response.raise_for_status = MagicMock()
                mock_post.return_value = mock_response

                with pytest.raises(AIError) as exc_info:
                    call_qwen_api("qwen3-coder-plus", [], 0.7, 1000)

                assert "invalid response" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()

    def test_qwen_authentication_error(self):
        """Test 401 authentication error."""
        with patch("gac.providers.qwen.QwenOAuthProvider") as mock_provider_class:
            with patch("gac.providers.base.httpx.post") as mock_post:
                mock_oauth_provider = mock.Mock()
                mock_oauth_provider.get_token.return_value = {
                    "access_token": "test-oauth-token",
                    "resource_url": "chat.qwen.ai",
                }
                mock_provider_class.return_value = mock_oauth_provider

                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_response.text = "Unauthorized"
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "401 Unauthorized",
                    request=mock.Mock(),
                    response=mock_response,
                )
                mock_post.return_value = mock_response

                with pytest.raises(AIError):
                    call_qwen_api("qwen3-coder-plus", [], 0.7, 1000)
