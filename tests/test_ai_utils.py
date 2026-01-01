"""Unit tests for AI utility functions.

These tests run without any external dependencies and test core logic.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import gac.ai_utils as ai_utils  # noqa: E402
from gac.errors import AIError  # noqa: E402


class TestCountTokens:
    """Test count_tokens function."""

    def test_count_tokens(self):
        """Test character-based token counting functionality."""
        # Test with string content - "Hello, world!" = 13 chars
        # 13 / 3.4 = 3.82, rounded = 4 tokens
        text = "Hello, world!"
        token_count = ai_utils.count_tokens(text, "openai:gpt-4")
        assert token_count == 4  # Should return calculated token count
        assert isinstance(token_count, int)

        # Test different text length
        text = "This is a test message"  # 22 chars
        # 22 / 3.4 = 6.47, rounded = 6 tokens
        token_count = ai_utils.count_tokens(text, "openai:gpt-4")
        assert token_count == 6

        # Test with list format
        messages = [{"role": "user", "content": "Hello"}]  # 5 chars
        # 5 / 3.4 = 1.47, rounded = 1 token
        token_count = ai_utils.count_tokens(messages, "openai:gpt-4")
        assert token_count == 1

        # Test with empty string vs no characters
        assert ai_utils.count_tokens("", "openai:gpt-4") == 0
        assert ai_utils.count_tokens("   ", "openai:gpt-4") == 1  # 3 spaces = 3/3.4 = 0.88, rounded = 1

    def test_count_tokens_empty_content(self):
        """Test token counting with empty content."""
        assert ai_utils.count_tokens("", "openai:gpt-4") == 0
        assert ai_utils.count_tokens([], "openai:gpt-4") == 0
        assert ai_utils.count_tokens({}, "openai:gpt-4") == 0

    def test_all_providers_use_same_character_based_counting(self):
        """Test that all providers use the same character-based counting."""
        text = "Hello, world!"  # 13 chars
        # 13 / 3.4 = 3.82, rounded = 4 tokens
        expected_tokens = round(len(text) / 3.4)

        # Test various providers - all should give the same result
        providers_and_models = [
            "openai:gpt-4",
            "anthropic:claude-3",
            "ollama:llama2",
            "lm-studio:local-model",
            "custom-openai:local-gpt4",
            "custom-anthropic:local-claude",
            "groq:llama3-70b",
            "gemini:gemini-pro",
        ]

        for model in providers_and_models:
            token_count = ai_utils.count_tokens(text, model)
            assert token_count == expected_tokens, (
                f"Provider {model} should give {expected_tokens} tokens, got {token_count}"
            )

    def test_character_based_calculation_examples(self):
        """Test specific examples of character-based token calculation."""
        test_cases = [
            ("Hello", 1),  # 5 chars / 3.4 = 1.47 -> 1 token
            ("Hello world", 3),  # 11 chars / 3.4 = 3.24 -> 3 tokens
            ("This is a test", 4),  # 14 chars / 3.4 = 4.12 -> 4 tokens
            ("", 0),  # Empty string = 0 tokens
            ("a", 1),  # 1 char / 3.4 = 0.29 -> rounded = 0, but we force 1 for non-empty
        ]

        for text, expected_tokens in test_cases:
            token_count = ai_utils.count_tokens(text, "openai:gpt-4")
            assert token_count == expected_tokens, (
                f"Text '{text}' should give {expected_tokens} tokens, got {token_count}"
            )

    def test_character_based_calculation_edge_cases(self):
        """Test edge cases for character-based token calculation."""
        # Test very short text
        assert ai_utils.count_tokens("a", "openai:gpt-4") == 1  # 1 char, forced to 1 token

        # Test long text
        long_text = "a" * 100  # 100 chars
        # 100 / 3.4 = 29.41 -> 29 tokens
        expected = round(100 / 3.4)
        assert ai_utils.count_tokens(long_text, "openai:gpt-4") == expected

        # Test with spaces and newlines
        text_with_spaces = "Hello \n\n world"  # 14 chars including spaces and newlines
        expected = round(14 / 3.4)  # = 4 tokens
        actual = ai_utils.count_tokens(text_with_spaces, "openai:gpt-4")
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_character_based_calculation_accuracy(self):
        """Test that character-based calculation gives reasonable results."""
        # Test that our calculation gives consistent results
        text = "The quick brown fox jumps over the lazy dog"
        token_count = ai_utils.count_tokens(text, "any:model")

        # Should be the same as the direct calculation
        expected = round(len(text) / 3.4)
        assert token_count == expected

        # Should be reasonable for this text (not way off)
        assert 10 <= token_count <= 15  # Reasonable range for this sentence

        # Test that different content lengths scale appropriately
        short_text = "Hi"
        medium_text = "This is a medium length message"
        long_text = short_text * 50

        short_tokens = ai_utils.count_tokens(short_text, "any:model")
        medium_tokens = ai_utils.count_tokens(medium_text, "any:model")
        long_tokens = ai_utils.count_tokens(long_text, "any:model")

        assert short_tokens < medium_tokens < long_tokens


class TestAIError:
    """Test AIError class."""

    def test_ai_error_class_exists(self):
        """Test that AIError class exists and can be instantiated."""
        error = AIError("Test error")
        assert str(error) == "Test error"

    def test_ai_error_with_type(self):
        """Test AIError with error type."""
        error = AIError("Test error", error_type="model")
        assert error.error_type == "model"


class TestGenerateWithRetries:
    def test_unsupported_provider(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "bad:model", [], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_empty_messages(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "openai:gpt-4", [], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_missing_provider_func(self):
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries({}, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    @patch("gac.ai_utils.Status")
    def test_skip_success_message(self, mock_status):
        mock_spinner = MagicMock()
        mock_status.return_value = mock_spinner
        funcs = {"openai": lambda **kw: "ok"}
        ai_utils.generate_with_retries(
            funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, False, False, True
        )
        mock_spinner.stop.assert_called_once()

    def test_empty_content(self):
        funcs = {"openai": lambda **kw: ""}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    def test_none_content(self):
        funcs = {"openai": lambda **kw: None}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, True)
        assert e.value.error_type == "model"

    @patch("gac.ai_utils.Status")
    @patch("gac.ai_utils.console")
    def test_auth_error_spinner_fail(self, mock_console, mock_status):
        mock_spinner = MagicMock()
        mock_status.return_value = mock_spinner

        def raise_auth_error(**kw):
            raise AIError.authentication_error("Invalid API key")

        funcs = {"openai": raise_auth_error}
        with pytest.raises(AIError):
            ai_utils.generate_with_retries(
                funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 1, False
            )
        mock_spinner.stop.assert_called()
        mock_console.print.assert_called_once()

    @patch("gac.ai_utils.time.sleep")
    def test_retry_warning(self, mock_sleep):
        call_count = [0]

        def func(**kw):
            call_count[0] += 1
            if call_count[0] < 2:
                raise AIError.connection_error("fail")
            return "ok"

        funcs = {"openai": func}
        ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert call_count[0] == 2

    def test_final_auth_error(self):
        def raise_auth_error(**kw):
            raise AIError.authentication_error("Invalid API key")

        funcs = {"openai": raise_auth_error}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert e.value.error_type == "authentication"

    def test_final_model_error(self):
        def raise_model_error(**kw):
            raise AIError.model_error("Model not found")

        funcs = {"openai": raise_model_error}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert e.value.error_type == "model"

    def test_final_unknown_error(self):
        """Test unknown error handling path (line 241)."""

        def raise_unknown_error(**kw):
            # Create an AIError with no specific type
            error = AIError("Something went wrong")
            error.error_type = "something_else"  # Unknown type
            raise error

        funcs = {"openai": raise_unknown_error}
        with pytest.raises(AIError) as e:
            ai_utils.generate_with_retries(funcs, "openai:gpt-4", [{"role": "user", "content": "x"}], 0.7, 100, 2, True)
        assert e.value.error_type == "unknown"
        assert "Failed to generate" in str(e.value) and "after 2 retries" in str(e.value)
