"""Tests for Copilot provider (copilot.py)."""

from unittest.mock import patch

import pytest

from gac.errors import AIError
from gac.providers.copilot import CopilotProvider


def _make_provider(api_key="test_session_token"):
    """Create a CopilotProvider with a mocked _get_api_key."""
    provider = CopilotProvider.__new__(CopilotProvider)
    provider.config = CopilotProvider.config
    provider._api_key = None
    provider._get_api_key = lambda: api_key  # type: ignore[assignment]
    return provider


class TestCopilotProviderAPIKey:
    """Test _get_api_key method."""

    def test_no_stored_tokens(self):
        """When no tokens stored, raise authentication error."""
        with patch("gac.providers.copilot.load_stored_tokens", return_value=None):
            provider = CopilotProvider.__new__(CopilotProvider)
            provider.config = CopilotProvider.config
            with pytest.raises(AIError, match="Copilot authentication not found"):
                provider._get_api_key()

    def test_no_access_token(self):
        """When tokens exist but no access_token, raise error."""
        with patch("gac.providers.copilot.load_stored_tokens", return_value={"host": "github.com"}):
            provider = CopilotProvider.__new__(CopilotProvider)
            provider.config = CopilotProvider.config
            with pytest.raises(AIError, match="Copilot OAuth token missing"):
                provider._get_api_key()

    def test_session_exchange_fails(self):
        """When session token exchange fails, raise error."""
        with patch(
            "gac.providers.copilot.load_stored_tokens",
            return_value={"access_token": "ghu_123", "host": "github.com"},
        ):
            with patch("gac.providers.copilot.get_valid_session_token", return_value=None):
                provider = CopilotProvider.__new__(CopilotProvider)
                provider.config = CopilotProvider.config
                with pytest.raises(AIError, match="Could not obtain Copilot session token"):
                    provider._get_api_key()

    def test_session_exchange_success(self):
        """When session token obtained, return it."""
        with patch(
            "gac.providers.copilot.load_stored_tokens",
            return_value={"access_token": "ghu_123", "host": "github.com"},
        ):
            with patch("gac.providers.copilot.get_valid_session_token", return_value="tid=abc"):
                provider = CopilotProvider.__new__(CopilotProvider)
                provider.config = CopilotProvider.config
                result = provider._get_api_key()
                assert result == "tid=abc"


class TestCopilotProviderHeaders:
    """Test _build_headers method."""

    def test_required_headers(self):
        """Headers include all required Copilot headers."""
        provider = _make_provider("tid=test")
        headers = provider._build_headers()

        assert headers["Authorization"] == "Bearer tid=test"
        assert "Editor-Version" in headers
        assert "Editor-Plugin-Version" in headers
        assert "Copilot-Integration-Id" in headers
        assert "Openai-Intent" in headers
        assert headers["Content-Type"] == "application/json"

    def test_no_x_api_key(self):
        """Headers should not include x-api-key."""
        provider = _make_provider()
        headers = provider._build_headers()
        assert "x-api-key" not in headers


class TestCopilotProviderAPIUrl:
    """Test _get_api_url method."""

    def test_default_url(self):
        """Default API URL uses githubcopilot.com."""
        with patch(
            "gac.providers.copilot.load_stored_tokens",
            return_value={"host": "github.com"},
        ):
            with patch("gac.providers.copilot.get_api_endpoint", return_value="https://api.githubcopilot.com"):
                provider = _make_provider()
                url = provider._get_api_url("gpt-4.1")
                assert url == "https://api.githubcopilot.com/chat/completions"

    def test_ghe_url(self):
        """GHE hosts get their own API endpoint."""
        with patch(
            "gac.providers.copilot.load_stored_tokens",
            return_value={"host": "ghe.company.com"},
        ):
            with patch("gac.providers.copilot.get_api_endpoint", return_value="https://ghe.company.com"):
                provider = _make_provider()
                url = provider._get_api_url("gpt-4.1")
                assert url == "https://ghe.company.com/chat/completions"
