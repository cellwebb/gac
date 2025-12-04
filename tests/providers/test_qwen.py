"""Tests for Qwen provider."""

from unittest import mock

import httpx
import pytest

from gac.errors import AIError
from gac.providers.qwen import call_qwen_api, get_qwen_auth


class TestGetQwenAuth:
    """Tests for get_qwen_auth function."""

    def test_uses_api_key_when_available(self, monkeypatch):
        """Test that API key is used when available."""
        monkeypatch.setenv("QWEN_API_KEY", "test_api_key")
        token, url = get_qwen_auth()
        assert token == "test_api_key"
        assert "qwen" in url.lower()

    @mock.patch("gac.providers.qwen.QwenOAuthProvider")
    def test_uses_oauth_when_no_api_key(self, mock_provider_class, monkeypatch):
        """Test that OAuth is used when no API key is available."""
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        mock_provider = mock.Mock()
        mock_provider.get_token.return_value = {
            "access_token": "oauth_token",
            "resource_url": "portal.qwen.ai",
        }
        mock_provider_class.return_value = mock_provider

        token, url = get_qwen_auth()
        assert token == "oauth_token"
        assert url == "https://portal.qwen.ai/v1/chat/completions"

    @mock.patch("gac.providers.qwen.QwenOAuthProvider")
    def test_error_when_no_auth(self, mock_provider_class, monkeypatch):
        """Test that error is raised when no auth is available."""
        monkeypatch.delenv("QWEN_API_KEY", raising=False)
        mock_provider = mock.Mock()
        mock_provider.get_token.return_value = None
        mock_provider_class.return_value = mock_provider

        with pytest.raises(AIError) as exc_info:
            get_qwen_auth()

        assert exc_info.value.error_type == "authentication"


class TestCallQwenApi:
    """Tests for call_qwen_api function."""

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_successful_api_call(self, mock_post, mock_auth):
        """Test successful API call."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_response = mock.Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        mock_post.return_value = mock_response

        result = call_qwen_api(
            model="qwen3-coder-plus",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=100,
        )

        assert result == "Test response"
        mock_post.assert_called_once()

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_null_content_error(self, mock_post, mock_auth):
        """Test error when API returns null content."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_response = mock.Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}
        mock_post.return_value = mock_response

        with pytest.raises(AIError) as exc_info:
            call_qwen_api(
                model="qwen3-coder-plus",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
            )

        assert exc_info.value.error_type == "model"
        assert "null" in str(exc_info.value).lower()

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_empty_content_error(self, mock_post, mock_auth):
        """Test error when API returns empty content."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_response = mock.Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": ""}}]}
        mock_post.return_value = mock_response

        with pytest.raises(AIError) as exc_info:
            call_qwen_api(
                model="qwen3-coder-plus",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
            )

        assert exc_info.value.error_type == "model"
        assert "empty" in str(exc_info.value).lower()

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_authentication_error(self, mock_post, mock_auth):
        """Test 401 authentication error."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=mock.Mock(),
            response=mock_response,
        )

        with pytest.raises(AIError) as exc_info:
            call_qwen_api(
                model="qwen3-coder-plus",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
            )

        assert exc_info.value.error_type == "authentication"

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_rate_limit_error(self, mock_post, mock_auth):
        """Test 429 rate limit error."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_response = mock.Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=mock.Mock(),
            response=mock_response,
        )

        with pytest.raises(AIError) as exc_info:
            call_qwen_api(
                model="qwen3-coder-plus",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
            )

        assert exc_info.value.error_type == "rate_limit"

    @mock.patch("gac.providers.qwen.get_qwen_auth")
    @mock.patch("gac.providers.qwen.httpx.post")
    def test_timeout_error(self, mock_post, mock_auth):
        """Test timeout error."""
        mock_auth.return_value = ("test_token", "https://api.qwen.ai/v1/chat/completions")
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(AIError) as exc_info:
            call_qwen_api(
                model="qwen3-coder-plus",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=100,
            )

        assert exc_info.value.error_type == "timeout"
