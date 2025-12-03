"""Tests for token_store module."""

import os
from pathlib import Path

from gac.auth.token_store import OAuthToken, TokenStore


class TestTokenStore:
    """Tests for TokenStore class."""

    def test_init_default_directory(self, tmp_path, monkeypatch):
        """Test that default directory is created correctly."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        store = TokenStore()
        assert store.base_dir == tmp_path / ".gac" / "oauth"

    def test_init_custom_directory(self, tmp_path):
        """Test initialization with custom directory."""
        custom_dir = tmp_path / "custom" / "oauth"
        store = TokenStore(custom_dir)
        assert store.base_dir == custom_dir
        assert custom_dir.exists()

    def test_directory_permissions(self, tmp_path):
        """Test that directory is created with secure permissions."""
        oauth_dir = tmp_path / "oauth"
        TokenStore(oauth_dir)
        mode = os.stat(oauth_dir).st_mode
        assert mode & 0o777 == 0o700

    def test_save_and_get_token(self, tmp_path):
        """Test saving and retrieving a token."""
        store = TokenStore(tmp_path)
        token: OAuthToken = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expiry": 1234567890,
            "token_type": "Bearer",
            "scope": "openid profile",
            "resource_url": "https://api.example.com",
        }

        store.save_token("test_provider", token)
        retrieved = store.get_token("test_provider")

        assert retrieved == token

    def test_token_file_permissions(self, tmp_path):
        """Test that token files have secure permissions."""
        store = TokenStore(tmp_path)
        token: OAuthToken = {
            "access_token": "test_token",
            "expiry": 1234567890,
            "token_type": "Bearer",
        }

        store.save_token("test_provider", token)
        token_path = tmp_path / "test_provider.json"
        mode = os.stat(token_path).st_mode
        assert mode & 0o777 == 0o600

    def test_get_nonexistent_token(self, tmp_path):
        """Test getting a token that doesn't exist."""
        store = TokenStore(tmp_path)
        result = store.get_token("nonexistent")
        assert result is None

    def test_remove_token(self, tmp_path):
        """Test removing a token."""
        store = TokenStore(tmp_path)
        token: OAuthToken = {
            "access_token": "test_token",
            "expiry": 1234567890,
            "token_type": "Bearer",
        }

        store.save_token("test_provider", token)
        assert store.get_token("test_provider") is not None

        store.remove_token("test_provider")
        assert store.get_token("test_provider") is None

    def test_remove_nonexistent_token(self, tmp_path):
        """Test removing a token that doesn't exist (should not raise)."""
        store = TokenStore(tmp_path)
        store.remove_token("nonexistent")

    def test_list_providers(self, tmp_path):
        """Test listing providers with stored tokens."""
        store = TokenStore(tmp_path)
        token: OAuthToken = {
            "access_token": "test_token",
            "expiry": 1234567890,
            "token_type": "Bearer",
        }

        store.save_token("provider1", token)
        store.save_token("provider2", token)

        providers = store.list_providers()
        assert sorted(providers) == ["provider1", "provider2"]

    def test_list_providers_empty(self, tmp_path):
        """Test listing providers when no tokens exist."""
        store = TokenStore(tmp_path)
        providers = store.list_providers()
        assert providers == []

    def test_atomic_write(self, tmp_path):
        """Test that token writes are atomic (temp file + rename)."""
        store = TokenStore(tmp_path)
        token: OAuthToken = {
            "access_token": "test_token",
            "expiry": 1234567890,
            "token_type": "Bearer",
        }

        store.save_token("test_provider", token)

        temp_file = tmp_path / "test_provider.tmp"
        assert not temp_file.exists()

        token_file = tmp_path / "test_provider.json"
        assert token_file.exists()
