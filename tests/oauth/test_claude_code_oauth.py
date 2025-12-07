import string
import time
from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest

from gac.oauth import claude_code


def test_urlsafe_b64encode_strips_padding() -> None:
    encoded = claude_code._urlsafe_b64encode(b"\xff\xef")
    assert "=" not in encoded
    assert encoded == "_-8"


def test_generate_code_verifier_character_set() -> None:
    verifier = claude_code._generate_code_verifier()
    allowed = set(string.ascii_letters + string.digits + "-_")
    assert 43 <= len(verifier) <= 128
    assert set(verifier) <= allowed


def test_compute_code_challenge_known_value() -> None:
    challenge = claude_code._compute_code_challenge("abc")
    assert challenge == "ungWv48Bz-pBQUDeXa4iI7ADYaOWF3qctBD_YfIAFa0"


def test_prepare_oauth_context_generates_valid_pkce_values() -> None:
    context = claude_code.prepare_oauth_context()

    assert len(context.state) >= 32
    assert len(context.code_verifier) >= 43
    assert context.redirect_uri is None
    expected_challenge = claude_code._compute_code_challenge(context.code_verifier)
    assert context.code_challenge == expected_challenge


def test_get_success_and_failure_html_include_messages() -> None:
    success_html = claude_code._get_success_html()
    failure_html = claude_code._get_failure_html()

    assert "Authentication Successful" in success_html
    assert "Authentication Failed" in failure_html


def test_exchange_code_for_tokens_invalid_response() -> None:
    """Test token exchange with invalid response (line 261->263)."""
    import httpx

    # Mock a non-200 response
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    context = claude_code.OAuthContext(
        state="test_state",
        code_verifier="test_verifier",
        code_challenge="test_challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",  # Add required redirect_uri
    )

    with mock.patch.object(httpx, "post", return_value=mock_response):
        result = claude_code.exchange_code_for_tokens("invalid_code", context)
        assert result is None  # Should return None on failed response


def test_exchange_code_for_tokens_request_exception() -> None:
    """Test token exchange with request exception."""
    import httpx

    context = claude_code.OAuthContext(
        state="test_state",
        code_verifier="test_verifier",
        code_challenge="test_challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",  # Add required redirect_uri
    )

    # Mock httpx.post to raise an exception
    with mock.patch.object(httpx, "post", side_effect=httpx.RequestError("Network error")):
        result = claude_code.exchange_code_for_tokens("test_code", context)
        assert result is None  # Should return None on exception


def test_perform_oauth_flow_server_startup_failure() -> None:
    """Test OAuth flow failure when server can't start (lines 278, 285-288)."""
    # Mock _start_callback_server to return None
    with mock.patch.object(claude_code, "_start_callback_server", return_value=None):
        with mock.patch("builtins.print") as mock_print:
            result = claude_code.perform_oauth_flow(quiet=False)
            assert result is None
            # Should print error message
            mock_print.assert_any_call("❌ Could not start OAuth callback server; all ports are in use")


def test_perform_oauth_flow_redirect_uri_failure() -> None:
    """Test OAuth flow failure when redirect URI is None (lines 294-297)."""
    # Mock server setup but no redirect URI
    mock_server = mock.Mock()
    mock_result = mock.Mock()
    mock_event = mock.Mock()

    with mock.patch.object(claude_code, "_start_callback_server", return_value=(mock_server, mock_result, mock_event)):
        with mock.patch("builtins.print") as mock_print:
            result = claude_code.perform_oauth_flow(quiet=False)
            assert result is None
            mock_server.shutdown.assert_called_once()
            mock_print.assert_any_call("❌ Failed to assign redirect URI for OAuth flow")


def test_perform_oauth_flow_timeout_failure() -> None:
    """Test OAuth flow timeout scenario (lines 301-305, 311)."""
    # Setup mock server with timeout
    mock_server = mock.Mock()
    mock_result = mock.Mock()
    mock_event = mock.Mock()
    mock_event.wait.return_value = False  # Timeout

    # Create a context that will have redirect_uri
    context = claude_code.OAuthContext(
        state="test_state",
        code_verifier="test_verifier",
        code_challenge="test_challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    with mock.patch.object(claude_code, "_start_callback_server", return_value=(mock_server, mock_result, mock_event)):
        with mock.patch.object(claude_code, "prepare_oauth_context", return_value=context):
            with mock.patch.object(claude_code, "build_authorization_url", return_value="http://test.auth.url"):
                with mock.patch("builtins.print"):
                    with mock.patch("webbrowser.open") as mock_open:
                        result = claude_code.perform_oauth_flow(quiet=False)
                        assert result is None
                        mock_server.shutdown.assert_called_once()
                        mock_open.assert_called_once_with("http://test.auth.url")


def test_perform_oauth_flow_auth_error() -> None:
    """Test OAuth flow with authorization error from callback."""
    # Setup mock server with auth error in result
    mock_server = mock.Mock()
    mock_result = mock.Mock()
    mock_result.error = "access_denied"
    mock_result.code = None
    mock_event = mock.Mock()
    mock_event.wait.return_value = True

    context = claude_code.OAuthContext(
        state="test_state",
        code_verifier="test_verifier",
        code_challenge="test_challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    with mock.patch.object(claude_code, "_start_callback_server", return_value=(mock_server, mock_result, mock_event)):
        with mock.patch.object(claude_code, "prepare_oauth_context", return_value=context):
            with mock.patch.object(claude_code, "build_authorization_url", return_value="http://test.auth.url"):
                with mock.patch("builtins.print") as mock_print:
                    with mock.patch("webbrowser.open"):
                        result = claude_code.perform_oauth_flow(quiet=False)
                        assert result is None
                        mock_server.shutdown.assert_called_once()
                        # Should contain the error message somewhere in the calls
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        assert any("access_denied" in call for call in print_calls)


def test_build_authorization_url_requires_redirect() -> None:
    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    with pytest.raises(RuntimeError):
        claude_code.build_authorization_url(context)


def test_build_authorization_url_includes_expected_parameters() -> None:
    context = claude_code.OAuthContext(
        state="state123",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    url = claude_code.build_authorization_url(context)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert query["state"] == ["state123"]
    assert query["code_challenge"] == ["challenge"]
    assert query["redirect_uri"] == ["http://localhost:8765/callback"]


def test_start_callback_server_returns_none_when_ports_in_use(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    def fake_http_server(*args, **kwargs):
        attempts.append(1)
        raise OSError("port busy")

    monkeypatch.setattr(claude_code, "HTTPServer", fake_http_server)

    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    result = claude_code._start_callback_server(context)

    expected_attempts = (
        claude_code.CLAUDE_CODE_CONFIG["callback_port_range"][1]
        - claude_code.CLAUDE_CODE_CONFIG["callback_port_range"][0]
        + 1
    )
    assert len(attempts) == expected_attempts
    assert result is None
    assert context.redirect_uri is None


def test_start_callback_server_success_sets_result(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyServer:
        def __init__(self, address, handler):
            self.address = address
            self.handler = handler
            self.serve_called = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def serve_forever(self):
            self.serve_called = True

    class FakeThread:
        def __init__(self, target, daemon=True):
            self.target = target
            self.daemon = daemon
            self.started = False

        def start(self):
            self.started = True
            self.target()

    def fake_thread(*, target, daemon=True):
        return FakeThread(target, daemon=daemon)

    monkeypatch.setattr(claude_code, "HTTPServer", DummyServer)
    monkeypatch.setattr(claude_code.threading, "Thread", fake_thread)

    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    result = claude_code._start_callback_server(context)

    assert result is not None
    server, oauth_result, event = result
