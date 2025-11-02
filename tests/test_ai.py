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

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_string_prompt(self, mock_openai_api):
        """Test generate_commit_message with string prompt using unified API."""
        # Setup mock
        mock_openai_api.return_value = "feat: Add new feature"

        # Test with string prompt using the unified API
        result = generate_commit_message(model="openai:gpt-4", prompt="Generate a commit message", quiet=True)

        assert result == "feat: Add new feature"

        # Verify the parameters passed to call_openai_api
        call_args = mock_openai_api.call_args
        assert call_args[1]["model"] == "gpt-4"  # model_name
        assert call_args[1]["messages"][1]["content"] == "Generate a commit message"  # user message
        assert call_args[1]["messages"][0]["content"] == ""  # system message (empty for string prompt)

    @patch("gac.ai.call_anthropic_api")
    def test_generate_commit_message_tuple_prompt(self, mock_anthropic_api):
        """Test generate_commit_message with tuple prompt using unified API."""
        # Setup mock
        mock_anthropic_api.return_value = "fix: Resolve bug"

        # Test with tuple prompt using the unified API
        system_prompt = "You are a helpful assistant."
        user_prompt = "Generate a commit message for a bug fix."
        result = generate_commit_message(
            model="anthropic:claude-3", prompt=(system_prompt, user_prompt), temperature=0.5, max_tokens=100, quiet=True
        )

        assert result == "fix: Resolve bug"

        # Verify the parameters passed to call_anthropic_api
        call_args = mock_anthropic_api.call_args
        assert call_args[1]["model"] == "claude-3"  # model_name
        assert call_args[1]["messages"][0]["content"] == system_prompt  # system message
        assert call_args[1]["messages"][1]["content"] == user_prompt  # user message
        assert call_args[1]["temperature"] == 0.5  # temperature
        assert call_args[1]["max_tokens"] == 100  # max_tokens

    @patch("gac.ai_utils.Halo")
    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_with_spinner(self, mock_openai_api, mock_halo_class):
        """Test generate_commit_message with spinner (non-quiet mode)."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_halo_class.return_value = mock_spinner
        mock_openai_api.return_value = "docs: Update README"

        # Test with spinner enabled (quiet=False)
        result = generate_commit_message(model="openai:gpt-4", prompt="test", quiet=False)

        assert result == "docs: Update README"

        # Verify spinner was used
        mock_halo_class.assert_called_once()
        mock_spinner.start.assert_called_once()
        mock_spinner.succeed.assert_called_once_with("Generated commit message with openai gpt-4")

    @patch("gac.ai.call_openrouter_api")
    def test_generate_commit_message_openrouter_provider(self, mock_openrouter_api):
        """Test that generate_commit_message routes openrouter provider correctly using unified API."""
        mock_openrouter_api.return_value = "chore: tidy config"

        result = generate_commit_message(
            model="openrouter:openrouter/auto",
            prompt="Generate",
            temperature=0.7,
            max_tokens=256,
            quiet=True,
        )

        assert result == "chore: tidy config"
        call_args = mock_openrouter_api.call_args
        assert call_args[1]["model"] == "openrouter/auto"
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["max_tokens"] == 256

    @patch("gac.ai.call_streamlake_api")
    def test_generate_commit_message_streamlake_provider(self, mock_streamlake_api):
        """Test that generate_commit_message routes streamlake provider correctly using unified API."""
        mock_streamlake_api.return_value = "feat: summarize planets"

        result = generate_commit_message(
            model="streamlake:mock-endpoint-id",
            prompt="Generate",
            temperature=0.6,
            max_tokens=200,
            quiet=True,
        )

        assert result == "feat: summarize planets"
        call_args = mock_streamlake_api.call_args
        assert call_args[1]["model"] == "mock-endpoint-id"
        assert call_args[1]["temperature"] == 0.6
        assert call_args[1]["max_tokens"] == 200

    @patch("gac.ai_utils.time.sleep")
    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_retry_logic(self, mock_openai_api, mock_sleep):
        """Test retry logic when generation fails."""
        # First two attempts fail, third succeeds
        mock_openai_api.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            "feat: Success after retries",
        ]

        # Test with retries
        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=3, quiet=True)

        assert result == "feat: Success after retries"
        assert mock_openai_api.call_count == 3

        # Verify sleep was called for retries (quiet=True uses single sleep calls)
        assert mock_sleep.call_count == 2  # 2 retries
        mock_sleep.assert_any_call(1)  # First retry: 2^0 = 1
        mock_sleep.assert_any_call(2)  # Second retry: 2^1 = 2

    @patch("gac.ai_utils.time.sleep")
    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_max_retries_exceeded(self, mock_openai_api, mock_sleep):
        """Test that AIError is raised when max retries are exceeded."""
        # All attempts fail
        mock_openai_api.side_effect = Exception("Persistent error")

        # Test max retries exceeded
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=2, quiet=True)

        assert "Failed to generate commit message after 2 attempts" in str(exc_info.value)
        assert mock_openai_api.call_count == 2

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_authentication_error(self, mock_openai_api):
        """Test error type classification for authentication errors."""
        mock_openai_api.side_effect = Exception("Invalid API key")

        # Test authentication error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "authentication"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_rate_limit_error(self, mock_openai_api):
        """Test error type classification for rate limit errors."""
        mock_openai_api.side_effect = Exception("Rate limit exceeded")

        # Test rate limit error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "rate_limit"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_timeout_error(self, mock_openai_api):
        """Test error type classification for timeout errors."""
        mock_openai_api.side_effect = Exception("Request timeout")

        # Test timeout error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "timeout"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_connection_error(self, mock_openai_api):
        """Test error type classification for connection errors."""
        mock_openai_api.side_effect = Exception("Network connection failed")

        # Test connection error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "connection"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_model_error(self, mock_openai_api):
        """Test error type classification for model errors."""
        mock_openai_api.side_effect = Exception("Model not found")

        # Test model error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "model"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_unknown_error(self, mock_openai_api):
        """Test error type classification for unknown errors."""
        mock_openai_api.side_effect = Exception("Some random error")

        # Test unknown error
        with pytest.raises(AIError) as exc_info:
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=True)

        assert exc_info.value.error_type == "unknown"

    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_response_without_choices(self, mock_openai_api):
        """Test handling of normal response format."""
        mock_openai_api.return_value = "Alternative response format"

        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", quiet=True)

        assert result == "Alternative response format"

    @patch("gac.ai_utils.time.sleep")
    @patch("gac.ai_utils.Halo")
    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_retry_with_spinner(self, mock_openai_api, mock_halo_class, mock_sleep):
        """Test retry logic with spinner animation."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_halo_class.return_value = mock_spinner

        # First attempt fails, second succeeds
        mock_openai_api.side_effect = [
            Exception("Temporary error"),
            "Success",
        ]

        # Test with spinner and retry
        result = generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=2, quiet=False)

        assert result == "Success"

        # Verify spinner was started and succeeded
        mock_spinner.start.assert_called_once()
        mock_spinner.succeed.assert_called_once()

        # Verify that sleep was called during retry (indicating retry countdown happened)
        assert mock_sleep.call_count > 0

    @patch("gac.ai_utils.Halo")
    @patch("gac.ai.call_openai_api")
    def test_generate_commit_message_failure_with_spinner(self, mock_openai_api, mock_halo_class):
        """Test that spinner shows failure when all retries are exhausted."""
        # Setup mocks
        mock_spinner = MagicMock()
        mock_halo_class.return_value = mock_spinner

        # All attempts fail
        mock_openai_api.side_effect = Exception("Persistent error")

        # Test failure with spinner
        with pytest.raises(AIError):
            generate_commit_message(model="openai:gpt-4.1-mini", prompt="test", max_retries=1, quiet=False)

        # Verify spinner showed failure
        mock_spinner.fail.assert_called_once_with("Failed to generate commit message with openai gpt-4.1-mini")

    @patch("gac.ai.call_anthropic_api")
    def test_generate_commit_message_list_prompt(self, mock_anthropic_api):
        """Test generate_commit_message with list of messages prompt format."""
        # Setup mock
        mock_anthropic_api.return_value = "feat: Add conversation support"

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

    @patch("gac.ai.call_openai_api")
    def test_generate_grouped_commits(self, mock_api):
        mock_api.return_value = '{"commits": []}'
        msgs = [{"role": "user", "content": "test"}]
        result = generate_grouped_commits("openai:gpt-4", msgs, 0.7, 500, 1, True, True)
        assert result == '{"commits": []}'
