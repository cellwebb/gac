"""Tests for qwen_oauth module."""

import time
from unittest import mock

import pytest

from gac.errors import AIError
from gac.oauth.qwen_oauth import (
    QWEN_CLIENT_ID,
    QWEN_DEVICE_CODE_ENDPOINT,
    QWEN_TOKEN_ENDPOINT,
    DeviceCodeResponse,
    QwenDeviceFlow,
    QwenOAuthProvider,
)
from gac.oauth.token_store import TokenStore


class TestQwenDeviceFlow:
    """Tests for QwenDeviceFlow class."""

    def test_init_defaults(self):
        """Test default initialization values."""
        flow = QwenDeviceFlow()
        assert flow.client_id == QWEN_CLIENT_ID
        assert flow.authorization_endpoint == QWEN_DEVICE_CODE_ENDPOINT
        assert flow.token_endpoint == QWEN_TOKEN_ENDPOINT
        assert "openid" in flow.scopes
        assert "model.completion" in flow.scopes

    def test_generate_pkce(self):
        """Test PKCE code verifier and challenge generation."""
        flow = QwenDeviceFlow()
        verifier, challenge = flow._generate_pkce()

        assert len(verifier) > 32
        assert len(challenge) > 32
        assert verifier != challenge

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_initiate_device_flow_success(self, mock_post):
        """Test successful device flow initiation."""
        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "TEST-CODE",
            "verification_uri": "https://chat.qwen.ai/activate",
            "verification_uri_complete": "https://chat.qwen.ai/activate?user_code=TEST-CODE",
            "expires_in": 600,
            "interval": 5,
        }
        mock_post.return_value = mock_response

        flow = QwenDeviceFlow()
        result = flow.initiate_device_flow()

        assert isinstance(result, DeviceCodeResponse)
        assert result.device_code == "test_device_code"
        assert result.user_code == "TEST-CODE"
        assert result.verification_uri == "https://chat.qwen.ai/activate"
        assert result.expires_in == 600

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_initiate_device_flow_error(self, mock_post):
        """Test device flow initiation failure."""
        mock_response = mock.Mock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        flow = QwenDeviceFlow()
        with pytest.raises(AIError) as exc_info:
            flow.initiate_device_flow()

        assert exc_info.value.error_type == "connection"

    @mock.patch("gac.oauth.qwen_oauth.time.sleep")
    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_poll_for_token_success(self, mock_post, mock_sleep):
        """Test successful token polling."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
            "scope": "openid profile",
            "resource_url": "https://api.qwen.ai",
        }
        mock_post.return_value = mock_response

        result = flow.poll_for_token("test_device_code")

        assert result["access_token"] == "test_access_token"
        assert result["refresh_token"] == "test_refresh_token"
        assert result["token_type"] == "Bearer"
        assert "expiry" in result

    @mock.patch("gac.oauth.qwen_oauth.time.sleep")
    @mock.patch("gac.oauth.qwen_oauth.time.time")
    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_poll_for_token_authorization_pending(self, mock_post, mock_time, mock_sleep):
        """Test token polling with authorization pending."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        mock_time.return_value = 0

        pending_response = mock.Mock()
        pending_response.is_success = False
        pending_response.json.return_value = {"error": "authorization_pending"}

        success_response = mock.Mock()
        success_response.is_success = True
        success_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        mock_post.side_effect = [pending_response, success_response]

        result = flow.poll_for_token("test_device_code")

        assert result["access_token"] == "test_access_token"
        mock_sleep.assert_called()

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_poll_for_token_access_denied(self, mock_post):
        """Test token polling when access is denied."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        mock_response = mock.Mock()
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "access_denied"}
        mock_post.return_value = mock_response

        with pytest.raises(AIError) as exc_info:
            flow.poll_for_token("test_device_code")

        assert exc_info.value.error_type == "authentication"

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        flow = QwenDeviceFlow()

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token",
        }
        mock_post.return_value = mock_response

        result = flow.refresh_token("old_refresh_token")

        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_refresh_token_keeps_old_refresh_token(self, mock_post):
        """Test that old refresh token is kept if new one not provided."""
        flow = QwenDeviceFlow()

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        result = flow.refresh_token("old_refresh_token")

        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "old_refresh_token"

    @mock.patch("gac.oauth.qwen_oauth.httpx.post")
    def test_refresh_token_failure(self, mock_post):
        """Test token refresh failure."""
        flow = QwenDeviceFlow()

        mock_response = mock.Mock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(AIError) as exc_info:
            flow.refresh_token("old_refresh_token")

        assert exc_info.value.error_type == "authentication"


class TestQwenOAuthProvider:
    """Tests for QwenOAuthProvider class."""

    def test_init_with_token_store(self, tmp_path):
        """Test initialization with custom token store."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        assert provider.token_store == token_store
        assert provider.name == "qwen"

    def test_init_default_token_store(self):
        """Test initialization with default token store."""
        with mock.patch("gac.oauth.qwen_oauth.TokenStore") as mock_store:
            QwenOAuthProvider()
            mock_store.assert_called_once()

    def test_is_token_expired_not_expired(self, tmp_path):
        """Test token expiry check for valid token."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        token = {
            "access_token": "test",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }
        assert not provider._is_token_expired(token)

    def test_is_token_expired_expired(self, tmp_path):
        """Test token expiry check for expired token."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        token = {
            "access_token": "test",
            "expiry": int(time.time()) - 100,
            "token_type": "Bearer",
        }
        assert provider._is_token_expired(token)

    def test_is_token_expired_within_buffer(self, tmp_path):
        """Test token expiry within 30-second buffer."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        token = {
            "access_token": "test",
            "expiry": int(time.time()) + 15,
            "token_type": "Bearer",
        }
        assert provider._is_token_expired(token)

    def test_get_token_not_authenticated(self, tmp_path):
        """Test getting token when not authenticated."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        assert provider.get_token() is None

    def test_get_token_valid(self, tmp_path):
        """Test getting valid token."""
        token_store = TokenStore(tmp_path)
        token = {
            "access_token": "test_token",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }
        token_store.save_token("qwen", token)

        provider = QwenOAuthProvider(token_store)
        result = provider.get_token()
        assert result["access_token"] == "test_token"

    def test_is_authenticated_true(self, tmp_path):
        """Test is_authenticated when token exists."""
        token_store = TokenStore(tmp_path)
        token = {
            "access_token": "test_token",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }
        token_store.save_token("qwen", token)

        provider = QwenOAuthProvider(token_store)
        assert provider.is_authenticated()

    def test_is_authenticated_false(self, tmp_path):
        """Test is_authenticated when no token."""
        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        assert not provider.is_authenticated()

    def test_logout(self, tmp_path, capsys):
        """Test logout removes token."""
        token_store = TokenStore(tmp_path)
        token = {
            "access_token": "test_token",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }
        token_store.save_token("qwen", token)

        provider = QwenOAuthProvider(token_store)
        assert provider.is_authenticated()

        provider.logout()

        assert not provider.is_authenticated()
        captured = capsys.readouterr()
        assert "logged out" in captured.out.lower()

    @mock.patch("gac.oauth.qwen_oauth.webbrowser.open")
    @mock.patch.object(QwenDeviceFlow, "poll_for_token")
    @mock.patch.object(QwenDeviceFlow, "initiate_device_flow")
    def test_initiate_auth_success(self, mock_initiate, mock_poll, mock_browser, tmp_path, capsys):
        """Test successful authentication initiation."""
        mock_initiate.return_value = DeviceCodeResponse(
            device_code="test_code",
            user_code="TEST-1234",
            verification_uri="https://chat.qwen.ai/activate",
            verification_uri_complete="https://chat.qwen.ai/activate?user_code=TEST-1234",
            expires_in=600,
        )
        mock_poll.return_value = {
            "access_token": "test_token",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }

        token_store = TokenStore(tmp_path)
        provider = QwenOAuthProvider(token_store)
        provider.initiate_auth()

        captured = capsys.readouterr()
        assert "TEST-1234" in captured.out
        assert provider.is_authenticated()
