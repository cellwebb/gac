import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import dotenv
import pytest

from gac.oauth import claude_code


def test_prepare_oauth_context_generates_valid_pkce_values() -> None:
    context = claude_code.prepare_oauth_context()

    assert len(context.state) >= 32
    assert len(context.code_verifier) >= 43
    assert context.redirect_uri is None
    expected_challenge = claude_code._compute_code_challenge(context.code_verifier)
    assert context.code_challenge == expected_challenge


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


def test_authenticate_and_save_success(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    tokens = {"access_token": "token"}
    saved: list[str] = []

    monkeypatch.setattr(claude_code, "perform_oauth_flow", lambda quiet: tokens)
    monkeypatch.setattr(claude_code, "get_token_storage_path", lambda: tmp_path / ".gac.env")

    def fake_save_token(access_token: str) -> bool:
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
    monkeypatch.setattr(claude_code, "save_token", lambda token: False)

    assert claude_code.authenticate_and_save(quiet=True) is False


def test_load_stored_token_missing_file_returns_none(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_path = tmp_path / ".gac.env"
    if env_path.exists():
        env_path.unlink()

    monkeypatch.setattr(claude_code, "get_token_storage_path", lambda: env_path)

    assert claude_code.load_stored_token() is None


def test_load_stored_token_reads_value(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_path = tmp_path / ".gac.env"
    env_path.write_text("")

    monkeypatch.setattr(claude_code, "get_token_storage_path", lambda: env_path)
    monkeypatch.setattr(dotenv, "dotenv_values", lambda path: {"CLAUDE_CODE_ACCESS_TOKEN": "token"})

    assert claude_code.load_stored_token() == "token"


def test_save_token_success(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_path = tmp_path / ".gac.env"
    monkeypatch.setattr(claude_code, "get_token_storage_path", lambda: env_path)

    captured: dict[str, str] = {}

    def fake_set_key(path: str, key: str, value: str):
        captured["path"] = path
        captured["key"] = key
        captured["value"] = value
        return True

    monkeypatch.setattr(dotenv, "set_key", fake_set_key)

    assert claude_code.save_token("token") is True
    assert captured == {
        "path": str(env_path),
        "key": "CLAUDE_CODE_ACCESS_TOKEN",
        "value": "token",
    }


def test_save_token_failure(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_path = tmp_path / ".gac.env"
    monkeypatch.setattr(claude_code, "get_token_storage_path", lambda: env_path)

    def fake_set_key(path: str, key: str, value: str):
        raise RuntimeError("disk full")

    monkeypatch.setattr(dotenv, "set_key", fake_set_key)

    assert claude_code.save_token("token") is False
