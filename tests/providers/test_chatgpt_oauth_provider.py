"""Tests for ChatGPT OAuth provider (chatgpt_oauth.py)."""

from unittest.mock import patch

import pytest

from gac.errors import AIError
from gac.providers.chatgpt_oauth import ChatGPTOAuthProvider


def _make_provider(api_key="test_token"):
    """Create a ChatGPTOAuthProvider with a mocked _get_api_key."""
    provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
    provider.config = ChatGPTOAuthProvider.config
    provider._api_key = None
    provider._get_api_key = lambda: api_key  # type: ignore[assignment]
    return provider


class TestChatGPTOAuthProviderAPIKey:
    """Test _get_api_key method."""

    def test_get_api_key_refresh_fails(self):
        """When refresh fails, raise authentication error."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=False):
            provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
            provider.config = ChatGPTOAuthProvider.config
            with pytest.raises(AIError, match="ChatGPT OAuth token not found or expired"):
                provider._get_api_key()

    def test_get_api_key_refresh_succeeds_no_stored_token(self):
        """When refresh succeeds but no stored token, raise error."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=True):
            with patch("gac.providers.chatgpt_oauth.load_stored_token", return_value=None):
                provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
                provider.config = ChatGPTOAuthProvider.config
                with pytest.raises(AIError, match="ChatGPT OAuth authentication not found"):
                    provider._get_api_key()

    def test_get_api_key_success(self):
        """When refresh and load succeed, return token."""
        with patch("gac.providers.chatgpt_oauth.refresh_token_if_expired", return_value=True):
            with patch("gac.providers.chatgpt_oauth.load_stored_token", return_value="test_token_123"):
                provider = ChatGPTOAuthProvider.__new__(ChatGPTOAuthProvider)
                provider.config = ChatGPTOAuthProvider.config
                result = provider._get_api_key()
                assert result == "test_token_123"


class TestChatGPTOAuthProviderHeaders:
    """Test _build_headers method."""

    def test_build_headers_with_account_id(self):
        """Headers include ChatGPT-Account-Id when available."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value={"account_id": "acc-123"}):
            provider = _make_provider("test_token")
            headers = provider._build_headers()

            assert "ChatGPT-Account-Id" in headers
            assert headers["ChatGPT-Account-Id"] == "acc-123"
            assert "x-api-key" not in headers
            assert "originator" in headers
            assert "User-Agent" in headers

    def test_build_headers_without_account_id(self):
        """Headers omit ChatGPT-Account-Id when not available."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("test_token")
            headers = provider._build_headers()

            assert "ChatGPT-Account-Id" not in headers
            assert "originator" in headers

    def test_build_headers_authorization_bearer(self):
        """Authorization header uses Bearer token."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("my_token")
            headers = provider._build_headers()

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer my_token"

    def test_build_headers_removes_x_api_key(self):
        """x-api-key header is removed if present from parent."""
        with patch("gac.providers.chatgpt_oauth.load_stored_tokens", return_value=None):
            provider = _make_provider("my_token")
            headers = provider._build_headers()
            assert "x-api-key" not in headers


class TestChatGPTOAuthProviderAPIUrl:
    """Test _get_api_url method."""

    def test_api_url_with_chat_completions(self):
        """API URL includes /chat/completions."""
        provider = _make_provider()
        url = provider._get_api_url("gpt-5.4")
        assert url.endswith("/chat/completions")
        assert "chatgpt.com" in url


class TestChatGPTOAuthProviderRequestBody:
    """Test _build_request_body method."""

    def test_request_body_uses_max_completion_tokens(self):
        """Request body uses max_completion_tokens instead of max_tokens."""
        provider = _make_provider()

        body = provider._build_request_body(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7,
            max_tokens=1000,
            model="gpt-5.4",
        )

        assert "max_completion_tokens" in body
        assert "max_tokens" not in body
        assert body["max_completion_tokens"] == 1000
