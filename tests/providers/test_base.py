"""Tests for base provider classes."""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.providers.base import (
    AnthropicCompatibleProvider,
    OpenAICompatibleProvider,
    ProviderConfig,
)


class SimpleOpenAIProvider(OpenAICompatibleProvider):
    """Simple OpenAI-compatible provider for testing."""

    config = ProviderConfig(
        name="SimpleOpenAI",
        api_key_env="SIMPLE_API_KEY",
        base_url="https://api.simple.com/v1/chat/completions",
    )


class SimpleAnthropicProvider(AnthropicCompatibleProvider):
    """Simple Anthropic-compatible provider for testing."""

    config = ProviderConfig(
        name="SimpleAnthropic",
        api_key_env="SIMPLE_ANTHROPIC_API_KEY",
        base_url="https://api.simple.com/v1/messages",
    )


class TestProviderConfig:
    """Test ProviderConfig dataclass."""

    def test_config_creation(self):
        """Test that ProviderConfig is created with correct values."""
        config = ProviderConfig(name="Test", api_key_env="TEST_KEY", base_url="https://api.test.com")
        assert config.name == "Test"
        assert config.api_key_env == "TEST_KEY"
        assert config.base_url == "https://api.test.com"
        assert config.timeout == ProviderDefaults.HTTP_TIMEOUT

    def test_default_headers(self):
        """Test that default headers are set."""
        config = ProviderConfig(name="Test", api_key_env="TEST_KEY", base_url="https://api.test.com")
        assert config.headers == {"Content-Type": "application/json"}

    def test_custom_headers(self):
        """Test that custom headers are preserved."""
        custom_headers = {"Authorization": "Bearer token"}
        config = ProviderConfig(
            name="Test",
            api_key_env="TEST_KEY",
            base_url="https://api.test.com",
            headers=custom_headers,
        )
        assert config.headers == custom_headers


class TestOpenAICompatibleProvider:
    """Test OpenAI-compatible provider."""

    def test_ssl_verification_enabled(self):
        """Test that SSL verification is enabled by default."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
            patch("gac.providers.base.get_ssl_verify", return_value=True),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "test content"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            result = provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            assert result == "test content"
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["verify"] is True

    def test_ssl_verification_can_be_disabled(self):
        """Test that SSL verification can be disabled."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
            patch("gac.providers.base.get_ssl_verify", return_value=False),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "test content"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["verify"] is False

    def test_timeout_from_config(self):
        """Test that timeout is read from config."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "test content"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["timeout"] == ProviderDefaults.HTTP_TIMEOUT

    def test_custom_timeout(self):
        """Test that custom timeout is respected."""
        config = ProviderConfig(
            name="SimpleOpenAI",
            api_key_env="SIMPLE_API_KEY",
            base_url="https://api.simple.com/v1/chat/completions",
            timeout=60,
        )
        provider = SimpleOpenAIProvider(config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "test content"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["timeout"] == 60

    def test_bearer_token_header(self):
        """Test that OpenAI-style Bearer token is added."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "test content"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"

    def test_missing_api_key(self):
        """Test that missing API key raises authentication error."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AIError) as exc_info:
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

            assert "SIMPLE_API_KEY" in str(exc_info.value)


class TestAnthropicCompatibleProvider:
    """Test Anthropic-compatible provider."""

    def test_anthropic_headers(self):
        """Test that Anthropic-style headers are set."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_ANTHROPIC_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"content": [{"text": "test response"}]}
            mock_post.return_value.raise_for_status = MagicMock()

            provider.generate(
                model="claude-3-sonnet",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["headers"]["x-api-key"] == "test-key"
            assert call_kwargs["headers"]["anthropic-version"] == "2023-06-01"

    def test_system_message_extraction(self):
        """Test that system messages are extracted correctly."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_ANTHROPIC_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"content": [{"text": "test response"}]}
            mock_post.return_value.raise_for_status = MagicMock()

            messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "test"},
            ]

            provider.generate(
                model="claude-3-sonnet",
                messages=messages,
                temperature=0.7,
                max_tokens=100,
            )

            call_kwargs = mock_post.call_args[1]
            body = call_kwargs["json"]
            assert body["system"] == "You are helpful"
            # System message should not be in messages list
            assert all(msg["role"] != "system" for msg in body["messages"])


class TestErrorHandling:
    """Test error handling in providers."""

    def test_http_error_handling(self):
        """Test that HTTP errors are properly converted."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.side_effect = httpx.HTTPStatusError("500 error", request=MagicMock(), response=mock_response)

            with pytest.raises(AIError):
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

    def test_timeout_error_handling(self):
        """Test that timeout errors are properly converted."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(AIError) as exc_info:
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

            assert "timed out" in str(exc_info.value).lower() or "timeout" in str(exc_info.value).lower()

    def test_connection_error_handling(self):
        """Test that connection errors are properly converted."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.side_effect = httpx.RequestError("Connection failed")

            with pytest.raises(AIError) as exc_info:
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

            assert "connection" in str(exc_info.value).lower()
