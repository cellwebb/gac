"""Tests for shared OAuth infrastructure in gac.oauth.base.

PKCE helpers, OAuthContext, callback handler, auth URL builder,
server startup, HTML pages, JWT parsing, token CRUD, and flow orchestration.
"""

import base64
import json
import string
import time
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

import gac.oauth.base as base_module
from gac.oauth.base import (
    OAuthContext,
    _CallbackHandler,
    _OAuthResult,
    build_auth_url,
    compute_code_challenge,
    generate_code_verifier,
    get_failure_html,
    get_success_html,
    is_token_expired,
    load_stored_token,
    load_stored_tokens,
    parse_jwt_claims,
    prepare_oauth_context,
    remove_token,
    save_token,
    start_callback_server,
    urlsafe_b64encode,
)

# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------


class TestPKCE:
    def test_urlsafe_b64encode_strips_padding(self):
        encoded = urlsafe_b64encode(b"\xff\xef")
        assert "=" not in encoded

    def test_generate_code_verifier_length(self):
        verifier = generate_code_verifier()
        assert isinstance(verifier, str)
        assert 43 <= len(verifier) <= 128

    def test_generate_code_verifier_character_set(self):
        verifier = generate_code_verifier()
        allowed = set(string.ascii_letters + string.digits + "-_")
        assert set(verifier) <= allowed

    def test_compute_code_challenge_known_value(self):
        challenge = compute_code_challenge("abc")
        assert challenge == "ungWv48Bz-pBQUDeXa4iI7ADYaOWF3qctBD_YfIAFa0"


# ---------------------------------------------------------------------------
# OAuthContext
# ---------------------------------------------------------------------------


class TestOAuthContext:
    def test_prepare_oauth_context_generates_valid_pkce(self):
        ctx = prepare_oauth_context()
        assert len(ctx.state) >= 32
        assert len(ctx.code_verifier) >= 43
        assert ctx.redirect_uri is None
        assert ctx.code_challenge == compute_code_challenge(ctx.code_verifier)
        assert ctx.expires_at is not None

    def test_is_expired_future(self):
        ctx = OAuthContext(
            state="s",
            code_verifier="v",
            code_challenge="c",
            created_at=time.time(),
            expires_at=time.time() + 600,
        )
        assert not ctx.is_expired()

    def test_is_expired_past(self):
        ctx = OAuthContext(
            state="s",
            code_verifier="v",
            code_challenge="c",
            created_at=time.time() - 600,
            expires_at=time.time() - 60,
        )
        assert ctx.is_expired()

    def test_is_expired_no_expiry_defaults_to_5min(self):
        ctx = OAuthContext(
            state="s",
            code_verifier="v",
            code_challenge="c",
            created_at=time.time() - 400,
            expires_at=None,
        )
        assert ctx.is_expired()


# ---------------------------------------------------------------------------
# JWT parsing
# ---------------------------------------------------------------------------


def _make_jwt(payload: dict) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return f"header.{encoded}.signature"


class TestParseJWTClaims:
    def test_valid_claims(self):
        claims = parse_jwt_claims(_make_jwt({"sub": "user123"}))
        assert claims is not None
        assert claims["sub"] == "user123"

    def test_empty_string(self):
        assert parse_jwt_claims("") is None

    def test_invalid_format(self):
        assert parse_jwt_claims("invalid") is None

    def test_two_parts_only(self):
        assert parse_jwt_claims("a.b") is None

    def test_invalid_base64(self):
        assert parse_jwt_claims("a.!!!invalid.b64.sig") is None

    def test_non_dict_payload(self):
        encoded = base64.urlsafe_b64encode(json.dumps([1, 2, 3]).encode()).decode()
        assert parse_jwt_claims(f"header.{encoded}.sig") is None

    def test_nested_org_structure(self):
        payload = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-1",
                "organizations": [{"id": "org-abc", "is_default": True}],
            }
        }
        claims = parse_jwt_claims(_make_jwt(payload))
        assert claims is not None
        orgs = claims["https://api.openai.com/auth"]["organizations"]
        assert orgs[0]["id"] == "org-abc"


# ---------------------------------------------------------------------------
# Callback handler
# ---------------------------------------------------------------------------


def _make_handler(path="/callback?code=test_code&state=s1") -> _CallbackHandler:
    handler = _CallbackHandler.__new__(_CallbackHandler)
    handler.path = path
    handler.command = "GET"
    handler.request_version = "HTTP/1.1"
    handler.headers = {}
    handler._headers_buffer = []
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.wfile = BytesIO()
    return handler


class TestCallbackHandler:
    def test_code_captured(self):
        result = _OAuthResult()
        event = MagicMock()
        _CallbackHandler.result = result
        _CallbackHandler.received_event = event
        _CallbackHandler._provider_name = "Test"

        handler = _make_handler("/cb?code=abc123&state=xyz")
        handler.do_GET()

        assert result.code == "abc123"
        assert result.state == "xyz"
        assert result.error is None
        handler.send_response.assert_called_with(200)

    def test_missing_code_returns_400(self):
        result = _OAuthResult()
        event = MagicMock()
        _CallbackHandler.result = result
        _CallbackHandler.received_event = event
        _CallbackHandler._provider_name = "Test"

        handler = _make_handler("/cb?state=xyz")
        handler.do_GET()

        assert result.error == "Missing authorization code"
        handler.send_response.assert_called_with(400)

    def test_event_is_set(self):
        result = _OAuthResult()
        event = MagicMock()
        _CallbackHandler.result = result
        _CallbackHandler.received_event = event
        _CallbackHandler._provider_name = "Test"

        handler = _make_handler("/cb?code=abc")
        handler.do_GET()
        event.set.assert_called_once()

    def test_log_message_suppressed(self):
        handler = _CallbackHandler.__new__(_CallbackHandler)
        handler.log_message("test %s", "arg")  # no-op, no raise


# ---------------------------------------------------------------------------
# build_auth_url
# ---------------------------------------------------------------------------


class TestBuildAuthUrl:
    def test_no_redirect_uri_raises(self):
        ctx = prepare_oauth_context()
        with pytest.raises(RuntimeError, match="Redirect URI"):
            build_auth_url({"auth_url": "https://example.com/auth"}, ctx)

    def test_includes_required_params(self):
        ctx = prepare_oauth_context()
        ctx.redirect_uri = "http://localhost:1455/callback"
        url = build_auth_url(
            {"auth_url": "https://example.com/auth", "client_id": "cid", "scope": "openid"},
            ctx,
        )
        assert "code_challenge" in url
        assert "S256" in url
        assert ctx.state in url
        assert "cid" in url

    def test_extra_params_appended(self):
        ctx = prepare_oauth_context()
        ctx.redirect_uri = "http://localhost:1455/callback"
        url = build_auth_url(
            {"auth_url": "https://example.com/auth", "client_id": "cid", "scope": "openid"},
            ctx,
            extra_params={"foo": "bar"},
        )
        assert "foo=bar" in url


# ---------------------------------------------------------------------------
# start_callback_server
# ---------------------------------------------------------------------------


class TestStartCallbackServer:
    def test_all_ports_occupied(self):
        with patch.object(base_module, "HTTPServer", side_effect=OSError("port in use")):
            result = start_callback_server(
                {"callback_port_range": (8765, 8767), "redirect_host": "http://localhost", "redirect_path": "callback"},
                "Test",
            )
        assert result is None


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


class TestHTMLPages:
    def test_success_html(self):
        html = get_success_html("TestProvider")
        assert "<!DOCTYPE html>" in html
        assert "TestProvider OAuth Complete" in html

    def test_failure_html_default(self):
        html = get_failure_html("TestProvider")
        assert "TestProvider OAuth Failed" in html
        assert "Missing authorization code" in html

    def test_failure_html_custom_reason(self):
        html = get_failure_html("TestProvider", "Custom error")
        assert "Custom error" in html


# ---------------------------------------------------------------------------
# Token CRUD (parameterized)
# ---------------------------------------------------------------------------


class TestTokenCRUD:
    def test_save_and_load_token(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert save_token("prov", "ENV", "access_tok")
            assert load_stored_token("prov") == "access_tok"

    def test_save_token_with_extra_keys(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert save_token(
                "prov",
                "ENV",
                "at",
                token_data={"foo": "bar", "baz": "qux"},
                extra_keys=("foo", "baz"),
            )
            saved = fake_token_store.get_token("prov")
            assert saved["extra"]["foo"] == "bar"
            assert saved["extra"]["baz"] == "qux"

    def test_save_token_with_expires_in(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert save_token("prov", "ENV", "at", token_data={"expires_in": 3600})
            saved = fake_token_store.get_token("prov")
            assert saved["expiry"] > time.time()

    def test_save_token_with_expires_at(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert save_token("prov", "ENV", "at", token_data={"expires_at": 1700000000})
            saved = fake_token_store.get_token("prov")
            assert saved["expiry"] == 1700000000

    def test_save_token_with_jwt_exp(self, fake_token_store):
        exp_val = int(time.time() + 3600)
        token_str = _make_jwt({"exp": exp_val})
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert save_token("prov", "ENV", token_str)
            saved = fake_token_store.get_token("prov")
            assert saved["expiry"] == exp_val

    def test_save_token_exception_returns_false(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            with patch.object(fake_token_store, "save_token", side_effect=RuntimeError("broken")):
                assert save_token("prov", "ENV", "at") is False

    def test_load_stored_token_none(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert load_stored_token("prov") is None

    def test_load_stored_tokens_flattens_extra(self, fake_token_store):
        fake_token_store.save_token(
            "prov",
            {
                "access_token": "at",
                "token_type": "Bearer",
                "extra": {"account_id": "acc123"},
            },
        )
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            tokens = load_stored_tokens("prov")
        assert tokens is not None
        assert tokens["account_id"] == "acc123"
        assert tokens["access_token"] == "at"

    def test_load_stored_tokens_no_extra(self, fake_token_store):
        fake_token_store.save_token("prov", {"access_token": "at", "token_type": "Bearer"})
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            tokens = load_stored_tokens("prov")
        assert tokens is not None
        assert tokens["access_token"] == "at"

    def test_load_stored_tokens_none(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert load_stored_tokens("prov") is None

    def test_remove_token(self, fake_token_store):
        import os

        fake_token_store.save_token("prov", {"access_token": "at"})
        os.environ["TEST_VAR"] = "val"
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert remove_token("prov", "TEST_VAR")
        assert "TEST_VAR" not in os.environ

    def test_remove_token_exception_returns_false(self):
        with patch.object(base_module, "TokenStore") as MockStore:
            store = MagicMock()
            store.remove_token.side_effect = RuntimeError("fail")
            MockStore.return_value = store
            assert remove_token("prov", "ENV") is False

    def test_is_token_expired_no_token(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert is_token_expired("prov")

    def test_is_token_expired_with_expiry_future(self, fake_token_store):
        fake_token_store.save_token(
            "prov",
            {
                "access_token": "at",
                "token_type": "Bearer",
                "expiry": int(time.time() + 3600),
            },
        )
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert not is_token_expired("prov")

    def test_is_token_expired_with_expiry_past(self, fake_token_store):
        fake_token_store.save_token(
            "prov",
            {
                "access_token": "at",
                "token_type": "Bearer",
                "expiry": int(time.time() - 60),
            },
        )
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert is_token_expired("prov")

    def test_is_token_expired_with_jwt_exp(self, fake_token_store):
        claims = {"exp": int(time.time() + 3600)}
        fake_token_store.save_token(
            "prov",
            {
                "access_token": _make_jwt(claims),
                "token_type": "Bearer",
            },
        )
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert not is_token_expired("prov")

    def test_is_token_expired_no_expiry_no_jwt(self, fake_token_store):
        fake_token_store.save_token("prov", {"access_token": "not-a-jwt", "token_type": "Bearer"})
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert not is_token_expired("prov")

    def test_is_token_expired_margin_seconds(self, fake_token_store):
        # Token expires in 2 minutes — should be expired with 300s margin
        fake_token_store.save_token(
            "prov",
            {
                "access_token": "at",
                "token_type": "Bearer",
                "expiry": int(time.time() + 120),
            },
        )
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            assert is_token_expired("prov", margin_seconds=300)

    def test_save_token_sets_env_var(self, fake_token_store):
        import os

        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            save_token("prov", "MY_TEST_ENV_VAR", "tok123")
        assert os.environ.get("MY_TEST_ENV_VAR") == "tok123"
        del os.environ["MY_TEST_ENV_VAR"]

    def test_save_token_empty_extra_fields_not_stored(self, fake_token_store):
        with patch.object(base_module, "TokenStore", return_value=fake_token_store):
            save_token("prov", "ENV", "at", token_data={"foo": "", "bar": None})
            saved = fake_token_store.get_token("prov")
            assert "extra" not in saved
