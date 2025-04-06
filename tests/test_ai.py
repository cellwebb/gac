"""Tests for ai module."""

from unittest.mock import MagicMock, patch

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
