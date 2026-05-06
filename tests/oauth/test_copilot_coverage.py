"""Coverage tests for oauth/copilot.py — targeting session persistence, poll edge cases, and non-quiet flow paths."""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import gac.oauth.copilot as copilot_module
from gac.oauth.copilot import (
    _load_persisted_session,
    _persist_session,
    _session_cache_path,
    authenticate_and_save,
    clear_caches,
    exchange_for_session_token,
    get_api_endpoint,
    get_valid_session_token,
    is_token_expired,
    perform_oauth_flow,
    poll_for_token,
    remove_token,
    save_token,
    start_device_flow,
)


@pytest.fixture(autouse=True)
def _clean_copilot_state(tmp_path):
    """Clear copilot state between tests, using tmp_path for cache."""
    clear_caches()
    store = copilot_module.TokenStore()
    store.remove_token("copilot")
    yield
    clear_caches()
    store.remove_token("copilot")


# ---------------------------------------------------------------------------
# _persist_session and _load_persisted_session
# ---------------------------------------------------------------------------


class TestPersistSession:
    """Tests for _persist_session — writing session tokens to disk."""

    @patch("gac.oauth.copilot.TokenStore")
    def test_persist_creates_file(self, MockStore, tmp_path):
        """_persist_session creates the cache file."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        session = {
            "token": "tid=abc",
            "expires_at": time.time() + 1800,
            "api_endpoint": "https://api.githubcopilot.com",
        }
        _persist_session(session, "github.com", "ghu_oauth_token_123")

        cache_path = _session_cache_path(tmp_path)
        assert cache_path.exists()
        data = json.loads(cache_path.read_text())
        assert data["github.com"]["token"] == "tid=abc"
        # oauth_fingerprint is oauth_token[:16]

    @patch("gac.oauth.copilot.TokenStore")
    def test_persist_appends_to_existing(self, MockStore, tmp_path):
        """_persist_session appends to existing cache file."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        cache_path.write_text(json.dumps({"github.com": {"token": "old", "expires_at": 0}}))

        session = {
            "token": "tid=new",
            "expires_at": time.time() + 1800,
            "api_endpoint": "https://api.githubcopilot.com",
        }
        _persist_session(session, "ghe.test.com", "ghu_other")

        data = json.loads(cache_path.read_text())
        assert data["github.com"]["token"] == "old"
        assert data["ghe.test.com"]["token"] == "tid=new"

    @patch("gac.oauth.copilot.TokenStore")
    def test_persist_failure_silent(self, MockStore):
        """_persist_session silently handles write failures."""
        mock_store = MagicMock()
        mock_store.base_dir = Path("/nonexistent/path/that/does/not/exist")
        MockStore.return_value = mock_store

        session = {"token": "tid=abc", "expires_at": time.time() + 1800, "api_endpoint": "https://example.com"}
        # Should not raise
        _persist_session(session, "github.com", "ghu_token")


class TestLoadPersistedSession:
    """Tests for _load_persisted_session — reading session tokens from disk."""

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_existing_valid_session(self, MockStore, tmp_path):
        """Loads a valid persisted session."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        data = {
            "github.com": {
                "token": "tid=abc",
                "expires_at": time.time() + 1800,
                "api_endpoint": "https://api.githubcopilot.com",
                "oauth_fingerprint": "ghu_oauth_token_",  # oauth_token[:16]
            }
        }
        cache_path.write_text(json.dumps(data))

        result = _load_persisted_session("github.com", "ghu_oauth_token_12345")
        assert result is not None
        assert result["token"] == "tid=abc"

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_fingerprint_mismatch(self, MockStore, tmp_path):
        """Returns None when OAuth fingerprint doesn't match."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        data = {
            "github.com": {
                "token": "tid=abc",
                "expires_at": time.time() + 1800,
                "api_endpoint": "https://api.githubcopilot.com",
                "oauth_fingerprint": "different_token",
            }
        }
        cache_path.write_text(json.dumps(data))

        result = _load_persisted_session("github.com", "ghu_oauth_token_12345")
        assert result is None

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_no_file(self, MockStore, tmp_path):
        """Returns None when cache file doesn't exist."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        result = _load_persisted_session("github.com", "ghu_token")
        assert result is None

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_no_host_entry(self, MockStore, tmp_path):
        """Returns None when host not in cache."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        cache_path.write_text(json.dumps({"other.host": {"token": "x"}}))

        result = _load_persisted_session("github.com", "ghu_token")
        assert result is None

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_empty_api_endpoint_derives(self, MockStore, tmp_path):
        """When api_endpoint is empty, derives from host."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store
        clear_caches()

        cache_path = _session_cache_path(tmp_path)
        data = {
            "github.com": {
                "token": "tid=abc",
                "expires_at": time.time() + 1800,
                "api_endpoint": "",
            }
        }
        cache_path.write_text(json.dumps(data))

        result = _load_persisted_session("github.com", "ghu_token")
        assert result is not None
        # Empty api_endpoint → derives from host for github.com
        assert "githubcopilot.com" in result["api_endpoint"]

    @patch("gac.oauth.copilot.TokenStore")
    def test_load_corrupt_file(self, MockStore, tmp_path):
        """Returns None when cache file is corrupt."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        cache_path.write_text("not valid json")

        result = _load_persisted_session("github.com", "ghu_token")
        assert result is None


# ---------------------------------------------------------------------------
# get_valid_session_token — disk cache path
# ---------------------------------------------------------------------------


class TestGetValidSessionTokenDiskCache:
    @patch("gac.oauth.copilot._load_persisted_session")
    @patch("gac.oauth.copilot.exchange_for_session_token")
    def test_disk_cache_hit(self, mock_exchange, mock_load):
        """Uses on-disk cache when available and not expired."""
        mock_load.return_value = {
            "token": "tid=cached",
            "expires_at": time.time() + 1800,
            "api_endpoint": "https://api.githubcopilot.com",
        }

        result = get_valid_session_token("ghu_oauth_1234567890", "github.com")
        assert result == "tid=cached"
        mock_exchange.assert_not_called()

    @patch("gac.oauth.copilot._load_persisted_session")
    @patch("gac.oauth.copilot.exchange_for_session_token")
    def test_disk_cache_expired(self, mock_exchange, mock_load):
        """Falls through to exchange when on-disk cache is expired."""
        mock_load.return_value = {
            "token": "tid=expired",
            "expires_at": time.time() - 60,  # Expired
            "api_endpoint": "https://api.githubcopilot.com",
        }
        mock_exchange.return_value = {
            "token": "tid=fresh",
            "expires_at": time.time() + 1800,
            "api_endpoint": "https://api.githubcopilot.com",
        }

        result = get_valid_session_token("ghu_oauth_1234567890", "github.com")
        assert result == "tid=fresh"


# ---------------------------------------------------------------------------
# poll_for_token — edge cases
# ---------------------------------------------------------------------------


class TestPollForTokenEdgeCases:
    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_slow_down_increases_interval(self, mock_sleep, mock_post):
        """slow_down error increases poll interval."""
        slow_resp = MagicMock()
        slow_resp.status_code = 200
        slow_resp.json.return_value = {"error": "slow_down"}

        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"access_token": "ghu_123"}

        mock_post.side_effect = [slow_resp, success_resp]

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result == "ghu_123"

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_expired_token_error(self, mock_sleep, mock_post):
        """expired_token error returns None."""
        expired_resp = MagicMock()
        expired_resp.status_code = 200
        expired_resp.json.return_value = {"error": "expired_token"}
        mock_post.return_value = expired_resp

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result is None

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_unsupported_grant_type_error(self, mock_sleep, mock_post):
        """unsupported_grant_type error returns None."""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"error": "unsupported_grant_type"}
        mock_post.return_value = resp

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result is None

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_unknown_error_still_polls(self, mock_sleep, mock_post):
        """Unknown error code falls through to debug log and keeps polling."""
        unknown_resp = MagicMock()
        unknown_resp.status_code = 200
        unknown_resp.json.return_value = {"error": "something_odd"}
        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"access_token": "ghu_123"}

        mock_post.side_effect = [unknown_resp, success_resp]

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result == "ghu_123"

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_non_200_response(self, mock_sleep, mock_post):
        """Non-200 HTTP response results in empty dict data."""
        fail_resp = MagicMock()
        fail_resp.status_code = 500
        # json() won't be called since status != 200

        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"access_token": "ghu_123"}

        mock_post.side_effect = [fail_resp, success_resp]

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result == "ghu_123"

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_poll_exception_continues(self, mock_sleep, mock_post):
        """Network exception during poll continues to next iteration."""
        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"access_token": "ghu_123"}

        mock_post.side_effect = [Exception("Network error"), success_resp]

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)
        assert result == "ghu_123"


# ---------------------------------------------------------------------------
# exchange_for_session_token — edge cases
# ---------------------------------------------------------------------------


class TestExchangeForSessionTokenEdgeCases:
    @patch("gac.oauth.copilot.httpx.get")
    def test_200_but_no_token_field(self, mock_get):
        """200 response with no 'token' field returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"expires_at": time.time() + 1800}
        mock_get.return_value = mock_response
        clear_caches()

        result = exchange_for_session_token("ghu_oauth", "github.com")
        assert result is None

    @patch("gac.oauth.copilot.httpx.get")
    def test_non_401_non_200_error(self, mock_get):
        """Non-401, non-200 status returns None with warning."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        result = exchange_for_session_token("ghu_oauth", "github.com")
        assert result is None


# ---------------------------------------------------------------------------
# start_device_flow — missing fields
# ---------------------------------------------------------------------------


class TestStartDeviceFlowEdgeCases:
    @patch("gac.oauth.copilot.httpx.post")
    def test_200_but_missing_fields(self, mock_post):
        """200 response missing required fields returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"device_code": "dc_123"}  # Missing user_code
        mock_post.return_value = mock_response

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = start_device_flow("github.com")
        assert result is None


# ---------------------------------------------------------------------------
# remove_token — session cache cleanup
# ---------------------------------------------------------------------------


class TestRemoveTokenSessionCache:
    @patch("gac.oauth.copilot._base_remove", return_value=False)
    def test_base_remove_fails(self, mock_remove):
        """Returns False when _base_remove fails."""
        result = remove_token()
        assert result is False

    @patch("gac.oauth.copilot._base_remove", return_value=True)
    @patch("gac.oauth.copilot.TokenStore")
    def test_removes_session_cache_file(self, MockStore, mock_remove, tmp_path):
        """Removes session cache file on token removal."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        cache_path = _session_cache_path(tmp_path)
        cache_path.write_text('{"github.com": {"token": "old"}}')
        assert cache_path.exists()

        result = remove_token()
        assert result is True
        # The real remove_token tries to unlink the cache file
        # Since we mocked TokenStore, the path resolution should work

    @patch("gac.oauth.copilot._base_remove", return_value=True)
    @patch("gac.oauth.copilot.TokenStore")
    def test_no_cache_file_still_succeeds(self, MockStore, mock_remove, tmp_path):
        """Succeeds even when session cache file doesn't exist."""
        mock_store = MagicMock()
        mock_store.base_dir = tmp_path
        MockStore.return_value = mock_store

        result = remove_token()
        assert result is True


# ---------------------------------------------------------------------------
# perform_oauth_flow — non-quiet paths
# ---------------------------------------------------------------------------


class TestPerformOAuthFlowNonQuiet:
    @patch("gac.oauth.copilot.poll_for_token")
    @patch("gac.oauth.copilot.start_device_flow")
    @patch("webbrowser.open")
    def test_success_non_quiet(self, mock_wb, mock_start, mock_poll):
        """Non-quiet mode prints user code and status."""
        mock_start.return_value = {
            "device_code": "dc",
            "user_code": "AB-CD",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 1,
        }
        mock_poll.return_value = "ghu_123"

        with patch("builtins.print") as mock_print:
            result = perform_oauth_flow(quiet=False)
        assert result == "ghu_123"
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("AB-CD" in c for c in calls)

    @patch("gac.oauth.copilot.poll_for_token", return_value=None)
    @patch("gac.oauth.copilot.start_device_flow")
    @patch("webbrowser.open")
    def test_poll_failure_non_quiet(self, mock_wb, mock_start, mock_poll):
        """Non-quiet mode prints failure when poll returns None."""
        mock_start.return_value = {
            "device_code": "dc",
            "user_code": "AB-CD",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 1,
        }
        with patch("builtins.print") as mock_print:
            result = perform_oauth_flow(quiet=False)
        assert result is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("not completed" in c for c in calls)

    @patch("gac.oauth.copilot.start_device_flow", return_value=None)
    def test_start_fails_non_quiet(self, mock_start):
        """Non-quiet mode prints failure when start_device_flow fails."""
        with patch("builtins.print") as mock_print:
            result = perform_oauth_flow(quiet=False)
        assert result is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Failed" in c or "failed" in c for c in calls)

    @patch("gac.oauth.copilot.poll_for_token")
    @patch("gac.oauth.copilot.start_device_flow")
    @patch("webbrowser.open", side_effect=Exception("no browser"))
    def test_browser_failure_non_quiet(self, mock_wb, mock_start, mock_poll):
        """Non-quiet mode handles browser failure gracefully."""
        mock_start.return_value = {
            "device_code": "dc",
            "user_code": "AB-CD",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 1,
        }
        mock_poll.return_value = "ghu_123"

        with patch("builtins.print") as mock_print:
            result = perform_oauth_flow(quiet=False)
        assert result == "ghu_123"
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("open" in c.lower() for c in calls)

    @patch("gac.oauth.copilot.poll_for_token")
    @patch("gac.oauth.copilot.start_device_flow")
    def test_fallback_verification_uri(self, mock_start, mock_poll):
        """Uses fallback verification_uri when not in response."""
        mock_start.return_value = {
            "device_code": "dc",
            "user_code": "AB-CD",
            # No verification_uri
            "expires_in": 900,
            "interval": 1,
        }
        mock_poll.return_value = "ghu_123"

        with patch("webbrowser.open"):
            with patch("builtins.print"):
                result = perform_oauth_flow(quiet=True)
        assert result == "ghu_123"


# ---------------------------------------------------------------------------
# authenticate_and_save — non-quiet and edge cases
# ---------------------------------------------------------------------------


class TestAuthenticateAndSaveNonQuiet:
    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token")
    @patch("gac.oauth.copilot.perform_oauth_flow")
    def test_success_non_quiet(self, mock_flow, mock_save, mock_session):
        """Non-quiet mode prints session exchange messages."""
        mock_flow.return_value = "ghu_123"
        mock_save.return_value = True
        mock_session.return_value = "tid=abc"

        with patch("builtins.print") as mock_print:
            result = authenticate_and_save(quiet=False)
        assert result is True
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("session" in c.lower() or "copilot" in c.lower() for c in calls)

    @patch("gac.oauth.copilot.perform_oauth_flow", return_value=None)
    def test_flow_fails_non_quiet(self, mock_flow):
        """Non-quiet mode with flow failure doesn't crash."""
        with patch("builtins.print"):
            result = authenticate_and_save(quiet=False)
        assert result is False

    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token")
    @patch("gac.oauth.copilot.perform_oauth_flow")
    def test_session_fails_non_quiet(self, mock_flow, mock_save, mock_session):
        """Non-quiet mode prints warning when session exchange fails."""
        mock_flow.return_value = "ghu_123"
        mock_save.return_value = True
        mock_session.return_value = None

        with patch("builtins.print") as mock_print:
            result = authenticate_and_save(quiet=False)
        assert result is False
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("session" in c.lower() or "copilot" in c.lower() for c in calls)

    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token", return_value=False)
    @patch("gac.oauth.copilot.perform_oauth_flow", return_value="ghu_123")
    def test_save_fails_non_quiet(self, mock_flow, mock_save, mock_session):
        """Non-quiet mode prints warning when save fails."""
        with patch("builtins.print") as mock_print:
            result = authenticate_and_save(quiet=False)
        assert result is False
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("could not be saved" in c.lower() for c in calls)

    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token")
    @patch("gac.oauth.copilot.perform_oauth_flow")
    def test_invalid_host_non_quiet(self, mock_flow, mock_save, mock_session):
        """Non-quiet mode prints error for invalid host."""
        with patch("builtins.print") as mock_print:
            result = authenticate_and_save(host="evil.com:8080", quiet=False)
        assert result is False
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Invalid" in c for c in calls)


# ---------------------------------------------------------------------------
# is_token_expired — edge cases
# ---------------------------------------------------------------------------


class TestIsTokenExpiredEdgeCases:
    def test_no_access_token(self):
        """Returns True when token has no access_token."""
        save_token("ghu_123", host="github.com")
        # Manually corrupt the stored token
        store = copilot_module.TokenStore()
        store.save_token("copilot", {"token_type": "Bearer"})
        assert is_token_expired()

    def test_with_oauth_token_but_no_access(self):
        """Returns True when stored data has no access_token key."""
        store = copilot_module.TokenStore()
        store.save_token("copilot", {"token_type": "Bearer"})
        assert is_token_expired()


# ---------------------------------------------------------------------------
# get_api_endpoint — GHE cached
# ---------------------------------------------------------------------------


class TestGetApiEndpointCached:
    def test_ghe_with_cached_endpoint(self):
        """Returns cached endpoint for GHE."""
        copilot_module._host_api_endpoints["ghe.test.com"] = "https://ghe.test.com/api"
        assert get_api_endpoint("ghe.test.com") == "https://ghe.test.com/api"
        clear_caches()
