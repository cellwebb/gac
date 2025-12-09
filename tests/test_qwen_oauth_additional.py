"""Additional tests to improve qwen_oauth.py coverage."""

import time
from unittest import mock
from unittest.mock import Mock

import pytest

from gac.errors import AIError
from gac.oauth.qwen_oauth import DeviceCodeResponse, QwenDeviceFlow, QwenOAuthProvider


class TestQwenOAuthMissingCoverage:
    """Test missing coverage areas in Qwen OAuth implementation."""

    def test_generate_pkce_valid_output(self):
        """Test PKCE generation produces valid base64url strings."""
        flow = QwenDeviceFlow()
        verifier, challenge = flow._generate_pkce()

        # Verify PKCE properties
        assert len(verifier) == 43  # 32 bytes base64url encoded
        assert len(challenge) == 43  # SHA256 hash base64url encoded
        assert verifier != challenge

    def test_initiate_device_flow_with_scopes(self):
        """Test device flow initiation with custom scopes."""
        flow = QwenDeviceFlow()
        flow.scopes = ["custom-scope"]

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

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            mock_post.return_value = mock_response

            result = flow.initiate_device_flow()

            assert isinstance(result, DeviceCodeResponse)
            # Verify scope was included in request
            call_args = mock_post.call_args
            assert "custom-scope" in call_args[1]["data"]["scope"]  # Check if scope is in the list

    def test_initiate_device_flow_no_scopes(self):
        """Test device flow initiation without scopes."""
        flow = QwenDeviceFlow()
        flow.scopes = []

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "TEST-CODE",
            "verification_uri": "https://chat.qwen.ai/activate",
            "expires_in": 600,
        }

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            mock_post.return_value = mock_response

            result = flow.initiate_device_flow()

            assert isinstance(result, DeviceCodeResponse)
            # Verify scope was not included when empty
            call_args = mock_post.call_args
            assert "scope" not in call_args[1]["data"]

    def test_poll_for_token_slow_down_error(self):
        """Test polling with slow_down error increases interval."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        # Mock responses: slow_down first, then success
        slow_response = mock.Mock()
        slow_response.is_success = False
        slow_response.json.return_value = {"error": "slow_down"}

        success_response = mock.Mock()
        success_response.is_success = True
        success_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            with mock.patch("gac.oauth.qwen_oauth.time.sleep") as mock_sleep:
                mock_post.side_effect = [slow_response, success_response]

                result = flow.poll_for_token("device_code")

                assert result["access_token"] == "test_access_token"
                # Verify sleep was called with increased interval
                mock_sleep.assert_called()
                # Should have been called twice (slow_down + success)
                assert mock_post.call_count == 2

    def test_poll_for_token_expired_token_error(self):
        """Test polling with expired_token error."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        expired_response = mock.Mock()
        expired_response.is_success = False
        expired_response.json.return_value = {"error": "expired_token"}

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            mock_post.return_value = expired_response

            with pytest.raises(AIError) as exc_info:
                flow.poll_for_token("device_code")

            assert "Device code expired" in str(exc_info.value)

    def test_poll_for_token_connection_error(self):
        """Test polling with connection error that gets retried."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        # Mock request error first, then success
        from httpx import RequestError

        request_error = RequestError("Connection failed")

        success_response = mock.Mock()
        success_response.is_success = True
        success_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            with mock.patch("gac.oauth.qwen_oauth.time.sleep") as mock_sleep:
                mock_post.side_effect = [request_error, success_response]

                result = flow.poll_for_token("device_code")

                assert result["access_token"] == "test_access_token"
                # Verify retry happened
                assert mock_post.call_count == 2
                mock_sleep.assert_called()

    def test_poll_for_token_timeout_exceeded(self):
        """Test polling timeout."""
        flow = QwenDeviceFlow()
        flow._pkce_verifier = "test_verifier"

        # Mock continuous authorization_pending responses
        pending_response = mock.Mock()
        pending_response.is_success = False
        pending_response.json.return_value = {"error": "authorization_pending"}

        with mock.patch("gac.oauth.qwen_oauth.httpx.post") as mock_post:
            with mock.patch("gac.oauth.qwen_oauth.time.time", side_effect=[0, 0, 0, 1000]):  # Simulate timeout
                with mock.patch("gac.oauth.qwen_oauth.time.sleep"):
                    mock_post.return_value = pending_response

                    with pytest.raises(AIError) as exc_info:
                        flow.poll_for_token("device_code", max_duration=10)

                    assert "Authorization timeout" in str(exc_info.value)

    def test_should_launch_browser_ssh_environment(self):
        """Test browser launch detection with SSH environment."""
        flow = QwenOAuthProvider()

        with mock.patch("gac.oauth.qwen_oauth.os.getenv") as mock_getenv:
            # Simulate SSH environment
            mock_getenv.side_effect = lambda key: "ssh_session" if key in ["SSH_CLIENT", "SSH_TTY"] else None

            result = flow._should_launch_browser()

            assert result is False

    def test_should_launch_browser_no_display(self):
        """Test browser launch detection without display (Linux)."""
        flow = QwenOAuthProvider()

        with mock.patch("gac.oauth.qwen_oauth.os.getenv") as mock_getenv:
            with mock.patch("gac.oauth.qwen_oauth.os.uname") as mock_uname:
                # Simulate no DISPLAY on non-Darwin system
                mock_getenv.side_effect = lambda key: None if key == "DISPLAY" else ""
                mock_uname.return_value = mock.Mock(sysname="Linux")

                result = flow._should_launch_browser()

                assert result is False

    def test_should_launch_browser_success(self):
        """Test successful browser launch detection."""
        flow = QwenOAuthProvider()

        with mock.patch("gac.oauth.qwen_oauth.os.getenv") as mock_getenv:
            with mock.patch("gac.oauth.qwen_oauth.os.uname") as mock_uname:
                # Simulate normal environment
                mock_getenv.return_value = None
                mock_uname.return_value = mock.Mock(sysname="Darwin")

                result = flow._should_launch_browser()

                assert result is True

    def test_initiate_auth_browser_launch_failure(self):
        """Test auth flow when browser launch fails."""
        provider = QwenOAuthProvider()

        mock_response = mock.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "device_code": "test_device_code",
            "user_code": "TEST-CODE",
            "verification_uri": "https://chat.qwen.ai/activate",
            "expires_in": 600,
        }

        # Test that browser launch failure is handled gracefully
        with mock.patch.object(provider.device_flow, "initiate_device_flow", return_value=mock_response):
            with mock.patch("gac.oauth.qwen_oauth.webbrowser.open", side_effect=Exception("Browser failed")):
                with mock.patch("builtins.print") as mock_print:
                    with mock.patch("gac.oauth.qwen_oauth.time.sleep"):
                        # Just test that the method starts without error (mock the token polling)
                        with mock.patch.object(
                            provider.device_flow, "poll_for_token", return_value={"access_token": "test"}
                        ):
                            with mock.patch.object(provider.token_store, "save_token"):
                                provider.initiate_auth(open_browser=True)

                        # Verify fallback message was printed
                        assert any("Failed to open browser" in str(call) for call in mock_print.call_args_list)

    def test_refresh_if_needed_no_token(self):
        """Test refresh when no token exists."""
        provider = QwenOAuthProvider()

        with mock.patch.object(provider.token_store, "get_token", return_value=None):
            result = provider.refresh_if_needed()

            assert result is None

    def test_refresh_if_needed_valid_token(self):
        """Test refresh when token is still valid."""
        provider = QwenOAuthProvider()

        future_time = int(time.time()) + 3600  # Valid for another hour
        valid_token = {
            "access_token": "valid_token",
            "expiry": future_time,
            "token_type": "Bearer",
        }

        with mock.patch.object(provider.token_store, "get_token", return_value=valid_token):
            result = provider.refresh_if_needed()

            assert result == valid_token

    def test_refresh_if_needed_expired_no_refresh_token(self):
        """Test refresh when token is expired and has no refresh token."""
        provider = QwenOAuthProvider()

        past_time = int(time.time()) - 100  # Expired 100 seconds ago
        expired_token = {
            "access_token": "expired_token",
            "expiry": past_time,
            "token_type": "Bearer",
            # No refresh_token
        }

        with mock.patch.object(provider.token_store, "get_token", return_value=expired_token):
            with mock.patch.object(provider.token_store, "remove_token") as mock_remove:
                result = provider.refresh_if_needed()

                assert result is None
                mock_remove.assert_called_once()

    def test_refresh_if_needed_refresh_failure(self):
        """Test refresh when token refresh fails."""
        provider = QwenOAuthProvider()

        past_time = int(time.time()) - 100
        expired_token = {
            "access_token": "expired_token",
            "expiry": past_time,
            "token_type": "Bearer",
            "refresh_token": "refresh_token",
        }

        with mock.patch.object(provider.token_store, "get_token", return_value=expired_token):
            with mock.patch.object(provider.device_flow, "refresh_token", side_effect=Exception("Refresh failed")):
                with mock.patch.object(provider.token_store, "remove_token") as mock_remove:
                    result = provider.refresh_if_needed()

                    assert result is None
                    mock_remove.assert_called_once()

    def test_get_token_refreshes_when_expired(self):
        """Test get_token triggers refresh when expired."""
        provider = QwenOAuthProvider()

        past_time = int(time.time()) - 100
        expired_token = {
            "access_token": "expired_token",
            "expiry": past_time,
            "token_type": "Bearer",
            "refresh_token": "refresh_token",
        }

        new_token = {
            "access_token": "new_token",
            "expiry": int(time.time()) + 3600,
            "token_type": "Bearer",
        }

        with mock.patch.object(provider.token_store, "get_token", return_value=expired_token):
            with mock.patch.object(provider, "refresh_if_needed", return_value=new_token):
                result = provider.get_token()

                assert result == new_token

    def test_get_token_returns_none_when_refresh_fails(self):
        """Test get_token returns None when refresh fails."""
        provider = QwenOAuthProvider()

        past_time = int(time.time()) - 100
        expired_token = {
            "access_token": "expired_token",
            "expiry": past_time,
            "token_type": "Bearer",
            "refresh_token": "refresh_token",
        }

        with mock.patch.object(provider.token_store, "get_token", return_value=expired_token):
            with mock.patch.object(provider, "refresh_if_needed", return_value=None):
                result = provider.get_token()

                assert result is None


def mock_json_serializable(obj):
    """Convert Mock objects to serializable dicts for testing."""
    if isinstance(obj, Mock):
        return {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
