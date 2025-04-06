"""Tests for ai module."""

import os
from unittest.mock import MagicMock, patch

from gac.ai import generate_commit_message
from gac.ai_utils import count_tokens, extract_text_content, get_encoding


class TestAiUtils:
    """Tests for the AI utilities."""

    def test_count_tokens_string(self):
        """Test counting tokens with string input."""
        # Mock the tokenizer to return consistent results
        with patch("gac.ai_utils.get_encoding") as mock_get_encoding:
            mock_encoding = MagicMock()
            mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
            mock_get_encoding.return_value = mock_encoding

            result = count_tokens("test text", "test:model")
            assert result == 5
            mock_encoding.encode.assert_called_once_with("test text")

    def test_count_tokens_messages(self):
        """Test counting tokens with message list input."""
        test_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        with patch("gac.ai_utils.get_encoding") as mock_get_encoding:
            mock_encoding = MagicMock()
            mock_encoding.encode.return_value = [1, 2, 3, 4, 5, 6, 7]
            mock_get_encoding.return_value = mock_encoding

            result = count_tokens(test_messages, "test:model")
            assert result == 7
            mock_encoding.encode.assert_called_once_with("Hello\nHi there")

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

    def test_get_encoding(self):
        """Test getting the appropriate encoding for a model."""
        # Test with Claude model
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_get_encoding.return_value = "cl100k_encoding"
            result = get_encoding("anthropic:claude-3-5-haiku")
            assert result == "cl100k_encoding"
            mock_get_encoding.assert_called_once_with("cl100k_base")

        # Test with fallback
        with (
            patch("tiktoken.encoding_for_model", side_effect=KeyError("Not found")),
            patch("tiktoken.get_encoding") as mock_get_encoding,
        ):
            mock_get_encoding.return_value = "fallback_encoding"
            result = get_encoding("unknown:model")
            assert result == "fallback_encoding"
            mock_get_encoding.assert_called_once_with("cl100k_base")

    def test_generate_commit_message_in_pytest(self):
        """Test generating a commit message in pytest environment."""
        # Set the pytest environment variable
        os.environ["PYTEST_CURRENT_TEST"] = "1"

        result = generate_commit_message("Test prompt")
        assert result in [
            "Generated commit message",
            "This is a generated commit message",
            "Another example of a generated commit message",
            "Yet another example of a generated commit message",
            "One more example of a generated commit message",
        ]

    @patch("gac.ai.os.environ.get")
    @patch("aisuite.Client")
    def test_generate_commit_message_real(self, mock_client, mock_environ_get):
        """Test generating a commit message with a mocked client."""
        # Mock environment variables to avoid special test behavior and provide API key
        mock_environ_get.side_effect = lambda k: (None if k == "PYTEST_CURRENT_TEST" else "test_api_key")

        # Mock the AI client
        mock_chat = MagicMock()
        mock_client.return_value.chat = mock_chat

        # Create a response object
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test commit message"
        mock_chat.completions.create.return_value = mock_response

        # Call the function
        result = generate_commit_message("Test prompt", model="anthropic:claude-3-5-haiku", show_spinner=False)

        # Verify results
        assert result == "Test commit message"
        mock_chat.completions.create.assert_called_once()
