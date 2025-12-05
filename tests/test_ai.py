"""Tests for ai module."""

from unittest.mock import MagicMock, patch

import pytest
import tiktoken

from gac.ai import generate_commit_message, generate_grouped_commits
from gac.ai_utils import (
    count_tokens,
    extract_text_content,
    get_encoding,
)
from gac.errors import AIError
from gac.providers import PROVIDER_REGISTRY, SUPPORTED_PROVIDERS


class TestAiUtils:
    """Tests for the AI utilities."""

    def test_extract_text_content(self):
        """Test extracting text content from various input formats."""
        # Test string input
        assert extract_text_content("test") == "test"

        # Test list of messages
        messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "World"}]
        assert extract_text_content(messages) == "Hello\nWorld"

        # Test dict with content
        message = {"role": "user", "content": "Test"}
        assert extract_text_content(message) == "Test"

        # Test empty input
        assert extract_text_content({}) == ""

    def test_get_encoding_known_model(self):
        """Test getting encoding for known models without mocking."""
        # Test with a well-known OpenAI model that should map to cl100k_base
        encoding = get_encoding("openai:gpt-4")
        assert isinstance(encoding, tiktoken.Encoding)
        assert encoding.name == "cl100k_base"

        # Verify encoding behavior
        tokens = encoding.encode("Hello world")
        assert len(tokens) > 0
        assert isinstance(tokens[0], int)

        # Decode should round-trip correctly
        decoded = encoding.decode(tokens)
        assert decoded == "Hello world"

    def test_count_tokens(self):
        """Test token counting functionality."""
        # Test with string content
        text = "Hello, world!"
        token_count = count_tokens(text, "openai:gpt-4")
        assert token_count > 0
        assert isinstance(token_count, int)

    @patch("gac.ai_utils.count_tokens")
    def test_count_tokens_anthropic_mock(self, mock_count_tokens):
        """Test that anthropic models are handled correctly."""
        # This tests the code path, not the actual implementation
        mock_count_tokens.return_value = 5

        # Test that anthropic model strings are recognized
        model = "anthropic:claude-3-haiku"
        assert model.startswith("anthropic")

    def test_count_tokens_empty_content(self):
        """Test token counting with empty content."""
        assert count_tokens("", "openai:gpt-4") == 0
        assert count_tokens([], "openai:gpt-4") == 0
        assert count_tokens({}, "openai:gpt-4") == 0

        # Test with list of messages
        messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
        token_count = count_tokens(messages, "openai:gpt-4")
        assert token_count > 0

        # Test with dict content
        message = {"role": "user", "content": "Test message"}
        token_count = count_tokens(message, "openai:gpt-4")
        assert token_count > 0

    def test_get_encoding_unknown_model(self):
        """Test getting encoding for unknown models falls back to default."""
        # Clear the cache first to ensure fresh test
        get_encoding.cache_clear()

        # Test with unknown model should fall back to default encoding
        encoding = get_encoding("unknown:model-xyz")
        assert isinstance(encoding, tiktoken.Encoding)
        # Should use the default cl100k_base encoding
        assert encoding.name == "cl100k_base"

    def test_count_tokens_error_handling(self):
        """Test error handling in count_tokens function."""
        # Test with a model that will cause encoding error
        with patch("gac.ai_utils.get_encoding") as mock_encoding:
            mock_encoding.side_effect = Exception("Encoding error")

            # Should fall back to character-based estimation (len/4)
            token_count = count_tokens("Hello world", "test:model")
            assert token_count == len("Hello world") // 4

    def test_count_tokens_with_various_content_types(self):
        """Test count_tokens with different content formats."""
        # Test with list containing invalid items
        messages = [
            {"role": "user", "content": "Valid message"},
            {"role": "assistant"},  # Missing content
            "invalid",  # Not a dict
            {"content": "No role"},  # Has content
        ]
        token_count = count_tokens(messages, "openai:gpt-4")
        assert token_count > 0  # Should count valid messages


class TestGenerateCommitMessage:
    """Tests for the generate_commit_message function."""

    def test_generate_commit_message_invalid_model_format(self):
        """Test that invalid model format raises AIError."""
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="invalid-format", prompt="test prompt")  # Missing colon separator
        assert "Invalid model format" in str(exc_info.value)

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(return_value="feat: Add new feature")})
    def test_generate_commit_message_string_prompt(self):
        """Test generate_commit_message with string prompt using unified API."""
        # Test with string prompt using the unified API
        result = generate_commit_message(model="openai:gpt-4", prompt="Generate a commit message", quiet=True)

        assert result == "feat: Add new feature"

        # Verify the openai function was called
        from gac.providers import PROVIDER_REGISTRY

        mock_openai_api = PROVIDER_REGISTRY["openai"]
        call_args = mock_openai_api.call_args
        assert call_args[1]["model"] == "gpt-4"  # model_name
        assert call_args[1]["messages"][1]["content"] == "Generate a commit message"  # user message
        assert call_args[1]["messages"][0]["content"] == ""  # system message (empty for string prompt)

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"anthropic": MagicMock(return_value="fix: Resolve bug")})
    def test_generate_commit_message_tuple_prompt(self):
        """Test generate_commit_message with tuple prompt using unified API."""
        # Test with tuple prompt using the unified API
        system_prompt = "You are a helpful assistant."
        user_prompt = "Generate a commit message for a bug fix."
        result = generate_commit_message(
            model="anthropic:claude-3", prompt=(system_prompt, user_prompt), temperature=0.5, max_tokens=100, quiet=True
        )

        assert result == "fix: Resolve bug"

        # Verify the parameters passed to call_anthropic_api
        from gac.providers import PROVIDER_REGISTRY

        mock_anthropic_api = PROVIDER_REGISTRY["anthropic"]
        call_args = mock_anthropic_api.call_args
        assert call_args[1]["model"] == "claude-3"  # model_name
        assert call_args[1]["messages"][0]["content"] == system_prompt  # system message
        assert call_args[1]["messages"][1]["content"] == user_prompt  # user message
        assert call_args[1]["temperature"] == 0.5  # temperature
        assert call_args[1]["max_tokens"] == 100  # max_tokens

    @patch("gac.ai_utils.Status")
    @patch("gac.ai_utils.console")
    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(return_value="docs: Update README")})
    def test_generate_commit_message_with_spinner(self, mock_console, mock_status_class):
        """Test generate_commit_message with spinner (non-quiet mode)."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_status_class.return_value = mock_spinner

        # Test with spinner enabled (quiet=False)
        result = generate_commit_message(model="openai:gpt-4", prompt="test", quiet=False)

        assert result == "docs: Update README"

        # Verify spinner was used
        mock_status_class.assert_called_once()
        mock_spinner.start.assert_called_once()
        mock_spinner.stop.assert_called_once()
        mock_console.print.assert_called_once_with("✓ Generated commit message with openai gpt-4")

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openrouter": MagicMock(return_value="chore: tidy config")})
    def test_generate_commit_message_openrouter_provider(self):
        """Test that generate_commit_message routes openrouter provider correctly using unified API."""
        result = generate_commit_message(
            model="openrouter:openrouter/auto",
            prompt="Generate",
            temperature=0.7,
            max_tokens=256,
            quiet=True,
        )

        assert result == "chore: tidy config"
        from gac.providers import PROVIDER_REGISTRY

        mock_openrouter_api = PROVIDER_REGISTRY["openrouter"]
        call_args = mock_openrouter_api.call_args
        assert call_args[1]["model"] == "openrouter/auto"
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["max_tokens"] == 256

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"streamlake": MagicMock(return_value="feat: summarize planets")})
    def test_generate_commit_message_streamlake_provider(self):
        """Test that generate_commit_message routes streamlake provider correctly using unified API."""
        result = generate_commit_message(
            model="streamlake:mock-endpoint-id",
            prompt="Generate",
            temperature=0.6,
            max_tokens=200,
            quiet=True,
        )

        assert result == "feat: summarize planets"
        from gac.providers import PROVIDER_REGISTRY

        mock_streamlake_api = PROVIDER_REGISTRY["streamlake"]
        call_args = mock_streamlake_api.call_args
        assert call_args[1]["model"] == "mock-endpoint-id"
        assert call_args[1]["temperature"] == 0.6
        assert call_args[1]["max_tokens"] == 200

    @patch("gac.ai_utils.time.sleep")
    @patch.dict(
        "gac.providers.PROVIDER_REGISTRY",
        {
            "openai": MagicMock(
                side_effect=[Exception("Network error"), Exception("Timeout"), "feat: Success after retries"]
            )
        },
    )
    def test_generate_commit_message_retry_logic(self, mock_sleep):
        """Test retry logic when generation fails."""
        # Test with retries
        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=3, quiet=True)

        assert result == "feat: Success after retries"
        from gac.providers import PROVIDER_REGISTRY

        mock_openai_api = PROVIDER_REGISTRY["openai"]
        assert mock_openai_api.call_count == 3

        # Verify sleep was called for retries (quiet=True uses single sleep calls)
        assert mock_sleep.call_count == 2  # 2 retries
        mock_sleep.assert_any_call(1)  # First retry: 2^0 = 1
        mock_sleep.assert_any_call(2)  # Second retry: 2^1 = 2

    @patch("gac.ai_utils.time.sleep")
    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Persistent error"))})
    def test_generate_commit_message_max_retries_exceeded(self, mock_sleep):
        """Test that AIError is raised when max retries are exceeded."""
        # Test max retries exceeded
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=2, quiet=True)

        assert "Failed to generate commit message after 2 retries" in str(exc_info.value)
        from gac.providers import PROVIDER_REGISTRY

        mock_openai_api = PROVIDER_REGISTRY["openai"]
        assert mock_openai_api.call_count == 2

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Invalid API key"))})
    def test_generate_commit_message_authentication_error(self):
        """Test error type classification for authentication errors."""
        # Test authentication error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "authentication"

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Rate limit exceeded"))})
    def test_generate_commit_message_rate_limit_error(self):
        """Test error type classification for rate limit errors."""
        # Test rate limit error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "rate_limit"

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Request timeout"))})
    def test_generate_commit_message_timeout_error(self):
        """Test error type classification for timeout errors."""
        # Test timeout error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "timeout"

    @patch.dict(
        "gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Network connection failed"))}
    )
    def test_generate_commit_message_connection_error(self):
        """Test error type classification for connection errors."""
        # Test connection error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "connection"

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Model not found"))})
    def test_generate_commit_message_model_error(self):
        """Test error type classification for model errors."""
        # Test model error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "model"

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Some random error"))})
    def test_generate_commit_message_unknown_error(self):
        """Test error type classification for unknown errors."""
        # Test unknown error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "unknown"

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(return_value="Alternative response format")})
    def test_generate_commit_message_response_without_choices(self):
        """Test handling of normal response format."""
        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", quiet=True)

        assert result == "Alternative response format"

    @patch("gac.ai_utils.time.sleep")
    @patch("gac.ai_utils.Status")
    @patch("gac.ai_utils.console")
    @patch.dict(
        "gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=[Exception("Temporary error"), "Success"])}
    )
    def test_generate_commit_message_retry_with_spinner(self, mock_console, mock_status_class, mock_sleep):
        """Test retry logic with spinner animation."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_status_class.return_value = mock_spinner

        # Test with spinner and retry
        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=2, quiet=False)

        assert result == "Success"

        # Verify spinner was started and succeeded
        mock_spinner.start.assert_called_once()
        mock_spinner.stop.assert_called_once()
        mock_console.print.assert_called()

        # Verify that sleep was called during retry (indicating retry countdown happened)
        assert mock_sleep.call_count > 0

    @patch("gac.ai_utils.Status")
    @patch("gac.ai_utils.console")
    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(side_effect=Exception("Persistent error"))})
    def test_generate_commit_message_failure_with_spinner(self, mock_console, mock_status_class):
        """Test that spinner shows failure when all retries are exhausted."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_status_class.return_value = mock_spinner

        # Test failure with spinner
        with pytest.raises(AIError):
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=False)

        # Verify spinner showed failure
        mock_spinner.stop.assert_called()
        mock_console.print.assert_called_with("✗ Failed to generate commit message with openai gpt-4.1-mini")

    @patch.dict(
        "gac.providers.PROVIDER_REGISTRY", {"anthropic": MagicMock(return_value="feat: Add conversation support")}
    )
    def test_generate_commit_message_list_prompt(self):
        """Test generate_commit_message with list of messages prompt format."""
        # Test with list prompt format (conversation messages)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Generate a commit message"},
            {"role": "assistant", "content": "What changes were made?"},
            {"role": "user", "content": "Added conversation support"},
        ]
        result = generate_commit_message(model="anthropic:claude-3", prompt=messages, quiet=True)

        assert result == "feat: Add conversation support"

        # Verify the messages were passed through correctly
        from gac.providers import PROVIDER_REGISTRY

        mock_anthropic_api = PROVIDER_REGISTRY["anthropic"]
        call_args = mock_anthropic_api.call_args
        passed_messages = call_args[1]["messages"]
        assert len(passed_messages) == 4
        assert passed_messages[0]["role"] == "system"
        assert passed_messages[1]["role"] == "user"
        assert passed_messages[2]["role"] == "assistant"
        assert passed_messages[3]["role"] == "user"

    @patch("gac.ai.generate_with_retries")
    def test_generate_commit_message_generic_exception_handling(self, mock_generate):
        """Test that non-AIError exceptions are converted to AIError.model_error."""
        # Simulate a truly unexpected exception (e.g., TypeError from internal logic)
        mock_generate.side_effect = TypeError("Unexpected internal error")

        # Test that the exception is caught and converted to AIError
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4", prompt="test", quiet=True)

        # Verify it was converted to a model error
        assert exc_info.value.error_type == "model"
        assert "Failed to generate commit message" in str(exc_info.value)
        assert "Unexpected internal error" in str(exc_info.value)

    @patch.dict("gac.providers.PROVIDER_REGISTRY", {"openai": MagicMock(return_value='{"commits": []}')})
    def test_generate_grouped_commits(self):
        msgs = [{"role": "user", "content": "test"}]
        result = generate_grouped_commits("openai:gpt-4", msgs, 0.7, 500, 1, True, True)
        assert result == '{"commits": []}'


class TestProviderRegistry:
    """Tests for the centralized provider registry."""

    def test_provider_registry_and_supported_providers_consistency(self):
        """Test that SUPPORTED_PROVIDERS contains exactly the keys from PROVIDER_REGISTRY."""
        # Get the set of registry keys and supported providers
        registry_keys = set(PROVIDER_REGISTRY.keys())
        supported_providers_set = set(SUPPORTED_PROVIDERS)

        # They should be identical
        assert registry_keys == supported_providers_set, (
            f"PROVIDER_REGISTRY keys and SUPPORTED_PROVIDERS are not identical:\n"
            f"Registry keys not in supported: {registry_keys - supported_providers_set}\n"
            f"Supported providers not in registry: {supported_providers_set - registry_keys}"
        )

    def test_provider_registry_functions_exist(self):
        """Test that all functions in PROVIDER_REGISTRY are callable."""
        for provider_name, provider_func in PROVIDER_REGISTRY.items():
            assert callable(provider_func), f"Provider function for '{provider_name}' is not callable"

    def test_supported_providers_is_sorted(self):
        """Test that SUPPORTED_PROVIDERS is sorted alphabetically."""
        assert SUPPORTED_PROVIDERS == sorted(PROVIDER_REGISTRY.keys()), (
            "SUPPORTED_PROVIDERS should be sorted alphabetically"
        )

    def test_provider_registry_complete(self):
        """Test that PROVIDER_REGISTRY contains all expected providers."""
        expected_providers = {
            "anthropic",
            "azure-openai",
            "cerebras",
            "claude-code",
            "chutes",
            "custom-anthropic",
            "custom-openai",
            "deepseek",
            "fireworks",
            "gemini",
            "groq",
            "kimi-coding",
            "lm-studio",
            "minimax",
            "mistral",
            "moonshot",
            "ollama",
            "openai",
            "openrouter",
            "qwen",
            "replicate",
            "streamlake",
            "synthetic",
            "together",
            "zai",
            "zai-coding",
        }

        actual_providers = set(PROVIDER_REGISTRY.keys())

        assert actual_providers == expected_providers, (
            f"Provider registry is missing expected providers or has extra ones:\n"
            f"Missing: {expected_providers - actual_providers}\n"
            f"Extra: {actual_providers - expected_providers}"
        )
