"""Tests for ChatGPT OAuth authentication."""

import base64
import json
import string
import time
from unittest.mock import MagicMock, patch

import pytest

from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG, DEFAULT_CODEX_MODELS
from gac.oauth.chatgpt_server import (
    OAuthContext,
    _compute_code_challenge,
    _generate_code_verifier,
    _urlsafe_b64encode,
    prepare_oauth_context,
)
from gac.oauth.chatgpt_tokens import (
    _provider_key,
    is_token_expired,
    parse_jwt_claims,
    refresh_access_token,
    save_token,
)

# Reference to the tokens module for patching
# ruff: noqa: E402, I001
import gac.oauth.chatgpt_tokens as chatgpt_tokens_module


class _FakeTokenStore:
    """Minimal fake TokenStore for unit tests."""

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._tokens: dict[str, dict] = {}

    def get_token(self, provider: str):
        return self._tokens.get(provider)

    def save_token(self, provider: str, token: dict) -> None:
        self._tokens[provider] = token

    def remove_token(self, provider: str) -> None:
        self._tokens.pop(provider, None)


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------


def test_urlsafe_b64encode_strips_padding() -> None:
    encoded = _urlsafe_b64encode(b"\xff\xef")
    assert "=" not in encoded
    assert encoded == "_-8"


def test_generate_code_verifier_is_hex() -> None:
    verifier = _generate_code_verifier()
    assert isinstance(verifier, str)
    assert len(verifier) == 128  # secrets.token_hex(64) → 128 hex chars
    assert set(verifier) <= set(string.hexdigits)


def test_compute_code_challenge_known_value() -> None:
    """SHA-256 of 'abc' is a known value."""
    challenge = _compute_code_challenge("abc")
    assert challenge == "ungWv48Bz-pBQUDeXa4iI7ADYaOWF3qctBD_YfIAFa0"


# ---------------------------------------------------------------------------
# OAuth context
# ---------------------------------------------------------------------------


def test_prepare_oauth_context_generates_valid_pkce() -> None:
    ctx = prepare_oauth_context()
    assert len(ctx.state) >= 32
    assert len(ctx.code_verifier) >= 43
    assert ctx.redirect_uri is None
    # Verify code_challenge matches the code_verifier
    expected = _compute_code_challenge(ctx.code_verifier)
    assert ctx.code_challenge == expected
    assert ctx.expires_at is not None


def test_oauth_context_is_expired_future() -> None:
    ctx = OAuthContext(
        state="s",
        code_verifier="v",
        code_challenge="c",
        created_at=time.time(),
        expires_at=time.time() + 600,
    )
    assert not ctx.is_expired()


def test_oauth_context_is_expired_past() -> None:
    ctx = OAuthContext(
        state="s",
        code_verifier="v",
        code_challenge="c",
        created_at=time.time() - 600,
        expires_at=time.time() - 60,
    )
    assert ctx.is_expired()


def test_oauth_context_is_expired_no_expiry() -> None:
    """When expires_at is None, use 5-minute default from created_at."""
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


def test_parse_jwt_claims_valid() -> None:
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "user123"}).encode()).decode()
    token = f"header.{payload}.signature"
    claims = parse_jwt_claims(token)
    assert claims is not None
    assert claims["sub"] == "user123"


def test_parse_jwt_claims_invalid() -> None:
    assert parse_jwt_claims("") is None
    assert parse_jwt_claims("invalid") is None
    assert parse_jwt_claims("a.b") is None


def test_parse_jwt_claims_with_org_structure() -> None:
    """Test JWT parsing with nested organization structure like real payloads."""
    mock_claims = {
        "aud": ["app_EMoamEEZ73f0CkXaXp7hrann"],
        "email": "test@example.com",
        "https://api.openai.com/auth": {
            "chatgpt_account_id": "d1844a91-9aac-419b-903e-f6a99c76f163",
            "organizations": [
                {"id": "org-abc123", "is_default": True, "role": "owner", "title": "Personal"},
            ],
        },
    }
    payload = base64.urlsafe_b64encode(json.dumps(mock_claims).encode()).decode()
    token = f"header.{payload}.sig"
    claims = parse_jwt_claims(token)
    assert claims is not None
    auth = claims.get("https://api.openai.com/auth", {})
    orgs = auth.get("organizations", [])
    assert len(orgs) == 1
    assert orgs[0]["id"] == "org-abc123"


# ---------------------------------------------------------------------------
# Token storage — uses OAuthToken.extra dict (no sidecar files)
# ---------------------------------------------------------------------------


def test_save_and_load_token(tmp_path) -> None:
    fake = _FakeTokenStore(tmp_path)
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
        assert save_token("test_access_token")
        # Verify via the same fake store
        saved = fake.get_token(_provider_key())
        assert saved is not None
        assert saved["access_token"] == "test_access_token"
        assert saved["token_type"] == "Bearer"


def test_save_token_with_extra_metadata(tmp_path) -> None:
    fake = _FakeTokenStore(tmp_path)
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
        assert save_token("at", token_data={"account_id": "acc123", "org_id": "org-1", "plan_type": "plus"})
        saved = fake.get_token(_provider_key())
        assert saved is not None
        assert saved["extra"]["account_id"] == "acc123"
        assert saved["extra"]["org_id"] == "org-1"


def test_load_stored_token_empty(tmp_path) -> None:
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=_FakeTokenStore(tmp_path)):
        from gac.oauth.chatgpt_tokens import load_stored_token

        assert load_stored_token() is None


def test_load_stored_tokens_flattens_extra(tmp_path) -> None:
    store = _FakeTokenStore(tmp_path)
    store.save_token(
        _provider_key(),
        {
            "access_token": "at",
            "token_type": "Bearer",
            "extra": {"account_id": "acc123", "org_id": "org-1"},
        },
    )
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=store):
        from gac.oauth.chatgpt_tokens import load_stored_tokens

        tokens = load_stored_tokens()
    assert tokens is not None
    assert tokens["account_id"] == "acc123"
    assert tokens["org_id"] == "org-1"
    assert tokens["access_token"] == "at"


def test_remove_token(tmp_path) -> None:
    store = _FakeTokenStore(tmp_path)
    store.save_token(_provider_key(), {"access_token": "tok", "token_type": "Bearer"})
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=store):
        from gac.oauth.chatgpt_tokens import remove_token

        assert remove_token()


# ---------------------------------------------------------------------------
# Token expiry
# ---------------------------------------------------------------------------


def test_is_token_expired_no_token(tmp_path) -> None:
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=_FakeTokenStore(tmp_path)):
        assert is_token_expired()


def test_is_token_expired_with_expiry_future(tmp_path) -> None:
    store = _FakeTokenStore(tmp_path)
    store.save_token(
        _provider_key(),
        {
            "access_token": "tok",
            "token_type": "Bearer",
            "expiry": int(time.time() + 3600),
        },
    )
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=store):
        assert not is_token_expired()


def test_is_token_expired_with_expiry_past(tmp_path) -> None:
    store = _FakeTokenStore(tmp_path)
    store.save_token(
        _provider_key(),
        {
            "access_token": "tok",
            "token_type": "Bearer",
            "expiry": int(time.time() - 60),
        },
    )
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=store):
        assert is_token_expired()


def test_is_token_expired_with_jwt_exp(tmp_path) -> None:
    """When no 'expiry' field, check JWT 'exp' claim."""
    claims = {"exp": int(time.time() + 3600)}
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode()
    token = f"header.{payload}.sig"
    store = _FakeTokenStore(tmp_path)
    store.save_token(_provider_key(), {"access_token": token, "token_type": "Bearer"})
    with patch.object(chatgpt_tokens_module, "TokenStore", return_value=store):
        assert not is_token_expired()


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


@patch("gac.oauth.chatgpt_tokens.httpx.post")
def test_refresh_access_token_success(mock_post) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new_at",
        "refresh_token": "new_rt",
        "id_token": "new_id",
    }
    mock_post.return_value = mock_response

    with patch.object(chatgpt_tokens_module, "TokenStore") as MockStore:
        store = MagicMock()
        store.get_token.return_value = {
            "access_token": "old_at",
            "token_type": "Bearer",
            "refresh_token": "old_rt",
        }
        MockStore.return_value = store
        with patch.object(chatgpt_tokens_module, "save_token", return_value=True):
            result = refresh_access_token()
    assert result == "new_at"


@patch("gac.oauth.chatgpt_tokens.httpx.post")
def test_refresh_access_token_failure(mock_post) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    with patch.object(chatgpt_tokens_module, "TokenStore") as MockStore:
        store = MagicMock()
        store.get_token.return_value = {
            "access_token": "old_at",
            "token_type": "Bearer",
            "refresh_token": "old_rt",
        }
        MockStore.return_value = store
        result = refresh_access_token()
    assert result is None


def test_refresh_access_token_no_refresh_token() -> None:
    with patch.object(chatgpt_tokens_module, "TokenStore") as MockStore:
        store = MagicMock()
        store.get_token.return_value = {
            "access_token": "at",
            "token_type": "Bearer",
        }
        MockStore.return_value = store
        result = refresh_access_token()
    assert result is None


# ---------------------------------------------------------------------------
# Config values
# ---------------------------------------------------------------------------


def test_chatgpt_oauth_config_values() -> None:
    assert CHATGPT_OAUTH_CONFIG["issuer"] == "https://auth.openai.com"
    assert CHATGPT_OAUTH_CONFIG["client_id"] == "app_EMoamEEZ73f0CkXaXp7hrann"
    assert CHATGPT_OAUTH_CONFIG["callback_port_range"] == (1455, 1465)
    assert CHATGPT_OAUTH_CONFIG["scope"] == "openid profile email offline_access"
    assert CHATGPT_OAUTH_CONFIG["provider_key"] == "chatgpt-oauth"


def test_default_codex_models() -> None:
    assert "gpt-5.4" in DEFAULT_CODEX_MODELS
    assert "gpt-5.3-codex" in DEFAULT_CODEX_MODELS
    assert len(DEFAULT_CODEX_MODELS) > 0


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------


def test_success_html_contains_message() -> None:
    from gac.oauth.chatgpt_server import _get_success_html

    html = _get_success_html()
    assert "ChatGPT OAuth Complete" in html


def test_failure_html_contains_reason() -> None:
    from gac.oauth.chatgpt_server import _get_failure_html

    html = _get_failure_html("Token exchange failed")
    assert "ChatGPT OAuth Failed" in html
    assert "Token exchange failed" in html


# ---------------------------------------------------------------------------
# _ensure_oauth_token (ai_utils.py)
# ---------------------------------------------------------------------------


def test_ensure_oauth_token_non_oauth_provider() -> None:
    """Non-OAuth providers should be a no-op."""
    from gac.ai_utils import _ensure_oauth_token

    # Should not raise for non-OAuth providers
    _ensure_oauth_token("openai")


def test_ensure_oauth_token_claude_code_no_token() -> None:
    """Should raise AIError when claude-code has no token."""
    from gac.ai_utils import _ensure_oauth_token
    from gac.errors import AIError

    with patch("gac.ai_utils.refresh_token_if_expired", return_value=False):
        with pytest.raises(AIError, match="claude-code"):
            _ensure_oauth_token("claude-code")


def test_ensure_oauth_token_chatgpt_no_token() -> None:
    """Should raise AIError when chatgpt-oauth has no token."""
    from gac.ai_utils import _ensure_oauth_token
    from gac.errors import AIError

    with patch("gac.oauth.chatgpt.is_token_expired", return_value=True):
        with patch("gac.oauth.chatgpt.refresh_access_token", return_value=None):
            with pytest.raises(AIError, match="chatgpt-oauth"):
                _ensure_oauth_token("chatgpt-oauth")

    """Minimal fake TokenStore for unit tests."""

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._tokens: dict[str, dict] = {}

    def get_token(self, provider: str):
        return self._tokens.get(provider)

    def save_token(self, provider: str, token: dict) -> None:
        self._tokens[provider] = token

    def remove_token(self, provider: str) -> None:
        self._tokens.pop(provider, None)
