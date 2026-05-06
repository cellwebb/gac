"""Tests for base provider classes."""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gac.constants import ProviderDefaults
from gac.errors import AIError
from gac.providers.base import (
    AnthropicCompatibleProvider,
    BaseConfiguredProvider,
    GenericHTTPProvider,
    OpenAICompatibleProvider,
    ProviderConfig,
)
from gac.providers.error_handler import (
    MAX_ERROR_RESPONSE_LENGTH,
    sanitize_error_response,
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

            assert isinstance(result, tuple)
            assert result[0] == "test content"
            assert isinstance(result[3], int) and result[3] >= 0
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

    def test_generate_returns_duration_ms(self):
        """Test that generate returns a non-negative integer duration_ms."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.return_value.json.return_value = {"choices": [{"message": {"content": "hello"}}]}
            mock_post.return_value.raise_for_status = MagicMock()

            result = provider.generate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=100,
            )

            content, prompt_tokens, completion_tokens, duration_ms, reasoning_tokens = result
            assert isinstance(duration_ms, int)
            assert duration_ms >= 0
            assert isinstance(reasoning_tokens, int)
            assert reasoning_tokens >= 0

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

    def test_anthropic_thinking_blocks_estimate_tokens(self):
        """Thinking blocks in Anthropic response estimate reasoning tokens."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        # Response with a thinking block (like Claude Code extended thinking)
        response = {
            "content": [
                {"type": "thinking", "thinking": "Let me reason about this commit message carefully..." * 10},
                {"type": "text", "text": "Here is the commit message"},
            ],
            "usage": {"input_tokens": 100, "output_tokens": 200},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "Here is the commit message"
        assert parsed.reasoning_tokens > 0  # Estimated from thinking text
        assert parsed.prompt_tokens == 100
        # output_tokens (200) minus reasoning_tokens should be completion_tokens
        assert parsed.completion_tokens == 200 - parsed.reasoning_tokens

    def test_anthropic_no_thinking_blocks_no_estimate(self):
        """No thinking blocks → reasoning_tokens stays 0."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        response = {
            "content": [{"text": "just a normal response"}],
            "usage": {"input_tokens": 50, "output_tokens": 30},
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens == 0
        assert parsed.completion_tokens == 30

    def test_anthropic_empty_thinking_no_estimate(self):
        """Empty thinking block text → reasoning_tokens stays 0."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        response = {
            "content": [
                {"type": "thinking", "thinking": ""},
                {"type": "text", "text": "actual content"},
            ],
            "usage": {"input_tokens": 50, "output_tokens": 30},
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens == 0

    def test_anthropic_only_thinking_no_text_block_raises(self):
        """Response with only thinking blocks (no text block) raises AIError."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        response = {
            "content": [{"type": "thinking", "thinking": "deep thoughts"}],
            "usage": {"input_tokens": 50, "output_tokens": 30},
        }
        with pytest.raises(AIError, match="missing text block"):
            provider._parse_response(response)

    def test_anthropic_multiple_thinking_blocks(self):
        """Multiple thinking blocks are joined for token estimation."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        # Two thinking blocks of 17 chars each → 34 total → 10 tokens
        response = {
            "content": [
                {"type": "thinking", "thinking": "A" * 17},
                {"type": "thinking", "thinking": "B" * 17},
                {"type": "text", "text": "The answer"},
            ],
            "usage": {"input_tokens": 100, "output_tokens": 50},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "The answer"
        # 17 + 1 (newline) + 17 = 35 chars → round(35/3.4) = 10
        assert parsed.reasoning_tokens == 10
        assert parsed.completion_tokens == 40  # 50 - 10

    def test_anthropic_prefers_type_text_block(self):
        """When multiple blocks have .text, prefer type='text' over others."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        response = {
            "content": [
                {"type": "metadata", "text": "meta-value"},
                {"type": "text", "text": "actual response"},
            ],
            "usage": {"input_tokens": 50, "output_tokens": 20},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "actual response"

    def test_anthropic_non_dict_block_in_content(self):
        """Non-dict items in content array are safely skipped."""
        provider = SimpleAnthropicProvider(SimpleAnthropicProvider.config)
        response = {
            "content": [
                "unexpected string",
                {"type": "text", "text": "safe content"},
            ],
            "usage": {"input_tokens": 50, "output_tokens": 20},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "safe content"

    def test_openai_think_tags_estimate_tokens(self):
        """OpenAI-compatible response with think tags estimates reasoning tokens."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        thinking = "Let me analyze the diff" * 10  # ~230 chars
        think_content = "<think>" + thinking + "</think>"
        response = {
            "choices": [{"message": {"content": think_content + "\nfeat: add feature"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 200},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == think_content + "\nfeat: add feature"
        assert parsed.reasoning_tokens > 0  # Estimated from think tags
        # completion_tokens should be 200 minus estimated reasoning
        assert parsed.completion_tokens < 200

    def test_openai_explicit_reasoning_tokens_win_over_think_tags(self):
        """When API reports reasoning_tokens explicitly, it wins over think-tag estimation."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        thinking = "Let me analyze the diff" * 10  # ~230 chars -> ~68 estimated
        think_content = "<think>" + thinking + "</think>"
        response = {
            "choices": [{"message": {"content": think_content + "\nfeat: add feature"}}],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "completion_tokens_details": {"reasoning_tokens": 42},
            },
        }
        parsed = provider._parse_response(response)
        # Explicit 42 wins, not the ~68 estimate from think tags
        assert parsed.reasoning_tokens == 42
        # completion_tokens = 200 - 42 = 158
        assert parsed.completion_tokens == 158

    def test_openai_reasoning_content_field_estimates_tokens(self):
        """DeepSeek-style reasoning_content field should populate reasoning tokens."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        reasoning_text = "Let me think about this carefully" * 10  # ~340 chars
        response = {
            "choices": [
                {
                    "message": {
                        "content": "feat: add feature",
                        "reasoning_content": reasoning_text,
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 200},
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "feat: add feature"
        assert parsed.reasoning_tokens > 0
        assert parsed.completion_tokens < 200

    def test_openai_reasoning_content_overrides_zero_from_api(self):
        """When API reports reasoning_tokens=0 but reasoning_content is non-empty
        (e.g. Wafer.ai's deepseek-v4-pro), estimate from the text instead of
        trusting the false zero."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        reasoning_text = "Step by step reasoning here" * 20  # ~540 chars
        response = {
            "choices": [
                {
                    "message": {
                        "content": "OK",
                        "reasoning_content": reasoning_text,
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens > 0
        assert parsed.completion_tokens < 200

    def test_openai_reasoning_field_openrouter_style(self):
        """OpenRouter-style `reasoning` field should also populate reasoning tokens."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        reasoning_text = "Reasoning text from OpenRouter" * 10  # ~310 chars
        response = {
            "choices": [
                {
                    "message": {
                        "content": "feat: add feature",
                        "reasoning": reasoning_text,
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 150},
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens > 0
        assert parsed.completion_tokens < 150

    def test_openai_null_reasoning_content_no_change(self):
        """Null reasoning_content should not affect existing zero-reasoning behavior."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        response = {
            "choices": [
                {
                    "message": {
                        "content": "feat: add feature",
                        "reasoning_content": None,
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }
        parsed = provider._parse_response(response)
        assert parsed.reasoning_tokens == 0
        assert parsed.completion_tokens == 50

    def test_openai_explicit_nonzero_reasoning_wins_over_content_field(self):
        """When API reports nonzero reasoning_tokens, trust it over reasoning_content estimate."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)
        reasoning_text = "Long reasoning content" * 50  # would estimate high
        response = {
            "choices": [
                {
                    "message": {
                        "content": "feat: add feature",
                        "reasoning_content": reasoning_text,
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "completion_tokens_details": {"reasoning_tokens": 25},
            },
        }
        parsed = provider._parse_response(response)
        # Trust the explicit nonzero count, not the estimate
        assert parsed.reasoning_tokens == 25
        assert parsed.completion_tokens == 175

    def test_generic_http_crash_proof_non_dict_choices(self):
        """GenericHTTPProvider should not crash on non-dict entries in choices."""
        from gac.providers.base import GenericHTTPProvider, ProviderConfig

        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "choices": ["not a dict"],
            "content": [{"text": "fallback text"}],
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "fallback text"

    def test_generic_http_crash_proof_non_dict_content(self):
        """GenericHTTPProvider should not crash on non-dict entries in content."""
        from gac.providers.base import GenericHTTPProvider, ProviderConfig

        provider = GenericHTTPProvider(ProviderConfig(name="Gen", api_key_env="KEY", base_url="http://test.url"))
        response = {
            "choices": [{"message": {"content": ""}}],
            "content": [42, {"text": "second entry"}],
        }
        parsed = provider._parse_response(response)
        assert parsed.content == "second entry"


class TestErrorPropagation:
    """Test that exceptions propagate from base providers to decorator.

    Error handling is centralized in the @handle_provider_errors decorator.
    Base provider classes should let httpx exceptions propagate up so the
    decorator can convert them to appropriate AIError types.
    """

    def test_http_error_propagates(self):
        """Test that HTTP errors propagate from base provider."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.side_effect = httpx.HTTPStatusError("500 error", request=MagicMock(), response=mock_response)

            with pytest.raises(httpx.HTTPStatusError):
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

    def test_timeout_error_propagates(self):
        """Test that timeout errors propagate from base provider."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(httpx.TimeoutException):
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )

    def test_connection_error_propagates(self):
        """Test that connection errors propagate from base provider."""
        provider = SimpleOpenAIProvider(SimpleOpenAIProvider.config)

        with (
            patch("gac.providers.base.httpx.post") as mock_post,
            patch.dict(os.environ, {"SIMPLE_API_KEY": "test-key"}),
        ):
            mock_post.side_effect = httpx.RequestError("Connection failed")

            with pytest.raises(httpx.RequestError):
                provider.generate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    temperature=0.7,
                    max_tokens=100,
                )


class TestSanitizeErrorResponse:
    """Test error response sanitization."""

    def test_empty_input(self):
        """Test that empty input returns empty string."""
        assert sanitize_error_response("") == ""

    def test_short_input_no_secrets(self):
        """Test that short input without secrets passes through."""
        text = "Error: Invalid request"
        result = sanitize_error_response(text)
        assert result == text

    def test_truncates_long_input(self):
        """Test that long input is truncated to max length."""
        long_text = "Error message. " * 50
        result = sanitize_error_response(long_text)
        assert len(result) == MAX_ERROR_RESPONSE_LENGTH + 3
        assert result.endswith("...")

    def test_redacts_openai_api_key(self):
        """Test that OpenAI API keys are redacted."""
        text = "Invalid API key: sk-abcdefghijklmnopqrstuvwxyz1234567890abcd"
        result = sanitize_error_response(text)
        assert "sk-abcdefghijklmnopqrstuvwxyz1234567890abcd" not in result
        assert "[REDACTED]" in result

    def test_redacts_anthropic_api_key(self):
        """Test that Anthropic API keys are redacted."""
        text = "Invalid key: sk-ant-abcdefghijklmnopqrstuvwxyz"
        result = sanitize_error_response(text)
        assert "sk-ant-" not in result
        assert "[REDACTED]" in result

    def test_redacts_github_token(self):
        """Test that GitHub tokens are redacted."""
        text = "Token: ghp_abcdefghijklmnopqrstuvwxyz123456"
        result = sanitize_error_response(text)
        assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in result
        assert "[REDACTED]" in result

    def test_redacts_jwt_token(self):
        """Test that JWT tokens are redacted."""
        text = "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = sanitize_error_response(text)
        assert "eyJ" not in result
        assert "[REDACTED]" in result

    def test_redacts_bearer_token(self):
        """Test that Bearer tokens are redacted."""
        text = "Authorization: Bearer abcdefghijklmnopqrstuvwxyz1234567890"
        result = sanitize_error_response(text)
        assert "Bearer abcdefghijklmnopqrstuvwxyz1234567890" not in result
        assert "[REDACTED]" in result

    def test_redacts_google_api_key(self):
        """Test that Google API keys are redacted."""
        text = "Key: AIzaSyAbcdefghijklmnopqrstuvwxyz12345"
        result = sanitize_error_response(text)
        assert "AIzaSy" not in result
        assert "[REDACTED]" in result

    def test_redacts_stripe_key(self):
        """Test that Stripe keys are redacted."""
        text = "Key: sk_live_abcdefghijklmnopqrstuvwxyz123456"
        result = sanitize_error_response(text)
        assert "sk_live_" not in result
        assert "[REDACTED]" in result

    def test_redacts_slack_token(self):
        """Test that Slack tokens are redacted."""
        text = "Token: xoxb-abcdefghijklmnopqrstuvwxyz"
        result = sanitize_error_response(text)
        assert "xoxb-" not in result
        assert "[REDACTED]" in result

    def test_redacts_multiple_secrets(self):
        """Test that multiple secrets in same text are redacted."""
        text = "Keys: sk-abc1234567890123456789012 and ghp_xyz1234567890123456789012345"
        result = sanitize_error_response(text)
        assert "sk-abc" not in result
        assert "ghp_xyz" not in result
        assert result.count("[REDACTED]") >= 2

    def test_redacts_long_alphanumeric_tokens(self):
        """Test that generic long alphanumeric tokens are redacted."""
        text = "Token: abcdefghijklmnopqrstuvwxyz123456789012"
        result = sanitize_error_response(text)
        assert "abcdefghijklmnopqrstuvwxyz123456789012" not in result
        assert "[REDACTED]" in result

    def test_preserves_short_alphanumeric(self):
        """Test that short alphanumeric strings are preserved."""
        text = "Error code: ABC123"
        result = sanitize_error_response(text)
        assert result == text

    def test_truncation_after_redaction(self):
        """Test that truncation happens after redaction."""
        long_key = "sk-" + "a" * 50
        long_text = f"Error with key {long_key} followed by " + "x" * 200
        result = sanitize_error_response(long_text)
        assert "[REDACTED]" in result
        assert len(result) <= MAX_ERROR_RESPONSE_LENGTH + 3


class TestBaseConfiguredProviderProperties:
    """Test BaseConfiguredProvider property accessors directly."""

    def test_name_property(self):
        config = ProviderConfig(name="TestName", api_key_env="TEST_KEY", base_url="http://test.url", timeout=45)

        class ConcreteProvider(BaseConfiguredProvider):
            def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
                return {}

            def _parse_response(self, response):
                return ""

            def generate(self, model, messages, temperature=0.7, max_tokens=1024, **kwargs):
                return ""

        provider = ConcreteProvider(config)
        assert provider.name == "TestName"

    def test_api_key_env_property(self):
        config = ProviderConfig(name="Test", api_key_env="MY_API_KEY", base_url="http://test.url")

        class ConcreteProvider(BaseConfiguredProvider):
            def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
                return {}

            def _parse_response(self, response):
                return ""

            def generate(self, model, messages, temperature=0.7, max_tokens=1024, **kwargs):
                return ""

        provider = ConcreteProvider(config)
        assert provider.api_key_env == "MY_API_KEY"

    def test_base_url_property(self):
        config = ProviderConfig(name="Test", api_key_env="KEY", base_url="http://custom.url/v1")

        class ConcreteProvider(BaseConfiguredProvider):
            def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
                return {}

            def _parse_response(self, response):
                return ""

            def generate(self, model, messages, temperature=0.7, max_tokens=1024, **kwargs):
                return ""

        provider = ConcreteProvider(config)
        assert provider.base_url == "http://custom.url/v1"

    def test_timeout_property(self):
        config = ProviderConfig(name="Test", api_key_env="KEY", base_url="http://test.url", timeout=99)

        class ConcreteProvider(BaseConfiguredProvider):
            def _build_request_body(self, messages, temperature, max_tokens, model, **kwargs):
                return {}

            def _parse_response(self, response):
                return ""

            def generate(self, model, messages, temperature=0.7, max_tokens=1024, **kwargs):
                return ""

        provider = ConcreteProvider(config)
        assert provider.timeout == 99


class TestGenericHTTPProviderParseResponse:
    """Test GenericHTTPProvider._parse_response with different response formats."""

    def _make_provider(self):
        config = ProviderConfig(name="Generic", api_key_env="KEY", base_url="http://test.url")
        return GenericHTTPProvider(config)

    def test_openai_style_response(self):
        provider = self._make_provider()
        response = {"choices": [{"message": {"content": "openai response"}}]}
        assert provider._parse_response(response).content == "openai response"

    def test_anthropic_style_response(self):
        provider = self._make_provider()
        response = {"content": [{"text": "anthropic response"}]}
        assert provider._parse_response(response).content == "anthropic response"

    def test_ollama_style_response(self):
        provider = self._make_provider()
        response = {"message": {"content": "ollama response"}}
        assert provider._parse_response(response).content == "ollama response"

    def test_fallback_long_string_value(self):
        provider = self._make_provider()
        response = {"result": "this is a long response text for fallback detection"}
        assert provider._parse_response(response).content == "this is a long response text for fallback detection"

    def test_no_content_raises_ai_error(self):
        provider = self._make_provider()
        response = {"status": "ok", "id": "123"}
        with pytest.raises(AIError, match="Could not extract content"):
            provider._parse_response(response)

    def test_empty_choices_falls_through(self):
        provider = self._make_provider()
        response = {"choices": [], "message": {"content": "from ollama"}}
        assert provider._parse_response(response).content == "from ollama"

    def test_choices_with_no_content_falls_through(self):
        provider = self._make_provider()
        response = {"choices": [{"message": {}}], "content": [{"text": "from anthropic"}]}
        assert provider._parse_response(response).content == "from anthropic"

    def test_empty_dict_raises_ai_error(self):
        provider = self._make_provider()
        with pytest.raises(AIError, match="Could not extract content"):
            provider._parse_response({})
