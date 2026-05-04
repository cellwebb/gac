"""Additional tests for chatgpt_tokens module to improve coverage."""

import base64
import json
import os
import time
from unittest.mock import MagicMock, patch

import gac.oauth.chatgpt_tokens as chatgpt_tokens_module
from gac.oauth.chatgpt_config import CHATGPT_OAUTH_CONFIG
from gac.oauth.chatgpt_tokens import (
    _provider_key,
    is_token_expired,
    load_stored_tokens,
    parse_jwt_claims,
    refresh_access_token,
    refresh_token_if_expired,
    remove_token,
    save_token,
)


class _FakeTokenStore:
    """Minimal fake TokenStore for unit tests."""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir
        self._tokens: dict[str, dict] = {}

    def get_token(self, provider: str):
        return self._tokens.get(provider)

    def save_token(self, provider: str, token: dict) -> None:
        self._tokens[provider] = token

    def remove_token(self, provider: str) -> None:
        self._tokens.pop(provider, None)


def _make_jwt(payload: dict) -> str:
    """Create a JWT-like string from a payload dict."""
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return f"header.{encoded}.signature"


class TestParseJwtClaimsEdgeCases:
    """Additional edge cases for JWT parsing."""

    def test_parse_jwt_non_dict_payload(self):
        """JWT payload that decodes to a non-dict should return None."""
        encoded = base64.urlsafe_b64encode(json.dumps([1, 2, 3]).encode()).decode()
        token = f"header.{encoded}.sig"
        assert parse_jwt_claims(token) is None

    def test_parse_jwt_invalid_base64(self):
        """JWT with invalid base64 should return None."""
        assert parse_jwt_claims("a.!!!invalid.b64.sig") is None

    def test_parse_jwt_empty_string(self):
        assert parse_jwt_claims("") is None

    def test_parse_jwt_two_parts_only(self):
        assert parse_jwt_claims("a.b") is None


class TestSaveTokenEdgeCases:
    """Additional edge cases for save_token."""

    def test_save_token_with_jwt_exp(self):
        """save_token extracts exp from JWT claims."""
        exp_val = int(time.time() + 3600)
        token_str = _make_jwt({"exp": exp_val})

        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = save_token(token_str)
            assert result is True
            saved = fake.get_token(_provider_key())
            assert saved is not None
            assert saved["expiry"] == exp_val

    def test_save_token_with_expires_at(self):
        """save_token uses expires_at from token_data."""
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = save_token("at", token_data={"expires_at": 1700000000})
            assert result is True
            saved = fake.get_token(_provider_key())
            assert saved is not None
            assert saved["expiry"] == 1700000000

    def test_save_token_with_expires_in(self):
        """save_token computes expiry from expires_in."""
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = save_token("at", token_data={"expires_in": 3600})
            assert result is True
            saved = fake.get_token(_provider_key())
            assert saved is not None
            assert saved["expiry"] > int(time.time())

    def test_save_token_with_empty_extra_fields(self):
        """Empty extra fields should not be stored."""
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = save_token("at", token_data={"account_id": "", "org_id": None})
            assert result is True
            saved = fake.get_token(_provider_key())
            assert "extra" not in saved

    def test_save_token_sets_env_var(self):
        """save_token sets the API key env var."""
        fake = _FakeTokenStore()
        env_var = CHATGPT_OAUTH_CONFIG["api_key_env_var"]
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            save_token("my_access_token")

        assert os.environ.get(env_var) == "my_access_token"

    def test_save_token_exception_returns_false(self):
        """save_token returns False on exception."""
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            with patch.object(fake, "save_token", side_effect=RuntimeError("broken")):
                assert save_token("at") is False


class TestLoadStoredTokensEdgeCases:
    """Additional edge cases for load_stored_tokens."""

    def test_load_stored_tokens_no_extra(self):
        """When no extra dict, just return token dict."""
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": "at", "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = load_stored_tokens()
        assert result is not None
        assert result["access_token"] == "at"

    def test_load_stored_tokens_none_token(self):
        """When no token stored, return None."""
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = load_stored_tokens()
        assert result is None


class TestRemoveTokenEdgeCases:
    """Additional edge cases for remove_token."""

    def test_remove_token_exception_returns_false(self):
        """remove_token returns False on exception."""
        with patch.object(chatgpt_tokens_module, "TokenStore") as MockStore:
            store = MagicMock()
            store.remove_token.side_effect = RuntimeError("fail")
            MockStore.return_value = store
            assert remove_token() is False

    def test_remove_token_clears_env_var(self):
        """remove_token clears the API key env var."""
        env_var = CHATGPT_OAUTH_CONFIG["api_key_env_var"]
        os.environ[env_var] = "test_value"
        fake = _FakeTokenStore()
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = remove_token()
        assert result is True
        assert env_var not in os.environ


class TestIsTokenExpiredEdgeCases:
    """Additional edge cases for is_token_expired."""

    def test_expired_jwt_exp_float(self):
        """When exp is a float, should still detect expiry."""
        claims = {"exp": time.time() - 100}  # Expired
        token_str = _make_jwt(claims)
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": token_str, "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            assert is_token_expired() is True

    def test_valid_jwt_exp(self):
        """When exp is in the future, should not be expired."""
        claims = {"exp": time.time() + 3600}  # Valid
        token_str = _make_jwt(claims)
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": token_str, "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            assert is_token_expired() is False

    def test_no_expiry_no_jwt_claims(self):
        """When no expiry and no JWT claims, assume still valid."""
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": "not-a-jwt", "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            assert is_token_expired() is False

    def test_jwt_exp_non_numeric(self):
        """When JWT exp is not numeric, assume valid."""
        claims = {"exp": "not-a-number"}
        token_str = _make_jwt(claims)
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": token_str, "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            assert is_token_expired() is False


class TestRefreshAccessTokenEdgeCases:
    """Additional edge cases for refresh_access_token."""

    def test_refresh_no_tokens_stored(self):
        """When no tokens stored, return None."""
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=_FakeTokenStore()):
            assert refresh_access_token() is None

    def test_refresh_no_refresh_token(self):
        """When no refresh_token in stored tokens, return None."""
        fake = _FakeTokenStore()
        fake.save_token(_provider_key(), {"access_token": "at", "token_type": "Bearer"})
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            assert refresh_access_token() is None

    @patch("gac.oauth.chatgpt_tokens.httpx.post")
    def test_refresh_success(self, mock_post):
        """Successful refresh."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_at",
            "refresh_token": "new_rt",
            "id_token": "new_id",
        }
        mock_post.return_value = mock_response

        fake = _FakeTokenStore()
        fake.save_token(
            _provider_key(),
            {
                "access_token": "old_at",
                "token_type": "Bearer",
                "refresh_token": "old_rt",
            },
        )
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            with patch.object(chatgpt_tokens_module, "save_token", return_value=True):
                result = refresh_access_token()
        assert result == "new_at"

    @patch("gac.oauth.chatgpt_tokens.httpx.post")
    def test_refresh_response_no_access_token(self, mock_post):
        """When refresh response has no access_token, return None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"refresh_token": "new_rt"}
        mock_post.return_value = mock_response

        fake = _FakeTokenStore()
        fake.save_token(
            _provider_key(),
            {
                "access_token": "old_at",
                "token_type": "Bearer",
                "refresh_token": "old_rt",
            },
        )
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = refresh_access_token()
        assert result is None

    @patch("gac.oauth.chatgpt_tokens.httpx.post")
    def test_refresh_non_200_status(self, mock_post):
        """When refresh returns non-200 status, return None."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        fake = _FakeTokenStore()
        fake.save_token(
            _provider_key(),
            {
                "access_token": "old_at",
                "token_type": "Bearer",
                "refresh_token": "old_rt",
            },
        )
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = refresh_access_token()
        assert result is None

    @patch("gac.oauth.chatgpt_tokens.httpx.post")
    def test_refresh_exception(self, mock_post):
        """When refresh raises an exception, return None."""
        mock_post.side_effect = Exception("Network error")

        fake = _FakeTokenStore()
        fake.save_token(
            _provider_key(),
            {
                "access_token": "old_at",
                "token_type": "Bearer",
                "refresh_token": "old_rt",
            },
        )
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            result = refresh_access_token()
        assert result is None

    @patch("gac.oauth.chatgpt_tokens.httpx.post")
    def test_refresh_save_fails(self, mock_post):
        """When save_token returns False after refresh, return None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_at",
            "refresh_token": "new_rt",
        }
        mock_post.return_value = mock_response

        fake = _FakeTokenStore()
        fake.save_token(
            _provider_key(),
            {
                "access_token": "old_at",
                "token_type": "Bearer",
                "refresh_token": "old_rt",
            },
        )
        with patch.object(chatgpt_tokens_module, "TokenStore", return_value=fake):
            with patch.object(chatgpt_tokens_module, "save_token", return_value=False):
                result = refresh_access_token()
        assert result is None


class TestRefreshTokenIfExpired:
    """Test refresh_token_if_expired function."""

    def test_not_expired_returns_true(self):
        """When token is not expired, return True without refreshing."""
        with patch.object(chatgpt_tokens_module, "is_token_expired", return_value=False):
            result = refresh_token_if_expired(quiet=True)
        assert result is True

    def test_expired_refresh_succeeds(self):
        """When expired and refresh succeeds, return True."""
        with patch.object(chatgpt_tokens_module, "is_token_expired", return_value=True):
            with patch.object(chatgpt_tokens_module, "refresh_access_token", return_value="new_at"):
                result = refresh_token_if_expired(quiet=True)
        assert result is True

    def test_expired_refresh_fails_verbose(self):
        """When expired and refresh fails in verbose mode, return False."""
        with patch.object(chatgpt_tokens_module, "is_token_expired", return_value=True):
            with patch.object(chatgpt_tokens_module, "refresh_access_token", return_value=None):
                result = refresh_token_if_expired(quiet=False)
        assert result is False

    def test_expired_refresh_fails_quiet(self):
        """When expired and refresh fails in quiet mode, return False."""
        with patch.object(chatgpt_tokens_module, "is_token_expired", return_value=True):
            with patch.object(chatgpt_tokens_module, "refresh_access_token", return_value=None):
                result = refresh_token_if_expired(quiet=True)
        assert result is False
