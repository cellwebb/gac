"""Tests for perform_oauth_flow() and authenticate_and_save() in base.py.

These are the core orchestration functions — they handle server startup,
browser launch, callback waiting, state validation, code exchange,
token saving, and all the error paths in between.
"""

import time
from unittest.mock import MagicMock, patch

import gac.oauth.base as base_module
from gac.oauth.base import (
    OAuthContext,
    _OAuthResult,
    authenticate_and_save,
    perform_oauth_flow,
)

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


def _make_context() -> OAuthContext:
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


def _mock_server():
    return MagicMock()


# ---------------------------------------------------------------------------
# perform_oauth_flow
# ---------------------------------------------------------------------------


class TestPerformOAuthFlow:
    """Test perform_oauth_flow — the core OAuth orchestration."""

    def test_server_startup_failure(self):
        """Returns None when callback server can't start."""
        with patch.object(base_module, "start_callback_server", return_value=None):
            result = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert result is None

    def test_timeout(self):
        """Returns None when callback times out."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = False  # timeout

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=True)
        assert out is None
        server.shutdown.assert_called_once()

    def test_callback_error(self):
        """Returns None when callback reports an error."""
        server = _mock_server()
        result = _make_result(error="access_denied")
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None
        server.shutdown.assert_called_once()

    def test_state_mismatch(self):
        """Returns None when callback state doesn't match context."""
        server = _mock_server()
        result = _make_result(state="wrong-state")
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is None

    def test_no_code_in_result(self):
        """Returns None when result has no code (edge case)."""
        server = _mock_server()
        result = _make_result(code=None)
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", lambda c, x: {}, quiet=True)
        assert out is None

    def test_token_exchange_failure(self):
        """Returns None when exchange_fn returns None."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value=None)
        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out is None
        exchange.assert_called_once_with("auth_code", ctx)

    def test_success(self):
        """Returns tokens on successful flow."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        tokens = {"access_token": "at_123", "token_type": "Bearer"}
        exchange = MagicMock(return_value=tokens)

        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open"):
                out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=True)
        assert out == tokens
        server.shutdown.assert_called_once()

    def test_browser_open_failure_still_succeeds(self):
        """Flow succeeds even if browser.open raises — user can open manually."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        tokens = {"access_token": "at_123"}
        exchange = MagicMock(return_value=tokens)

        with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
            with patch("webbrowser.open", side_effect=Exception("no browser")):
                out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out == tokens

    def test_existing_token_warning(self):
        """Prints warning when overwriting existing tokens."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value={"access_token": "new"})

        with patch.object(base_module, "load_stored_token", return_value="old"):
            with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=False)
        assert out is not None
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("overwritten" in c.lower() for c in calls)

    def test_quiet_mode_suppresses_output(self):
        """Quiet mode doesn't print anything."""
        server = _mock_server()
        result = _make_result()
        event = MagicMock()
        event.wait.return_value = True

        ctx = _make_context()
        exchange = MagicMock(return_value={"access_token": "at"})

        with patch.object(base_module, "load_stored_token", return_value=None):
            with patch.object(base_module, "start_callback_server", return_value=(server, result, event, ctx)):
                with patch("webbrowser.open"):
                    with patch("builtins.print") as mock_print:
                        out = perform_oauth_flow(CONFIG, "Test", exchange, quiet=True)
        assert out is not None
        # In quiet mode with no existing token, only success message printed
        calls = [str(c) for c in mock_print.call_args_list]
        assert len(calls) <= 1  # at most the success message


# ---------------------------------------------------------------------------
# authenticate_and_save
# ---------------------------------------------------------------------------


class TestAuthenticateAndSave:
    """Test authenticate_and_save — the public entry point."""

    def test_flow_returns_none(self):
        """Returns False when OAuth flow fails."""
        with patch.object(base_module, "perform_oauth_flow", return_value=None):
            assert authenticate_and_save(CONFIG, "Test", lambda c, x: {}) is False

    def test_no_access_token_in_response(self):
        """Returns False when tokens have no access_token."""
        tokens = {"refresh_token": "rt"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            out = authenticate_and_save(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is False

    def test_save_fails(self):
        """Returns False when save_token fails."""
        tokens = {"access_token": "at"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch.object(base_module, "save_token", return_value=False):
                out = authenticate_and_save(CONFIG, "Test", lambda c, x: {}, quiet=False)
        assert out is False

    def test_success(self):
        """Returns True when flow and save succeed."""
        tokens = {"access_token": "at_123", "token_type": "Bearer"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch.object(base_module, "save_token", return_value=True):
                out = authenticate_and_save(
                    CONFIG,
                    "Test",
                    lambda c, x: {},
                    extra_token_keys=("org_id",),
                    quiet=False,
                )
        assert out is True

    def test_success_passes_extra_token_keys(self):
        """authenticate_and_save forwards extra_token_keys to save_token."""
        tokens = {"access_token": "at", "org_id": "org-1"}
        with patch.object(base_module, "perform_oauth_flow", return_value=tokens):
            with patch.object(base_module, "save_token", return_value=True) as mock_save:
                authenticate_and_save(
                    CONFIG,
                    "Test",
                    lambda c, x: {},
                    extra_token_keys=("org_id",),
                )
        mock_save.assert_called_once_with(
            CONFIG["provider_key"],
            CONFIG["api_key_env_var"],
            "at",
            tokens,
            ("org_id",),
        )

    def test_success_passes_extra_auth_params(self):
        """authenticate_and_save forwards extra_auth_params to perform_oauth_flow."""
        with patch.object(base_module, "perform_oauth_flow", return_value=None) as mock_flow:
            authenticate_and_save(
                CONFIG,
                "Test",
                lambda c, x: {},
                extra_auth_params={"foo": "bar"},
            )
        _, kwargs = mock_flow.call_args
        assert kwargs["extra_auth_params"] == {"foo": "bar"}
