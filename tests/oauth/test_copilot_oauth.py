"""Tests for GitHub Copilot OAuth — Device Flow, session exchange, token CRUD."""

import time
from unittest.mock import MagicMock, patch

import pytest

import gac.oauth.copilot as copilot_module
from gac.oauth.copilot import (
    COPILOT_OAUTH_CONFIG,
    DEFAULT_COPILOT_MODELS,
    DEVICE_FLOW_CONFIG,
    _normalize_host,
    _require_valid_host,
    _session_cache_path,
    authenticate_and_save,
    clear_caches,
    exchange_for_session_token,
    get_api_endpoint,
    get_valid_session_token,
    is_token_expired,
    load_stored_token,
    load_stored_tokens,
    perform_oauth_flow,
    poll_for_token,
    refresh_token_if_expired,
    remove_token,
    save_token,
    start_device_flow,
)

PROVIDER_KEY = "copilot"


@pytest.fixture(autouse=True)
def _clean_copilot_state():
    """Clear copilot token, session cache, and in-memory caches between tests."""
    clear_caches()
    # Use the copilot module's own remove_token to clean up (same TokenStore)
    from gac.oauth import copilot as _cop

    _store = _cop.TokenStore()
    _store.remove_token(PROVIDER_KEY)
    # Clear persisted session cache file
    actual_path = _session_cache_path(_store.base_dir)
    if actual_path.exists():
        actual_path.unlink()
    yield
    clear_caches()
    _store.remove_token(PROVIDER_KEY)
    if actual_path.exists():
        actual_path.unlink()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_values(self):
        assert COPILOT_OAUTH_CONFIG["api_base_url"] == "https://api.githubcopilot.com"
        assert DEVICE_FLOW_CONFIG["client_id"] == "Iv1.b507a08c87ecfe98"

    def test_default_models(self):
        assert "gpt-4.1" in DEFAULT_COPILOT_MODELS
        assert "claude-opus-4.6" in DEFAULT_COPILOT_MODELS
        assert "gemini-2.5-pro" in DEFAULT_COPILOT_MODELS


# ---------------------------------------------------------------------------
# Host normalization (security-critical)
# ---------------------------------------------------------------------------


class TestNormalizeHost:
    def test_empty_returns_github(self):
        assert _normalize_host("") == "github.com"

    def test_github_com(self):
        assert _normalize_host("github.com") == "github.com"

    def test_ghe_host(self):
        assert _normalize_host("ghe.mycompany.com") == "ghe.mycompany.com"

    def test_uppercase_normalized(self):
        assert _normalize_host("GitHub.com") == "github.com"

    def test_rejects_scheme(self):
        assert _normalize_host("https://evil.com") is None

    def test_rejects_path(self):
        assert _normalize_host("github.com/evil") is None

    def test_rejects_credentials(self):
        assert _normalize_host("user@attacker.tld") is None

    def test_rejects_query(self):
        assert _normalize_host("host?q=1") is None

    def test_strips_trailing_dot(self):
        assert _normalize_host("github.com.") == "github.com"

    def test_rejects_port(self):
        """Port numbers allow SSRF to internal services."""
        assert _normalize_host("evil.com:8080") is None

    def test_rejects_percent_encoding(self):
        """Percent-encoded null bytes can confuse HTTP parsers."""
        assert _normalize_host("evil.com%00.github.com") is None

    def test_rejects_crlf_tab(self):
        """CRLF / tab injection."""
        assert _normalize_host("evil.com\r\nHost:evil") is None
        assert _normalize_host("evil.com\textra") is None

    def test_rejects_backslash(self):
        assert _normalize_host("evil.com\\path") is None

    def test_rejects_bare_dots(self):
        """'...' is not a valid hostname."""
        assert _normalize_host("....") is None

    def test_rejects_starts_with_hyphen(self):
        assert _normalize_host("-evil.com") is None

    def test_rejects_starts_with_dot(self):
        assert _normalize_host(".evil.com") is None

    def test_rejects_localhost(self):
        """localhost could point to local services."""
        assert _normalize_host("localhost") is None

    def test_rejects_loopback_ip(self):
        """127.x.x.x is loopback — SSRF to local services."""
        assert _normalize_host("127.0.0.1") is None

    def test_rejects_private_10(self):
        """10.x.x.x is RFC 1918 private."""
        assert _normalize_host("10.0.0.1") is None

    def test_rejects_private_172(self):
        """172.16-31.x.x is RFC 1918 private."""
        assert _normalize_host("172.16.0.1") is None
        assert _normalize_host("172.31.255.1") is None

    def test_rejects_private_192(self):
        """192.168.x.x is RFC 1918 private."""
        assert _normalize_host("192.168.1.1") is None

    def test_allows_ghe_hostname(self):
        """Legitimate GHE hostnames still pass."""
        assert _normalize_host("ghe.mycompany.com") == "ghe.mycompany.com"
        assert _normalize_host("github.my-enterprise.org") == "github.my-enterprise.org"


class TestRequireValidHost:
    def test_valid(self):
        assert _require_valid_host("github.com") == "github.com"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid or unsafe hostname"):
            _require_valid_host("evil.com:8080")

    def test_empty_returns_github(self):
        assert _require_valid_host("") == "github.com"


# ---------------------------------------------------------------------------
# Device Flow
# ---------------------------------------------------------------------------


class TestStartDeviceFlow:
    @patch("gac.oauth.copilot.httpx.post")
    def test_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "device_code": "dc_123",
            "user_code": "ABCD-1234",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 5,
        }
        mock_post.return_value = mock_response

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = start_device_flow("github.com")

        assert result is not None
        assert result["device_code"] == "dc_123"
        assert result["user_code"] == "ABCD-1234"

    @patch("gac.oauth.copilot.httpx.post")
    def test_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            assert start_device_flow("github.com") is None

    @patch("gac.oauth.copilot.httpx.post")
    def test_exception(self, mock_post):
        mock_post.side_effect = Exception("Network error")

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            assert start_device_flow("github.com") is None

    def test_invalid_host_rejected(self):
        """Invalid host never makes a network call."""
        result = start_device_flow("evil.com:8080")
        assert result is None


class TestPollForToken:
    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_success(self, mock_sleep, mock_post):
        # First poll returns pending, second returns token
        pending_resp = MagicMock()
        pending_resp.status_code = 200
        pending_resp.json.return_value = {"error": "authorization_pending"}

        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"access_token": "ghu_12345"}

        mock_post.side_effect = [pending_resp, success_resp]

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)

        assert result == "ghu_12345"

    @patch("gac.oauth.copilot.httpx.post")
    @patch("gac.oauth.copilot.time.sleep")
    def test_denied(self, mock_sleep, mock_post):
        denied_resp = MagicMock()
        denied_resp.status_code = 200
        denied_resp.json.return_value = {"error": "access_denied"}
        mock_post.return_value = denied_resp

        with patch("gac.oauth.copilot.get_ssl_verify", return_value=True):
            result = poll_for_token("dc_123", interval=1, expires_in=30)

        assert result is None

    def test_invalid_host_rejected(self):
        """Invalid host never makes a network call."""
        result = poll_for_token("dc_123", host="evil.com:8080", interval=1, expires_in=30)
        assert result is None


# ---------------------------------------------------------------------------
# Session token exchange
# ---------------------------------------------------------------------------


class TestSessionTokenExchange:
    @patch("gac.oauth.copilot.httpx.get")
    def test_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "tid=abc123",
            "expires_at": time.time() + 1800,
            "endpoints": {"api": "https://api.githubcopilot.com"},
        }
        mock_get.return_value = mock_response

        result = exchange_for_session_token("ghu_oauth", "github.com")
        assert result is not None
        assert result["token"] == "tid=abc123"
        assert "api.githubcopilot.com" in result["api_endpoint"]

    @patch("gac.oauth.copilot.httpx.get")
    def test_ghe_fallback(self, mock_get):
        """GHE without endpoints.api falls back to the host itself."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "tid=ghe",
            "expires_at": time.time() + 1800,
            # No "endpoints" key
        }
        mock_get.return_value = mock_response
        clear_caches()

        result = exchange_for_session_token("ghu_oauth", "ghe.company.com")
        assert result is not None
        assert result["api_endpoint"] == "https://ghe.company.com"

    @patch("gac.oauth.copilot.httpx.get")
    def test_401(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = exchange_for_session_token("ghu_oauth", "github.com")
        assert result is None

    @patch("gac.oauth.copilot.httpx.get")
    def test_exception(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        result = exchange_for_session_token("ghu_oauth", "github.com")
        assert result is None


class TestGetValidSessionToken:
    def test_no_oauth_token(self):
        assert refresh_token_if_expired(quiet=True) is False

    @patch("gac.oauth.copilot.exchange_for_session_token")
    def test_exchange_success(self, mock_exchange):
        mock_exchange.return_value = {
            "token": "tid=abc",
            "expires_at": time.time() + 1800,
            "api_endpoint": "https://api.githubcopilot.com",
        }
        save_token("ghu_oauth", host="github.com")
        result = get_valid_session_token("ghu_oauth", "github.com")
        assert result == "tid=abc"

    @patch("gac.oauth.copilot.exchange_for_session_token")
    def test_exchange_failure(self, mock_exchange):
        mock_exchange.return_value = None
        save_token("ghu_oauth", host="github.com")
        result = get_valid_session_token("ghu_oauth", "github.com")
        assert result is None


# ---------------------------------------------------------------------------
# Token CRUD
# ---------------------------------------------------------------------------


class TestTokenCRUD:
    def test_save_and_load(self):
        assert save_token("ghu_123", host="github.com")
        assert load_stored_token() == "ghu_123"

    def test_save_with_user(self):
        assert save_token("ghu_123", host="github.com", user="octocat")
        tokens = load_stored_tokens()
        assert tokens is not None
        assert tokens["host"] == "github.com"
        assert tokens["user"] == "octocat"

    def test_load_stored_tokens_none(self):
        assert load_stored_tokens() is None

    def test_remove(self):
        save_token("ghu_123", host="github.com")
        assert remove_token()
        assert load_stored_token() is None

    def test_is_token_expired_no_token(self):
        assert is_token_expired()

    def test_is_token_expired_with_token(self):
        save_token("ghu_123", host="github.com")
        assert not is_token_expired()


# ---------------------------------------------------------------------------
# refresh_token_if_expired
# ---------------------------------------------------------------------------


class TestRefreshTokenIfExpired:
    def test_no_token(self):
        assert refresh_token_if_expired(quiet=True) is False

    @patch("gac.oauth.copilot.get_valid_session_token")
    def test_session_valid(self, mock_session):
        mock_session.return_value = "tid=abc"
        save_token("ghu_oauth", host="github.com")
        assert refresh_token_if_expired(quiet=True) is True

    @patch("gac.oauth.copilot.get_valid_session_token")
    def test_session_invalid(self, mock_session):
        mock_session.return_value = None
        save_token("ghu_oauth", host="github.com")
        assert refresh_token_if_expired(quiet=True) is False


# ---------------------------------------------------------------------------
# clear_caches
# ---------------------------------------------------------------------------


class TestClearCaches:
    def test_clears_caches(self):
        copilot_module._session_cache["test"] = {"token": "x"}
        copilot_module._host_api_endpoints["github.com"] = "https://example.com"
        clear_caches()
        assert len(copilot_module._session_cache) == 0
        assert len(copilot_module._host_api_endpoints) == 0


# ---------------------------------------------------------------------------
# get_api_endpoint
# ---------------------------------------------------------------------------


class TestGetApiEndpoint:
    def test_default_github(self):
        clear_caches()
        assert get_api_endpoint("github.com") == "https://api.githubcopilot.com"

    def test_default_ghe(self):
        clear_caches()
        assert get_api_endpoint("ghe.company.com") == "https://ghe.company.com"

    def test_cached(self):
        copilot_module._host_api_endpoints["ghe.test"] = "https://ghe.test/api"
        assert get_api_endpoint("ghe.test") == "https://ghe.test/api"
        clear_caches()


# ---------------------------------------------------------------------------
# perform_oauth_flow (delegation)
# ---------------------------------------------------------------------------


class TestPerformOAuthFlow:
    @patch("gac.oauth.copilot.poll_for_token")
    @patch("gac.oauth.copilot.start_device_flow")
    @patch("webbrowser.open")
    def test_success(self, mock_wb, mock_start, mock_poll):
        mock_start.return_value = {
            "device_code": "dc",
            "user_code": "AB-CD",
            "verification_uri": "https://github.com/login/device",
            "expires_in": 900,
            "interval": 1,
        }
        mock_poll.return_value = "ghu_123"

        result = perform_oauth_flow(quiet=True)
        assert result == "ghu_123"

    @patch("gac.oauth.copilot.start_device_flow", return_value=None)
    def test_start_fails(self, mock_start):
        result = perform_oauth_flow(quiet=True)
        assert result is None

    def test_invalid_host_rejected(self):
        """Invalid host is caught before any network call."""
        result = perform_oauth_flow(host="evil.com:8080", quiet=True)
        assert result is None


class TestAuthenticateAndSave:
    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token")
    @patch("gac.oauth.copilot.perform_oauth_flow")
    def test_success(self, mock_flow, mock_save, mock_session):
        mock_flow.return_value = "ghu_123"
        mock_save.return_value = True
        mock_session.return_value = "tid=abc"

        assert authenticate_and_save(quiet=True) is True

    @patch("gac.oauth.copilot.perform_oauth_flow", return_value=None)
    def test_flow_fails(self, mock_flow):
        assert authenticate_and_save(quiet=True) is False

    @patch("gac.oauth.copilot.get_valid_session_token")
    @patch("gac.oauth.copilot.save_token")
    @patch("gac.oauth.copilot.perform_oauth_flow")
    def test_session_fails(self, mock_flow, mock_save, mock_session):
        mock_flow.return_value = "ghu_123"
        mock_save.return_value = True
        mock_session.return_value = None

        assert authenticate_and_save(quiet=True) is False

    def test_invalid_host_rejected(self):
        """Invalid host is caught before any network call."""
        assert authenticate_and_save(host="evil.com:8080", quiet=True) is False
