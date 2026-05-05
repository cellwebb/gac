"""Tests for Claude Code OAuth — config, code exchange, token CRUD, and wrappers."""

import os
import time
from unittest import mock

import httpx

import gac.oauth.base as base_module
from gac.oauth import claude_code
from gac.oauth.base import OAuthContext
from gac.oauth.claude_code import CLAUDE_CODE_CONFIG

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_values(self):
        assert CLAUDE_CODE_CONFIG["provider_key"] == "claude-code"
        assert CLAUDE_CODE_CONFIG["api_key_env_var"] == "CLAUDE_CODE_ACCESS_TOKEN"
        assert CLAUDE_CODE_CONFIG["callback_port_range"] == (8765, 8795)


# ---------------------------------------------------------------------------
# Code exchange
# ---------------------------------------------------------------------------


class TestExchangeCode:
    def _make_context(self) -> OAuthContext:
        return OAuthContext(
            state="test_state",
            code_verifier="test_verifier",
            code_challenge="test_challenge",
            created_at=time.time(),
            redirect_uri="http://localhost:8765/callback",
        )

    def test_success(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "at_123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with mock.patch.object(httpx, "post", return_value=mock_response):
            with mock.patch("time.time", return_value=1000.0):
                result = claude_code._exchange_code("auth_code", self._make_context())

        assert result is not None
        assert result["access_token"] == "at_123"
        assert result["expires_at"] == 1000.0 + 3600

    def test_success_with_expires_at(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "at_123",
            "token_type": "Bearer",
            "expires_at": 9999,
        }

        with mock.patch.object(httpx, "post", return_value=mock_response):
            result = claude_code._exchange_code("auth_code", self._make_context())

        assert result is not None
        assert result["expires_at"] == 9999

    def test_invalid_response(self):
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with mock.patch.object(httpx, "post", return_value=mock_response):
            result = claude_code._exchange_code("code", self._make_context())
        assert result is None

    def test_request_exception(self):
        with mock.patch.object(httpx, "post", side_effect=httpx.RequestError("Network error")):
            result = claude_code._exchange_code("code", self._make_context())
        assert result is None

    def test_no_redirect_uri(self):
        ctx = OAuthContext(
            state="s",
            code_verifier="v",
            code_challenge="c",
            created_at=time.time(),
        )
        assert claude_code._exchange_code("code", ctx) is None


# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------


class TestLoadStoredToken:
    def test_exists(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"access_token": "tok123"}):
            assert claude_code.load_stored_token() == "tok123"

    def test_not_found(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value=None):
            assert claude_code.load_stored_token() is None


# ---------------------------------------------------------------------------
# Token expiry
# ---------------------------------------------------------------------------


class TestIsTokenExpired:
    def test_expired(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"expiry": 940}):
            with mock.patch("time.time", return_value=1000):
                assert claude_code.is_token_expired() is True

    def test_no_expiry_assumed_valid(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"access_token": "tok"}):
            assert claude_code.is_token_expired() is False

    def test_within_5_minutes(self):
        # Claude uses 300s margin
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"expiry": 1120}):
            with mock.patch("time.time", return_value=1000):
                assert claude_code.is_token_expired() is True  # 120s left < 300s margin

    def test_no_token(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value=None):
            assert claude_code.is_token_expired() is True


# ---------------------------------------------------------------------------
# Token refresh (re-auth)
# ---------------------------------------------------------------------------


class TestRefreshTokenIfExpired:
    def test_valid_token(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"expiry": 5000}):
            with mock.patch("time.time", return_value=1000):
                with mock.patch.object(claude_code, "authenticate_and_save") as mock_auth:
                    assert claude_code.refresh_token_if_expired(quiet=True) is True
                    mock_auth.assert_not_called()

    def test_expired_reauth_succeeds(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"expiry": 940}):
            with mock.patch("time.time", return_value=1000):
                with mock.patch.object(claude_code, "authenticate_and_save", return_value=True) as m:
                    assert claude_code.refresh_token_if_expired(quiet=True) is True
                    m.assert_called_once_with(quiet=True)

    def test_expired_reauth_fails(self):
        with mock.patch.object(base_module.TokenStore, "get_token", return_value={"expiry": 940}):
            with mock.patch("time.time", return_value=1000):
                with mock.patch.object(claude_code, "authenticate_and_save", return_value=False):
                    assert claude_code.refresh_token_if_expired(quiet=True) is False


# ---------------------------------------------------------------------------
# save_token / remove_token wrappers
# ---------------------------------------------------------------------------


class TestSaveToken:
    def test_with_expiry_in_data(self, monkeypatch):
        mock_store = mock.Mock()
        monkeypatch.setattr(base_module.TokenStore, "save_token", mock_store)
        mock_env = {}
        monkeypatch.setattr(os, "environ", mock_env)

        with mock.patch("time.time", return_value=1000.0):
            result = claude_code.save_token("tok", {"access_token": "tok", "expires_in": 3600, "token_type": "Bearer"})

        assert result is True
        saved = mock_store.call_args[0][1]
        assert saved["expiry"] == 1000.0 + 3600
        assert mock_env["CLAUDE_CODE_ACCESS_TOKEN"] == "tok"

    def test_without_expiry(self, monkeypatch):
        mock_store = mock.Mock()
        monkeypatch.setattr(base_module.TokenStore, "save_token", mock_store)
        mock_env = {}
        monkeypatch.setattr(os, "environ", mock_env)

        assert claude_code.save_token("tok") is True
        saved = mock_store.call_args[0][1]
        assert "expiry" not in saved

    def test_failure(self, monkeypatch):
        def _raise(*a, **kw):
            raise Exception("fail")

        monkeypatch.setattr(base_module.TokenStore, "save_token", _raise)
        mock_env = {}
        monkeypatch.setattr(os, "environ", mock_env)
        assert claude_code.save_token("tok") is False


class TestRemoveToken:
    def test_success(self, monkeypatch):
        mock_store = mock.Mock()
        monkeypatch.setattr(base_module.TokenStore, "remove_token", mock_store)
        mock_env = {"CLAUDE_CODE_ACCESS_TOKEN": "tok"}
        monkeypatch.setattr(os, "environ", mock_env)

        assert claude_code.remove_token() is True
        assert "CLAUDE_CODE_ACCESS_TOKEN" not in mock_env

    def test_failure(self, monkeypatch):
        def _raise(*a, **kw):
            raise Exception("fail")

        monkeypatch.setattr(base_module.TokenStore, "remove_token", _raise)
        mock_env = {"CLAUDE_CODE_ACCESS_TOKEN": "tok"}
        monkeypatch.setattr(os, "environ", mock_env)

        assert claude_code.remove_token() is False
        assert "CLAUDE_CODE_ACCESS_TOKEN" in mock_env


# ---------------------------------------------------------------------------
# Wrapper delegation
# ---------------------------------------------------------------------------


class TestWrapperDelegation:
    def test_perform_oauth_flow(self):
        with mock.patch.object(claude_code, "_base_flow", return_value={"access_token": "at"}) as m:
            assert claude_code.perform_oauth_flow(quiet=True) == {"access_token": "at"}
            m.assert_called_once()

    def test_authenticate_and_save(self):
        with mock.patch.object(claude_code, "_base_authenticate", return_value=True) as m:
            assert claude_code.authenticate_and_save(quiet=True) is True
            m.assert_called_once()
