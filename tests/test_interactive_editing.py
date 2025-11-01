"""Unit tests for in-place interactive editing functionality."""

from unittest import mock

from gac.utils import edit_commit_message_inplace


class TestEditCommitMessageInplace:
    """Tests for edit_commit_message_inplace() function."""

    def test_edit_commit_message_success(self):
        """Test successful in-place editing."""
        initial_message = "feat: initial message"
        edited_message = "feat: edited message\n\nWith more details"

        with mock.patch("gac.utils.prompt", return_value=edited_message):
            result = edit_commit_message_inplace(initial_message)
            assert result == edited_message

    def test_edit_commit_message_with_context(self):
        """Test that context is displayed before editing."""
        initial_message = "fix: bug"
        context = {
            "files_changed": 3,
            "insertions": 42,
            "deletions": 10,
        }

        with mock.patch("gac.utils.prompt", return_value="fix: updated bug fix"):
            result = edit_commit_message_inplace(initial_message, context)
            assert result == "fix: updated bug fix"

    def test_edit_commit_message_empty_result(self):
        """Test handling when user provides empty message."""
        with mock.patch("gac.utils.prompt", return_value="   \n\n  "):
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_cancelled_eof(self):
        """Test handling when user cancels with EOF (Ctrl+D)."""
        with mock.patch("gac.utils.prompt", side_effect=EOFError()):
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_cancelled_keyboard_interrupt(self):
        """Test handling when user cancels with Ctrl+C."""
        with mock.patch("gac.utils.prompt", side_effect=KeyboardInterrupt()):
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_multiline(self):
        """Test that multiline messages are preserved."""
        multiline_message = "feat: add feature\n\nDetailed description\nacross multiple lines"

        with mock.patch("gac.utils.prompt", return_value=multiline_message):
            result = edit_commit_message_inplace("Original")
            assert result == multiline_message
            assert "\n\n" in result

    def test_edit_commit_message_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        with mock.patch("gac.utils.prompt", return_value="  \n  feat: message  \n\n  "):
            result = edit_commit_message_inplace("Original")
            assert result == "feat: message"

    def test_edit_commit_message_preserves_internal_whitespace(self):
        """Test that internal whitespace and formatting is preserved."""
        formatted_message = "feat: add feature\n\n- Added component A\n- Modified component B\n\nRelated to #123"

        with mock.patch("gac.utils.prompt", return_value=formatted_message):
            result = edit_commit_message_inplace("Original")
            assert result == formatted_message
            assert "- Added component A" in result
            assert "- Modified component B" in result

    def test_edit_commit_message_default_value_passed(self):
        """Test that initial message is passed as default to prompt."""
        initial_message = "fix: original message"

        with mock.patch("gac.utils.prompt") as mock_prompt:
            mock_prompt.return_value = "fix: updated message"
            edit_commit_message_inplace(initial_message)

            mock_prompt.assert_called_once()
            call_kwargs = mock_prompt.call_args.kwargs
            assert call_kwargs["default"] == initial_message
            assert call_kwargs["multiline"] is True
            assert call_kwargs["vi_mode"] is True

    def test_edit_commit_message_vi_mode_enabled(self):
        """Test that vi mode is enabled for editing."""
        with mock.patch("gac.utils.prompt") as mock_prompt:
            mock_prompt.return_value = "edited"
            edit_commit_message_inplace("original")

            call_kwargs = mock_prompt.call_args.kwargs
            assert call_kwargs["vi_mode"] is True

    def test_edit_commit_message_multiline_enabled(self):
        """Test that multiline mode is enabled."""
        with mock.patch("gac.utils.prompt") as mock_prompt:
            mock_prompt.return_value = "edited"
            edit_commit_message_inplace("original")

            call_kwargs = mock_prompt.call_args.kwargs
            assert call_kwargs["multiline"] is True

    def test_edit_commit_message_exception_handling(self):
        """Test that unexpected exceptions are handled gracefully."""
        with mock.patch("gac.utils.prompt", side_effect=Exception("Unexpected error")):
            result = edit_commit_message_inplace("original")
            assert result is None

    def test_edit_commit_message_no_context(self):
        """Test editing without context."""
        with mock.patch("gac.utils.prompt", return_value="edited message"):
            result = edit_commit_message_inplace("original", context=None)
            assert result == "edited message"

    def test_edit_commit_message_empty_context(self):
        """Test editing with empty context dict."""
        with mock.patch("gac.utils.prompt", return_value="edited message"):
            result = edit_commit_message_inplace("original", context={})
            assert result == "edited message"

    def test_edit_commit_message_partial_context(self):
        """Test editing with partial context (only files_changed)."""
        context = {"files_changed": 5}

        with mock.patch("gac.utils.prompt", return_value="edited message"):
            result = edit_commit_message_inplace("original", context=context)
            assert result == "edited message"
