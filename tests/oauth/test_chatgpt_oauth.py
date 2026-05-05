"""Tests for ChatGPT OAuth — config, code exchange, token refresh, wrapper delegation."""

import base64
import json
from unittest.mock import MagicMock, patch

import pytest

import gac.oauth.chatgpt as chatgpt_module
from gac.oauth.base import OAuthContext, prepare_oauth_context
from gac.oauth.chatgpt import (
    CHATGPT_OAUTH_CONFIG,
    DEFAULT_CODEX_MODELS,
    _exchange_code,
    authenticate_and_save,
    perform_oauth_flow,
    refresh_access_token,
    refresh_token_if_expired,
)

PROVIDER_KEY = CHATGPT_OAUTH_CONFIG["provider_key"]


def _make_jwt(payload: dict) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return f"header.{encoded}.signature"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_values(self):
        assert CHATGPT_OAUTH_CONFIG["issuer"] == "https://auth.openai.com"
        assert CHATGPT_OAUTH_CONFIG["client_id"] == "app_EMoamEEZ73f0CkXaXp7hrann"
        assert CHATGPT_OAUTH_CONFIG["callback_port_range"] == (1455, 1465)
        assert CHATGPT_OAUTH_CONFIG["scope"] == "openid profile email offline_access"
        assert CHATGPT_OAUTH_CONFIG["provider_key"] == "chatgpt-oauth"

    def test_default_codex_models(self):
        assert "gpt-5.4" in DEFAULT_CODEX_MODELS
        assert len(DEFAULT_CODEX_MODELS) > 0


# ---------------------------------------------------------------------------
# Code exchange
# ---------------------------------------------------------------------------


class TestExchangeCode:
    def _make_context(self) -> OAuthContext:
        ctx = prepare_oauth_context()
        ctx.redirect_uri = "http://localhost:1455/callback"
        return ctx

    def test_exchange_with_org_structure(self):
        id_claims = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-123",
                "organizations": [
                    {"id": "org-default", "is_default": True, "role": "owner"},
                    {"id": "org-other", "is_default": False},
                ],
            }
        }
        access_claims = {"chatgpt_plan_type": "plus"}

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": _make_jwt(access_claims),
            "refresh_token": "rt-123",
            "id_token": _make_jwt(id_claims),
        }

        with patch("gac.oauth.chatgpt.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt.get_ssl_verify", return_value=True):
                result = _exchange_code("test_code", self._make_context())

        assert result["account_id"] == "acc-123"
        assert result["org_id"] == "org-default"
        assert result["plan_type"] == "plus"

    def test_exchange_no_default_org(self):
        id_claims = {
            "https://api.openai.com/auth": {
                "chatgpt_account_id": "acc-456",
                "organizations": [{"id": "org-first"}],
            }
        }
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": _make_jwt({}),
            "refresh_token": "rt-456",
            "id_token": _make_jwt(id_claims),
        }

        with patch("gac.oauth.chatgpt.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt.get_ssl_verify", return_value=True):
                result = _exchange_code("code", self._make_context())
        assert result["org_id"] == "org-first"

    def test_exchange_no_organizations(self):
        id_claims = {
            "https://api.openai.com/auth": {"chatgpt_account_id": "acc-789"},
            "organization_id": "org-from-id-token",
        }
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": _make_jwt({}),
            "refresh_token": "rt-789",
            "id_token": _make_jwt(id_claims),
        }

        with patch("gac.oauth.chatgpt.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt.get_ssl_verify", return_value=True):
                result = _exchange_code("code", self._make_context())
        assert result["org_id"] == "org-from-id-token"

    def test_exchange_no_org_at_all(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "access_token": _make_jwt({}),
            "refresh_token": "rt-999",
            "id_token": _make_jwt({"sub": "user123"}),
        }

        with patch("gac.oauth.chatgpt.httpx.post", return_value=mock_response):
            with patch("gac.oauth.chatgpt.get_ssl_verify", return_value=True):
                result = _exchange_code("code", self._make_context())
        assert result["org_id"] == ""

    def test_exchange_no_redirect_uri(self):
        ctx = prepare_oauth_context()
        assert _exchange_code("code", ctx) is None

    def test_exchange_exception(self):
        with patch("gac.oauth.chatgpt.httpx.post", side_effect=Exception("Network error")):
            with patch("gac.oauth.chatgpt.get_ssl_verify", return_value=True):
                ctx = self._make_context()
                assert _exchange_code("code", ctx) is None


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


class TestRefreshAccessToken:
    def test_delegates_to_base_refresh(self):
        """refresh_access_token delegates to _base_refresh with correct args."""
        with patch.object(chatgpt_module, "_base_refresh", return_value="new_at") as m:
            assert refresh_access_token() == "new_at"
            m.assert_called_once()
            # Verify it passes the ChatGPT config
            call_kwargs = m.call_args
            assert call_kwargs.kwargs.get("provider_key") == PROVIDER_KEY

    def test_returns_none_on_failure(self):
        with patch.object(chatgpt_module, "_base_refresh", return_value=None):
            assert refresh_access_token() is None


class TestRefreshTokenIfExpired:
    def test_not_expired(self):
        with patch.object(chatgpt_module, "is_token_expired", return_value=False):
            assert refresh_token_if_expired(quiet=True) is True

    def test_expired_refresh_succeeds(self):
        with patch.object(chatgpt_module, "is_token_expired", return_value=True):
            with patch.object(chatgpt_module, "refresh_access_token", return_value="new_at"):
                assert refresh_token_if_expired(quiet=True) is True

    def test_expired_refresh_fails(self):
        with patch.object(chatgpt_module, "is_token_expired", return_value=True):
            with patch.object(chatgpt_module, "refresh_access_token", return_value=None):
                assert refresh_token_if_expired(quiet=True) is False


# ---------------------------------------------------------------------------
# Wrapper delegation
# ---------------------------------------------------------------------------


class TestWrapperDelegation:
    def test_perform_oauth_flow_delegates(self):
        with patch.object(chatgpt_module, "_base_flow", return_value={"access_token": "at"}) as m:
            assert perform_oauth_flow(quiet=True) == {"access_token": "at"}
            m.assert_called_once()

    def test_authenticate_and_save_delegates(self):
        with patch.object(chatgpt_module, "_base_authenticate", return_value=True) as m:
            assert authenticate_and_save(quiet=True) is True
            m.assert_called_once()


# ---------------------------------------------------------------------------
# ensure_oauth_token (ai_utils.py)
# ---------------------------------------------------------------------------


class TestEnsureOAuthToken:
    def test_non_oauth_provider_noop(self):
        from gac.ai_utils import _ensure_oauth_token

        _ensure_oauth_token("openai")

    def test_claude_code_no_token_raises(self):
        from gac.ai_utils import _ensure_oauth_token
        from gac.errors import AIError

        with patch("gac.ai_utils.refresh_token_if_expired", return_value=False):
            with pytest.raises(AIError, match="claude-code"):
                _ensure_oauth_token("claude-code")

    def test_chatgpt_no_token_raises(self):
        from gac.ai_utils import _ensure_oauth_token
        from gac.errors import AIError

        with patch("gac.oauth.chatgpt.is_token_expired", return_value=True):
            with patch("gac.oauth.chatgpt.refresh_access_token", return_value=None):
                with pytest.raises(AIError, match="chatgpt-oauth"):
                    _ensure_oauth_token("chatgpt-oauth")
