import string
import time
from types import SimpleNamespace
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
    assert context.redirect_uri == "http://localhost:8765/callback"
    assert server.serve_called
    assert isinstance(oauth_result, claude_code._OAuthResult)
    assert event.is_set() is False


def test_callback_handler_success_sets_code_and_state(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = claude_code._CallbackHandler.__new__(claude_code._CallbackHandler)
    handler.path = "/callback?code=abc&state=expected"
    handler.result = claude_code._OAuthResult()

    class FlagEvent:
        def __init__(self) -> None:
            self.flag = False

        def set(self) -> None:
            self.flag = True

        def is_set(self) -> bool:
            return self.flag

    event = FlagEvent()
    handler.received_event = event
    captured: dict[str, object] = {}

    def fake_write_response(status: int, body: str) -> None:
        captured["status"] = status
        captured["body"] = body

    handler._write_response = fake_write_response  # type: ignore[method-assign]

    handler.do_GET()

    assert handler.result.code == "abc"
    assert handler.result.state == "expected"
    assert handler.result.error is None
    assert event.is_set()
    assert captured["status"] == 200
    assert "Authentication Successful" in captured["body"]  # type: ignore[index]


def test_callback_handler_failure_sets_error(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = claude_code._CallbackHandler.__new__(claude_code._CallbackHandler)
    handler.path = "/callback?state=expected"
    handler.result = claude_code._OAuthResult()

    class FlagEvent:
        def __init__(self) -> None:
            self.flag = False

        def set(self) -> None:
            self.flag = True

        def is_set(self) -> bool:
            return self.flag

    event = FlagEvent()
    handler.received_event = event
    captured: dict[str, object] = {}

    def fake_write_response(status: int, body: str) -> None:
        captured["status"] = status
        captured["body"] = body

    handler._write_response = fake_write_response  # type: ignore[method-assign]

    handler.do_GET()

    assert handler.result.error == "Missing code or state"
    assert handler.result.code is None
    assert handler.result.state is None
    assert event.is_set()
    assert captured["status"] == 400
    assert "Authentication Failed" in captured["body"]  # type: ignore[index]


def test_exchange_code_for_tokens_success_adds_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyResponse:
        status_code = 200
        text = "ok"

        def json(self) -> dict:
            return {"access_token": "token", "expires_in": 30}

    def fake_post(url, json, headers, timeout):
        assert url == claude_code.CLAUDE_CODE_CONFIG["token_url"]
        return DummyResponse()

    monkeypatch.setattr(claude_code.httpx, "post", fake_post)

    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    before = time.time()
    tokens = claude_code.exchange_code_for_tokens("code", context)
    assert tokens is not None
    assert tokens["access_token"] == "token"
    assert "expires_at" in tokens
    assert tokens["expires_at"] == pytest.approx(before + 30, abs=1.0)


def test_exchange_code_for_tokens_returns_none_on_error_status(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyResponse:
        status_code = 400
        text = "bad request"

        def json(self) -> dict:
            return {}

    def fake_post(url, json, headers, timeout):
        return DummyResponse()

    monkeypatch.setattr(claude_code.httpx, "post", fake_post)

    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    tokens = claude_code.exchange_code_for_tokens("code", context)
    assert tokens is None


def test_exchange_code_for_tokens_raises_without_redirect() -> None:
    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    with pytest.raises(RuntimeError):
        claude_code.exchange_code_for_tokens("code", context)


def test_exchange_code_for_tokens_handles_post_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(claude_code.httpx, "post", fake_post)

    context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
        redirect_uri="http://localhost:8765/callback",
    )

    tokens = claude_code.exchange_code_for_tokens("code", context)
    assert tokens is None


def test_perform_oauth_flow_returns_none_when_server_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    monkeypatch.setattr(claude_code, "prepare_oauth_context", lambda: base_context)
    monkeypatch.setattr(claude_code, "_start_callback_server", lambda ctx: None)

    result = claude_code.perform_oauth_flow(quiet=True)
    assert result is None


def test_perform_oauth_flow_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    class FakeServer:
        def __init__(self) -> None:
            self.shutdown_called = False

        def shutdown(self) -> None:
            self.shutdown_called = True

    class FakeEvent:
        def __init__(self) -> None:
            self.wait_called_with: float | None = None

        def wait(self, timeout: float) -> bool:
            self.wait_called_with = timeout
            return False

    fake_server = FakeServer()
    fake_event = FakeEvent()
    fake_result = SimpleNamespace(code=None, state=None, error=None)

    def fake_prepare() -> claude_code.OAuthContext:
        return base_context

    def fake_start(context: claude_code.OAuthContext):
        context.redirect_uri = "http://localhost:8765/callback"
        return fake_server, fake_result, fake_event

    monkeypatch.setattr(claude_code, "prepare_oauth_context", fake_prepare)
    monkeypatch.setattr(claude_code, "_start_callback_server", fake_start)
    monkeypatch.setattr(claude_code, "build_authorization_url", lambda ctx: "http://example.com/auth")
    monkeypatch.setattr(claude_code.webbrowser, "open", lambda url: True)

    result = claude_code.perform_oauth_flow(quiet=True)

    assert result is None
    assert fake_server.shutdown_called
    assert fake_event.wait_called_with == claude_code.CLAUDE_CODE_CONFIG["callback_timeout"]


def test_perform_oauth_flow_success(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="state123",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    class FakeServer:
        def __init__(self) -> None:
            self.shutdown_called = False

        def shutdown(self) -> None:
            self.shutdown_called = True

    class FakeEvent:
        def wait(self, timeout: float) -> bool:
            return True

    fake_server = FakeServer()
    fake_event = FakeEvent()
    fake_result = SimpleNamespace(code="authcode", state="state123", error=None)
    captured: dict[str, str] = {}

    def fake_prepare() -> claude_code.OAuthContext:
        return base_context

    def fake_start(context: claude_code.OAuthContext):
        context.redirect_uri = "http://localhost:8765/callback"
        return fake_server, fake_result, fake_event

    def fake_exchange(auth_code: str, context: claude_code.OAuthContext) -> dict[str, str]:
        captured["code"] = auth_code
        captured["redirect_uri"] = context.redirect_uri or ""
        return {"access_token": "token"}

    monkeypatch.setattr(claude_code, "prepare_oauth_context", fake_prepare)
    monkeypatch.setattr(claude_code, "_start_callback_server", fake_start)
    monkeypatch.setattr(claude_code, "build_authorization_url", lambda ctx: "http://example.com/auth")
    monkeypatch.setattr(claude_code.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(claude_code, "exchange_code_for_tokens", fake_exchange)

    tokens = claude_code.perform_oauth_flow(quiet=True)

    assert tokens == {"access_token": "token"}
    assert captured["code"] == "authcode"
    assert captured["redirect_uri"] == "http://localhost:8765/callback"
    assert fake_server.shutdown_called


def test_perform_oauth_flow_detects_state_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="expected",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    class FakeServer:
        def __init__(self) -> None:
            self.shutdown_called = False

        def shutdown(self) -> None:
            self.shutdown_called = True

    class FakeEvent:
        def wait(self, timeout: float) -> bool:
            return True

    fake_server = FakeServer()
    fake_event = FakeEvent()
    fake_result = SimpleNamespace(code="authcode", state="different", error=None)

    def fake_prepare() -> claude_code.OAuthContext:
        return base_context

    def fake_start(context: claude_code.OAuthContext):
        context.redirect_uri = "http://localhost:8765/callback"
        return fake_server, fake_result, fake_event

    def fail_exchange(auth_code: str, context: claude_code.OAuthContext):
        raise AssertionError("exchange should not be called on state mismatch")

    monkeypatch.setattr(claude_code, "prepare_oauth_context", fake_prepare)
    monkeypatch.setattr(claude_code, "_start_callback_server", fake_start)
    monkeypatch.setattr(claude_code, "build_authorization_url", lambda ctx: "http://example.com/auth")
    monkeypatch.setattr(claude_code.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(claude_code, "exchange_code_for_tokens", fail_exchange)

    result = claude_code.perform_oauth_flow(quiet=True)

    assert result is None
    assert fake_server.shutdown_called


def test_perform_oauth_flow_handles_callback_error(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="expected",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    class FakeServer:
        def __init__(self) -> None:
            self.shutdown_called = False

        def shutdown(self) -> None:
            self.shutdown_called = True

    class FakeEvent:
        def wait(self, timeout: float) -> bool:
            return True

    fake_server = FakeServer()
    fake_event = FakeEvent()
    fake_result = SimpleNamespace(code=None, state=None, error="bad redirect")

    def fake_prepare() -> claude_code.OAuthContext:
        return base_context

    def fake_start(context: claude_code.OAuthContext):
        context.redirect_uri = "http://localhost:8765/callback"
        return fake_server, fake_result, fake_event

    monkeypatch.setattr(claude_code, "prepare_oauth_context", fake_prepare)
    monkeypatch.setattr(claude_code, "_start_callback_server", fake_start)
    monkeypatch.setattr(claude_code, "build_authorization_url", lambda ctx: "http://example.com/auth")
    monkeypatch.setattr(claude_code.webbrowser, "open", lambda url: True)

    result = claude_code.perform_oauth_flow(quiet=True)

    assert result is None
    assert fake_server.shutdown_called


def test_perform_oauth_flow_returns_none_when_exchange_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    base_context = claude_code.OAuthContext(
        state="state",
        code_verifier="verifier",
        code_challenge="challenge",
        created_at=time.time(),
    )

    class FakeServer:
        def shutdown(self) -> None:
            self.shutdown_called = True

        def __init__(self) -> None:
            self.shutdown_called = False

    class FakeEvent:
        def wait(self, timeout: float) -> bool:
            return True

    fake_server = FakeServer()
    fake_event = FakeEvent()
    fake_result = SimpleNamespace(code="auth", state="state", error=None)

    def fake_prepare() -> claude_code.OAuthContext:
        return base_context

    def fake_start(context: claude_code.OAuthContext):
        context.redirect_uri = "http://localhost:8765/callback"
        return fake_server, fake_result, fake_event

    monkeypatch.setattr(claude_code, "prepare_oauth_context", fake_prepare)
    monkeypatch.setattr(claude_code, "_start_callback_server", fake_start)
    monkeypatch.setattr(claude_code, "build_authorization_url", lambda ctx: "http://example.com/auth")
    monkeypatch.setattr(claude_code.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(claude_code, "exchange_code_for_tokens", lambda code, ctx: None)

    result = claude_code.perform_oauth_flow(quiet=True)

    assert result is None
    assert fake_server.shutdown_called


def test_authenticate_and_save_success(monkeypatch: pytest.MonkeyPatch) -> None:
    tokens = {"access_token": "token"}
    saved: list[str] = []

    monkeypatch.setattr(claude_code, "perform_oauth_flow", lambda quiet: tokens)

    def fake_save_token(access_token: str, token_data: dict | None = None) -> bool:
        saved.append(access_token)
        return True

    monkeypatch.setattr(claude_code, "save_token", fake_save_token)

    assert claude_code.authenticate_and_save(quiet=True) is True
    assert saved == ["token"]


def test_authenticate_and_save_missing_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(claude_code, "perform_oauth_flow", lambda quiet: {"refresh_token": "abc"})

    assert claude_code.authenticate_and_save(quiet=True) is False


def test_authenticate_and_save_handles_save_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(claude_code, "perform_oauth_flow", lambda quiet: {"access_token": "token"})
    monkeypatch.setattr(claude_code, "save_token", lambda token, token_data=None: False)

    assert claude_code.authenticate_and_save(quiet=True) is False


def test_authenticate_and_save_returns_false_when_flow_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(claude_code, "perform_oauth_flow", lambda quiet: None)

    assert claude_code.authenticate_and_save(quiet=True) is False


def test_load_stored_token_missing_file_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    from gac.oauth.token_store import TokenStore

    mock_store = mock.Mock(spec=TokenStore)
    mock_store.get_token.return_value = None
    monkeypatch.setattr(claude_code, "TokenStore", lambda: mock_store)

    assert claude_code.load_stored_token() is None


def test_load_stored_token_reads_value(monkeypatch: pytest.MonkeyPatch) -> None:
    from gac.oauth.token_store import TokenStore

    mock_store = mock.Mock(spec=TokenStore)
    mock_store.get_token.return_value = {"access_token": "token"}
    monkeypatch.setattr(claude_code, "TokenStore", lambda: mock_store)

    assert claude_code.load_stored_token() == "token"


def test_load_stored_token_returns_none_when_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from gac.oauth.token_store import TokenStore

    mock_store = mock.Mock(spec=TokenStore)
    mock_store.get_token.return_value = {}  # Token dict without access_token
    monkeypatch.setattr(claude_code, "TokenStore", lambda: mock_store)

    assert claude_code.load_stored_token() is None


def test_save_token_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from gac.oauth.token_store import TokenStore

    mock_store = mock.Mock(spec=TokenStore)
    mock_store.save_token.return_value = None
    monkeypatch.setattr(claude_code, "TokenStore", lambda: mock_store)

    assert claude_code.save_token("token") is True
    mock_store.save_token.assert_called_once()
    call_args = mock_store.save_token.call_args
    assert call_args[0][0] == "claude-code"  # provider name
    assert call_args[0][1]["access_token"] == "token"
    assert call_args[0][1]["token_type"] == "Bearer"


def test_save_token_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from gac.oauth.token_store import TokenStore

    mock_store = mock.Mock(spec=TokenStore)
    mock_store.save_token.side_effect = Exception("disk full")
    monkeypatch.setattr(claude_code, "TokenStore", lambda: mock_store)

    assert claude_code.save_token("token") is False
