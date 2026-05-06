"""Coverage tests for oauth/base.py — targeting refresh_oauth_token, build_auth_url fallbacks, start_callback_server, and flow branches."""

import base64
import json
import time
from unittest.mock import MagicMock, patch

import gac.oauth.base as base_module
from gac.oauth.base import (
    OAuthContext,
    _OAuthResult,
    authenticate_and_save,
    build_auth_url,
    is_token_expired,
    parse_jwt_claims,
    perform_oauth_flow,
    refresh_oauth_token,
    save_token,
    start_callback_server,
)

# ---------------------------------------------------------------------------
# refresh_oauth_token
# ---------------------------------------------------------------------------


class TestRefreshOAuthToken:
    """Tests for refresh_oauth_token — shared helper for HTTP-based token refresh."""

    def test_no_stored_tokens(self, fake_token_store):
        """Returns None when no tokens stored."""
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            result = refresh_oauth_token(
                "https://example.com/token",
                "client-123",
                "test-provider",
                "TEST_ENV",
            )
        assert result is None

    def test_no_refresh_token(self, fake_token_store):
        """Returns None when token data has no refresh_token."""
        fake_token_store.save_token("test-provider", {"access_token": "at", "token_type": "Bearer"})
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            result = refresh_oauth_token(
                "https://example.com/token",
                "client-123",
                "test-provider",
                "TEST_ENV",
            )
        assert result is None

    @patch("gac.oauth.base.httpx.post")
    def test_success(self, mock_post, fake_token_store):
        """Successful token refresh returns new access token."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-at",
            "refresh_token": "new-rt",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                )
        assert result == "new-at"

    @patch("gac.oauth.base.httpx.post")
    def test_success_with_client_secret(self, mock_post, fake_token_store):
        """Client secret is included in the request when provided."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new-at"}
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                    client_secret="secret-abc",
                )
        assert result == "new-at"
        call_data = mock_post.call_args[1]["data"]
        assert call_data["client_secret"] == "secret-abc"

    @patch("gac.oauth.base.httpx.post")
    def test_success_with_custom_save_fn(self, mock_post, fake_token_store):
        """Custom save_fn is used when provided."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new-at", "refresh_token": "new-rt"}
        mock_post.return_value = mock_response

        custom_save = MagicMock(return_value=True)
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                    save_fn=custom_save,
                )
        assert result == "new-at"
        custom_save.assert_called_once()

    @patch("gac.oauth.base.httpx.post")
    def test_success_with_expires_in(self, mock_post, fake_token_store):
        """expires_in in response sets expires_at in merged tokens."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-at",
            "refresh_token": "new-rt",
            "expires_in": 7200,
        }
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                )
        assert result == "new-at"

    @patch("gac.oauth.base.httpx.post")
    def test_http_error(self, mock_post, fake_token_store):
        """Non-200 HTTP response returns None."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                )
        assert result is None

    @patch("gac.oauth.base.httpx.post")
    def test_network_error(self, mock_post, fake_token_store):
        """Network exception returns None."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_post.side_effect = Exception("Connection refused")

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                )
        assert result is None

    @patch("gac.oauth.base.httpx.post")
    def test_no_access_token_in_response(self, mock_post, fake_token_store):
        """200 response with no access_token returns None."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"refresh_token": "new-rt"}
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                )
        assert result is None

    @patch("gac.oauth.base.httpx.post")
    def test_save_fails(self, mock_post, fake_token_store):
        """Successful refresh but save_token fails returns None."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new-at"}
        mock_post.return_value = mock_response

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.save_token", return_value=False):
                with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                    result = refresh_oauth_token(
                        "https://example.com/token",
                        "client-123",
                        "test-provider",
                        "TEST_ENV",
                    )
        assert result is None

    @patch("gac.oauth.base.httpx.post")
    def test_custom_save_fn_fails(self, mock_post, fake_token_store):
        """Successful refresh but custom save_fn returns False → None."""
        fake_token_store.save_token(
            "test-provider",
            {"access_token": "old-at", "token_type": "Bearer", "extra": {"refresh_token": "rt-123"}},
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new-at"}
        mock_post.return_value = mock_response

        custom_save = MagicMock(return_value=False)
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch("gac.oauth.base.get_ssl_verify", return_value=True):
                result = refresh_oauth_token(
                    "https://example.com/token",
                    "client-123",
                    "test-provider",
                    "TEST_ENV",
                    save_fn=custom_save,
                )
        assert result is None


# ---------------------------------------------------------------------------
# build_auth_url — issuer fallback path
# ---------------------------------------------------------------------------


class TestBuildAuthUrlFallback:
    def test_issuer_fallback_when_no_auth_url(self):
        """When auth_url is missing, falls back to issuer/oauth/authorize."""
        ctx = OAuthContext(
            state="s1",
            code_verifier="v1",
            code_challenge="c1",
            created_at=time.time(),
            redirect_uri="http://localhost:8765/callback",
        )
        config = {"issuer": "https://auth.example.com", "client_id": "cid", "scope": "openid"}
        url = build_auth_url(config, ctx)
        assert "auth.example.com/oauth/authorize" in url
        assert "code_challenge" in url

    def test_no_auth_url_no_issuer(self):
        """When both auth_url and issuer are missing, URL starts with empty string."""
        ctx = OAuthContext(
            state="s1",
            code_verifier="v1",
            code_challenge="c1",
            created_at=time.time(),
            redirect_uri="http://localhost:8765/callback",
        )
        config = {"client_id": "cid", "scope": "openid"}
        url = build_auth_url(config, ctx)
        assert "code_challenge" in url


# ---------------------------------------------------------------------------
# perform_oauth_flow — non-quiet output paths
# ---------------------------------------------------------------------------


CONFIG = {
    "auth_url": "https://example.com/auth",
    "client_id": "test-client",
    "scope": "openid",
    "redirect_host": "http://localhost",
    "redirect_path": "callback",
    "callback_port_range": (8765, 8767),
    "callback_timeout": 120,
    "provider_key": "test-provider",
    "api_key_env_var": "TEST_OAUTH_TOKEN",
}


def _make_context():
    return OAuthContext(
        state="correct-state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )


def _make_result(code="auth_code", state="correct-state", error=None):
    r = _OAuthResult()
    r.code = code
    r.state = state
    r.error = error
    return r


class TestPerformOAuthFlowNonQuiet:
    """Test perform_oauth_flow non-quiet output paths for coverage."""

    def test_server_startup_failure_non_quiet(self):
        """Prints error when server fails to start (non-quiet)."""
        with patch.object(base_module, "start_callback_server", return_value=None):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("builtins.print") as mock_print:
                    result = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert result is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Could not start" in c for c in calls)

    def test_timeout_non_quiet(self):
        """Prints timeout message (non-quiet)."""
        server = MagicMock()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = False

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("timed out" in c for c in calls)

    def test_callback_error_non_quiet(self):
        """Prints error message on callback error (non-quiet)."""
        server = MagicMock()
        result = _make_result(error="access_denied")
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("callback error" in c for c in calls)

    def test_state_mismatch_non_quiet(self):
        """Prints state mismatch message (non-quiet)."""
        server = MagicMock()
        result = _make_result(state="wrong-state")
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("State mismatch" in c for c in calls)

    def test_no_code_non_quiet(self):
        """Prints no-code message (non-quiet)."""
        server = MagicMock()
        result = _make_result(code=None)
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("No authorization code" in c for c in calls)

    def test_exchange_failure_non_quiet(self):
        """Prints exchange failure message (non-quiet)."""
        server = MagicMock()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value=None)
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out is None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Token exchange failed" in c for c in calls)

    def test_success_non_quiet(self):
        """Prints success message on successful flow (non-quiet)."""
        server = MagicMock()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value={"access_token": "at_123"})
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out is not None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("successful" in c for c in calls)

    def test_browser_failure_non_quiet(self):
        """Prints browser failure message (non-quiet)."""
        server = MagicMock()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value={"access_token": "at_123"})
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch.object(base_module, "load_stored_token", return_value=None):
                with patch("webbrowser.open", side_effect=Exception("no browser")):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out is not None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Failed to open browser" in c for c in calls)


# ---------------------------------------------------------------------------
# authenticate_and_save — non-quiet output paths
# ---------------------------------------------------------------------------


class TestAuthenticateAndSaveNonQuiet:
    def test_no_access_token_non_quiet(self):
        """Prints error when tokens have no access_token (non-quiet)."""
        tokens = {"refresh_token": "rt"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch("builtins.print") as mock_print:
                out = authenticate_and_save(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is False
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("No access token" in c for c in calls)

    def test_save_fails_non_quiet(self):
        """Prints error when save_token fails (non-quiet)."""
        tokens = {"access_token": "at"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch.object(base_module, "save_token", return_value=False):
                with patch("builtins.print") as mock_print:
                    out = authenticate_and_save(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is False
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("Failed to save" in c for c in calls)

    def test_success_non_quiet(self):
        """Prints success message on successful save (non-quiet)."""
        tokens = {"access_token": "at_123", "token_type": "Bearer"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch.object(base_module, "save_token", return_value=True):
                with patch("builtins.print") as mock_print:
                    out = authenticate_and_save(
                        CONFIG,
                        "Test",
                        lambda c, x: {},
                        extra_token_keys=("org_id",),
                        quiet=False,
                    )
        assert out is True
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("saved" in c.lower() for c in calls)


# ---------------------------------------------------------------------------
# is_token_expired — edge cases
# ---------------------------------------------------------------------------


class TestIsTokenExpiredEdgeCases:
    def test_jwt_exp_non_numeric(self, fake_token_store):
        """JWT exp that is a string (not int/float) → returns False."""
        import base64

        payload = {"exp": "not-a-number"}
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        token_str = f"header.{encoded}.sig"

        fake_token_store.save_token("prov", {"access_token": token_str, "token_type": "Bearer"})
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            # exp exists in claims but is a string → isinstance check fails → False
            assert not is_token_expired("prov")

    def test_save_token_with_refresh_token(self, fake_token_store):
        """save_token with refresh_token in token_data stores it."""
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            saved = save_token(
                "prov",
                "ENV",
                "at",
                token_data={"refresh_token": "rt-456"},
            )
        assert saved
        stored = fake_token_store.get_token("prov")
        assert stored["refresh_token"] == "rt-456"


# ---------------------------------------------------------------------------
# start_callback_server — actually starts a server
# ---------------------------------------------------------------------------


class TestStartCallbackServerReal:
    def test_starts_on_free_port(self):
        """start_callback_server actually starts an HTTP server on a free port."""
        config = {
            "callback_port_range": (19876, 19885),  # High ports unlikely to be in use
            "redirect_host": "http://localhost",
            "redirect_path": "callback",
        }
        result = start_callback_server(config, "Test")
        assert result is not None
        server, oauth_result, event, ctx = result
        assert ctx.redirect_uri is not None
        assert "1987" in ctx.redirect_uri  # One of our port range
        assert oauth_result is not None
        server.shutdown()


# ---------------------------------------------------------------------------
# parse_jwt_claims — exception handler
# ---------------------------------------------------------------------------


class TestParseJwtClaimsException:
    def test_exception_during_decode(self):
        """Exception during base64 decoding returns None."""
        # This will cause an error in the decode step
        assert parse_jwt_claims("a.!!!!invalid.b64.sig") is None

    def test_exception_in_json_loads(self):
        """Exception during JSON parsing returns None."""
        # Valid base64 but not valid JSON
        encoded = base64.urlsafe_b64encode(b"not-json").decode()
        assert parse_jwt_claims(f"header.{encoded}.sig") is None
