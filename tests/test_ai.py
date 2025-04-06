"""Tests for ai module."""

import os
from unittest.mock import MagicMock, patch

from gac.ai import (
    generate_commit_message,
    truncate_git_diff,
    truncate_single_file_diff,
    truncate_with_beginning_and_end,
)
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

    def test_truncate_with_beginning_and_end(self):
        """Test truncating multi-line text preserving beginning and end."""
        lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]

        # Mock count_tokens to simulate different scenarios
        with patch("gac.ai.count_tokens") as mock_count_tokens:
            # Scenario 1: First and last lines already exceed limit
            mock_count_tokens.return_value = 10  # Always over limit
            result = truncate_with_beginning_and_end(lines, "test:model", 5)
            assert result == "Line 1"  # Just take first line

            # Reset for scenario 2
            mock_count_tokens.reset_mock()
            # Scenario 2: Can fit more lines
            # First call checks first+last, then we add Line 2, then Line 4, then check if can add more  # noqa: E501
            mock_count_tokens.side_effect = [3, 4, 5, 6, 7]
            result = truncate_with_beginning_and_end(lines, "test:model", 5)
            # Should contain first, last, and ellipsis
            assert "Line 1" in result
            assert "Line 5" in result
            assert "..." in result  # Ellipsis for truncation

    def test_truncate_git_diff(self):
        """Test truncating a git diff."""
        test_diff = """diff --git a/file1.txt b/file1.txt
index abc123..def456 100644
--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,4 @@
 Line 1
+Added line
 Line 2
 Line 3
diff --git a/file2.txt b/file2.txt
index 123abc..456def 100644
--- a/file2.txt
+++ b/file2.txt
@@ -1,2 +1,2 @@
-Removed line
+New line"""

        with (
            patch("gac.ai.count_tokens") as mock_count_tokens,
            patch("unidiff.PatchSet.from_string") as mock_parse_diff,
        ):
            # Create mock PatchSet objects
            file1_mock = MagicMock()
            file1_mock.added = 1
            file1_mock.removed = 0
            file1_mock.source_file = "a/file1.txt"
            file1_mock.target_file = "b/file1.txt"
            file1_mock.__str__.return_value = "diff --git a/file1.txt b/file1.txt\nContent 1"

            file2_mock = MagicMock()
            file2_mock.added = 1
            file2_mock.removed = 1
            file2_mock.source_file = "a/file2.txt"
            file2_mock.target_file = "b/file2.txt"
            file2_mock.__str__.return_value = "diff --git a/file2.txt b/file2.txt\nContent 2"

            # Setup the patch_set mock
            patch_set_mock = [file1_mock, file2_mock]
            mock_parse_diff.return_value = patch_set_mock

            # Setup token counting
            mock_count_tokens.side_effect = [
                20,  # First check if under limit
                10,  # file1 tokens
                5,  # file2 tokens
                15,  # importance calcs
            ]

            result = truncate_git_diff(test_diff, "test:model", 10)
            assert "file2.txt" in result  # Higher importance file should be included
            assert "files not shown" in result  # Truncation message

    def test_truncate_single_file_diff(self):
        """Test truncating a single file diff."""
        test_file_diff = """diff --git a/file.txt b/file.txt
index abc123..def456 100644
--- a/file.txt
+++ b/file.txt
@@ -1,5 +1,6 @@
 Line 1
 Line 2
+Added line
 Line 3
-Removed line
 Line 5"""

        # Create a simpler test that directly verifies truncation message presence
        with patch("gac.ai.count_tokens") as mock_count_tokens:
            # Mock count_tokens to return values forcing truncation in the fallback path
            mock_count_tokens.side_effect = lambda *args, **kwargs: (
                20 if len(args) > 0 and args[0] == test_file_diff else 3
            )

            # Call with very small token limit to ensure truncation
            result = truncate_single_file_diff(test_file_diff, "test:model", 5)

            # Verify truncation message appears
            assert "truncated" in result

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

        # Clean up
        if "PYTEST_CURRENT_TEST" in os.environ:
            del os.environ["PYTEST_CURRENT_TEST"]

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
