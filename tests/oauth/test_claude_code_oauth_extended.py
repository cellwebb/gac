"""Extended tests to improve claude_code.py coverage."""

import os
from unittest import mock

from gac.oauth import claude_code


def test_load_stored_token_success(monkeypatch):
    """Test successful token loading from store."""
    # Mock token data
    mock_token = {"access_token": "test_token_123", "expiry": 9999999999}

    def mock_get_token(provider: str):
        if provider == "claude-code":
            return mock_token
        return None

    # Mock at instance level
    with mock.patch.object(claude_code.TokenStore, "get_token", side_effect=mock_get_token):
        result = claude_code.load_stored_token()
        assert result == "test_token_123"


def test_load_stored_token_not_found(monkeypatch):
    """Test token loading when no token is stored."""
    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=None):
        result = claude_code.load_stored_token()
        assert result is None


def test_is_token_expired_with_expiry(monkeypatch):
    """Test token expiry check with expiry information."""
    # Mock expired token
    current_time = 1000
    expired_token = {"expiry": current_time - 60}  # Expired 1 minute ago

    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=expired_token):
        with mock.patch("time.time", return_value=current_time):
            result = claude_code.is_token_expired()
            assert result is True


def test_is_token_expired_no_expiry_info(monkeypatch):
    """Test token expiry check when no expiry information is available."""
    token_without_expiry = {"access_token": "test_token"}  # No expiry

    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=token_without_expiry):
        result = claude_code.is_token_expired()
        assert result is False  # Should assume valid if no expiry info


def test_is_token_expired_within_5_minutes(monkeypatch):
    """Test token expiry check when token expires within 5 minutes."""
    current_time = 1000
    expiring_token = {"expiry": current_time + 120}  # Expires in 2 minutes

    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=expiring_token):
        with mock.patch("time.time", return_value=current_time):
            result = claude_code.is_token_expired()
            assert result is True  # Should consider expired if within 5 minutes


def test_is_token_expired_no_token(monkeypatch):
    """Test token expiry check when no token exists."""
    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=None):
        result = claude_code.is_token_expired()
        assert result is True  # Should consider expired if no token


def test_refresh_token_if_expired_valid_token(monkeypatch):
    """Test refresh when token is already valid."""
    # Mock a valid token
    current_time = 1000
    valid_token = {"expiry": current_time + 3600}  # Expires in 1 hour

    # Mock both token access and authenticate function
    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=valid_token):
        with mock.patch("time.time", return_value=current_time):
            with mock.patch.object(claude_code, "authenticate_and_save", return_value=True) as mock_auth:
                result = claude_code.refresh_token_if_expired(quiet=True)
                assert result is True
                # Should not call authenticate since token is valid
                mock_auth.assert_not_called()


def test_refresh_token_if_expired_successful_refresh(monkeypatch):
    """Test successful token refresh when expired."""
    # Mock expired token
    current_time = 1000
    expired_token = {"expiry": current_time - 60}

    # Mock both token access and authenticate function
    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=expired_token):
        with mock.patch("time.time", return_value=current_time):
            with mock.patch.object(claude_code, "authenticate_and_save", return_value=True) as mock_auth:
                result = claude_code.refresh_token_if_expired(quiet=True)
                assert result is True
                mock_auth.assert_called_once_with(quiet=True)


def test_refresh_token_if_expired_failed_refresh(monkeypatch):
    """Test failed token refresh when expired."""
    # Mock expired token
    current_time = 1000
    expired_token = {"expiry": current_time - 60}

    # Mock both token access and authenticate function
    with mock.patch.object(claude_code.TokenStore, "get_token", return_value=expired_token):
        with mock.patch("time.time", return_value=current_time):
            with mock.patch.object(claude_code, "authenticate_and_save", return_value=False) as mock_auth:
                result = claude_code.refresh_token_if_expired(quiet=True)
                assert result is False
                mock_auth.assert_called_once_with(quiet=True)


def test_save_token_with_expiry_in_data(monkeypatch):
    """Test saving token with expiry information in token_data."""
    mock_store = mock.Mock()
    monkeypatch.setattr(claude_code.TokenStore, "save_token", mock_store)

    # Mock environment variable access
    mock_env = {}
    monkeypatch.setattr(os, "environ", mock_env)

    token_data = {"access_token": "new_token_123", "expires_in": 3600, "token_type": "Bearer"}

    current_time = 1000

    with mock.patch("time.time", return_value=current_time):
        result = claude_code.save_token("new_token_123", token_data)

    assert result is True
    mock_store.assert_called_once_with("claude-code", mock.ANY)

    # Check that the saved token has expiry calculated
    saved_token = mock_store.call_args[0][1]
    assert saved_token["access_token"] == "new_token_123"
    assert saved_token["token_type"] == "Bearer"
    assert saved_token["expiry"] == current_time + 3600

    # Check environment variable was set
    assert mock_env["CLAUDE_CODE_ACCESS_TOKEN"] == "new_token_123"


def test_save_token_without_expiry_data(monkeypatch):
    """Test saving token without expiry information."""
    mock_store = mock.Mock()
    monkeypatch.setattr(claude_code.TokenStore, "save_token", mock_store)

    # Mock environment variable access
    mock_env = {}
    monkeypatch.setattr(os, "environ", mock_env)

    result = claude_code.save_token("simple_token")

    assert result is True
    mock_store.assert_called_once_with("claude-code", mock.ANY)

    # Check that the saved token has no expiry
    saved_token = mock_store.call_args[0][1]
    assert saved_token["access_token"] == "simple_token"
    assert saved_token["token_type"] == "Bearer"
    assert "expiry" not in saved_token

    # Check environment variable was set
    assert mock_env["CLAUDE_CODE_ACCESS_TOKEN"] == "simple_token"


def test_save_token_failure(monkeypatch):
    """Test saving token when store operation fails."""

    def mock_store_error(*args, **kwargs):
        raise Exception("Storage error")

    monkeypatch.setattr(claude_code.TokenStore, "save_token", mock_store_error)

    # Mock environment variable access
    mock_env = {}
    monkeypatch.setattr(os, "environ", mock_env)

    result = claude_code.save_token("test_token")

    assert result is False
    assert "CLAUDE_CODE_ACCESS_TOKEN" not in mock_env


def test_remove_token_success(monkeypatch):
    """Test successful token removal."""
    mock_store = mock.Mock()
    monkeypatch.setattr(claude_code.TokenStore, "remove_token", mock_store)

    # Mock environment variable access
    mock_env = {"CLAUDE_CODE_ACCESS_TOKEN": "existing_token"}
    monkeypatch.setattr(os, "environ", mock_env)

    result = claude_code.remove_token()

    assert result is True
    mock_store.assert_called_once_with("claude-code")
    assert "CLAUDE_CODE_ACCESS_TOKEN" not in mock_env


def test_remove_token_failure(monkeypatch):
    """Test token removal when store operation fails."""

    def mock_store_error(*args, **kwargs):
        raise Exception("Removal error")

    monkeypatch.setattr(claude_code.TokenStore, "remove_token", mock_store_error)

    # Mock environment variable access
    mock_env = {"CLAUDE_CODE_ACCESS_TOKEN": "existing_token"}
    monkeypatch.setattr(os, "environ", mock_env)

    result = claude_code.remove_token()

    assert result is False
    assert "CLAUDE_CODE_ACCESS_TOKEN" in mock_env  # Should not be removed on failure


def test_authenticate_and_save_success(monkeypatch):
    """Test successful authentication and token saving."""
    # Mock OAuth flow return
    oauth_tokens = {"access_token": "oauth_token_123", "expires_in": 3600, "token_type": "Bearer"}

    with mock.patch.object(claude_code, "perform_oauth_flow", return_value=oauth_tokens):
        with mock.patch.object(claude_code, "save_token", return_value=True) as mock_save:
            result = claude_code.authenticate_and_save(quiet=True)

            assert result is True
            claude_code.perform_oauth_flow.assert_called_once_with(quiet=True)
            mock_save.assert_called_once_with("oauth_token_123", token_data=oauth_tokens)


def test_authenticate_and_save_no_tokens(monkeypatch):
    """Test authentication when OAuth flow returns no tokens."""
    with mock.patch.object(claude_code, "perform_oauth_flow", return_value=None):
        with mock.patch.object(claude_code, "save_token") as mock_save:
            result = claude_code.authenticate_and_save(quiet=True)

            assert result is False
            claude_code.perform_oauth_flow.assert_called_once_with(quiet=True)
            mock_save.assert_not_called()


def test_authenticate_and_save_no_access_token(monkeypatch):
    """Test authentication when OAuth response has no access token."""
    oauth_tokens = {
        "refresh_token": "refresh_123",
        "token_type": "Bearer",
        # No access_token key
    }

    with mock.patch.object(claude_code, "perform_oauth_flow", return_value=oauth_tokens):
        with mock.patch.object(claude_code, "save_token") as mock_save:
            with mock.patch("builtins.print"):
                result = claude_code.authenticate_and_save(quiet=False)

                assert result is False
                claude_code.perform_oauth_flow.assert_called_once_with(quiet=False)
                mock_save.assert_not_called()


def test_authenticate_and_save_save_failure(monkeypatch):
    """Test authentication when token saving fails."""
    oauth_tokens = {"access_token": "oauth_token_123", "expires_in": 3600, "token_type": "Bearer"}

    with mock.patch.object(claude_code, "perform_oauth_flow", return_value=oauth_tokens):
        with mock.patch.object(claude_code, "save_token", return_value=False) as mock_save:
            with mock.patch("builtins.print"):
                result = claude_code.authenticate_and_save(quiet=False)

                assert result is False
                claude_code.perform_oauth_flow.assert_called_once_with(quiet=False)
                mock_save.assert_called_once_with("oauth_token_123", token_data=oauth_tokens)
