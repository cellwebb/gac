"""Shared test fixtures for OAuth tests."""

import pytest


class FakeTokenStore:
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


@pytest.fixture
def fake_token_store(tmp_path):
    """Provide a FakeTokenStore instance."""
    return FakeTokenStore(tmp_path)
