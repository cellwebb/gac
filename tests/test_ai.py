"""Tests for ai module."""

from unittest.mock import patch

import pytest
import tiktoken

from gac.ai import extract_text_content, generate_with_fallback, get_encoding
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


class TestGenerateWithFallback:
    """Tests for the generate_with_fallback function."""

    @patch("gac.ai.generate_commit_message")
    def test_primary_model_success(self, mock_generate):
        """Test that primary model is used when it works successfully."""
        # Setup the mock to return a successful result
        mock_generate.return_value = "feat: Add new feature"

        # Call the function with primary model only
        result = generate_with_fallback(
            primary_model="anthropic:claude-3-5-haiku",
            prompt="Test prompt",
            backup_model="openai:gpt-4o",
        )

        # Verify primary model was called with correct parameters
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        assert args[0] == "anthropic:claude-3-5-haiku"  # Check primary model was used
        assert args[1] == "Test prompt"  # Check prompt was passed correctly

        # Verify the expected result was returned
        assert result == "feat: Add new feature"

    @patch("gac.ai.generate_commit_message")
    @patch("gac.ai.print_message")  # Mock print_message to avoid console output in tests
    def test_fallback_to_backup_model(self, mock_print, mock_generate):
        """Test fallback to backup model when primary model fails."""
        # Setup mock to fail on first call (primary) and succeed on second call (backup)
        mock_generate.side_effect = [
            AIError("Primary model failed", error_type="connection"),
            "fix: Fix the bug with backup model",
        ]

        # Call the function with both primary and backup models
        result = generate_with_fallback(
            primary_model="anthropic:claude-3-5-haiku",
            prompt="Test prompt",
            backup_model="openai:gpt-4o",
            quiet=True,  # Set quiet to avoid logger message issues in tests
        )

        # Verify both models were called
        assert mock_generate.call_count == 2

        # Verify first call was with primary model
        primary_call = mock_generate.call_args_list[0]
        assert primary_call[0][0] == "anthropic:claude-3-5-haiku"

        # Verify second call was with backup model
        backup_call = mock_generate.call_args_list[1]
        assert backup_call[0][0] == "openai:gpt-4o"

        # Verify the result from backup model was returned
        assert result == "fix: Fix the bug with backup model"

    @patch("gac.ai.generate_commit_message")
    @patch("gac.ai.print_message")
    def test_both_models_fail(self, mock_print, mock_generate):
        """Test error handling when both primary and backup models fail."""
        # Setup mock to fail on both calls
        primary_error = AIError("Primary model failed", error_type="timeout")
        backup_error = AIError("Backup model failed", error_type="authentication")
        mock_generate.side_effect = [primary_error, backup_error]

        # Call function and expect it to raise an AIError
        with pytest.raises(AIError) as exc_info:
            generate_with_fallback(
                primary_model="anthropic:claude-3-5-haiku",
                prompt="Test prompt",
                backup_model="openai:gpt-4o",
                quiet=True,
            )

        # Verify error message contains details about both failures
        error_message = str(exc_info.value)
        assert "Both primary and backup models failed" in error_message
        assert "Primary model error" in error_message
        assert "Backup model error" in error_message
        assert mock_generate.call_count == 2

    @patch("gac.ai.generate_commit_message")
    def test_no_backup_model(self, mock_generate):
        """Test that the original error is raised when no backup model is provided."""
        # Setup mock to fail
        error = AIError("Primary model failed", error_type="connection")
        mock_generate.side_effect = error

        # Call function with no backup model and expect original error
        with pytest.raises(AIError) as exc_info:
            generate_with_fallback(
                primary_model="anthropic:claude-3-5-haiku",
                prompt="Test prompt",
                backup_model=None,
            )

        # Verify the original error is raised
        assert exc_info.value is error
        mock_generate.assert_called_once()
