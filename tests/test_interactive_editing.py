"""Unit tests for in-place interactive editing functionality."""

import inspect
from unittest import mock

from gac.utils import edit_commit_message_inplace


class TestEditCommitMessageInplace:
    """Tests for edit_commit_message_inplace() function."""

    def _setup_app_mock(self, edited_text: str, submitted: bool = True, cancelled: bool = False):
        """Helper to set up Application.run() mock that modifies state properly."""

        def mock_run():
            stack = inspect.stack()
            for frame_info in stack:
                frame_locals = frame_info.frame.f_locals
                if "text_buffer" in frame_locals and "submitted" in frame_locals and "cancelled" in frame_locals:
                    frame_locals["text_buffer"].text = edited_text
                    frame_locals["submitted"]["value"] = submitted
                    frame_locals["cancelled"]["value"] = cancelled
                    break

        return mock_run

    def test_edit_commit_message_success(self):
        """Test successful in-place editing."""
        initial_message = "feat: initial message"
        edited_message = "feat: edited message\n\nWith more details"

        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock(edited_message, submitted=True)
            result = edit_commit_message_inplace(initial_message)
            assert result == edited_message

    def test_edit_commit_message_basic(self):
        """Test basic editing functionality."""
        initial_message = "fix: bug"

        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock("fix: updated bug fix", submitted=True)
            result = edit_commit_message_inplace(initial_message)
            assert result == "fix: updated bug fix"

    def test_edit_commit_message_empty_result(self):
        """Test handling when user provides empty message."""
        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock("   \n\n  ", submitted=True)
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_cancelled_eof(self):
        """Test handling when user cancels with EOF."""
        with mock.patch("prompt_toolkit.Application.run", side_effect=EOFError()):
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_cancelled_keyboard_interrupt(self):
        """Test handling when user cancels with Ctrl+C."""
        with mock.patch("prompt_toolkit.Application.run", side_effect=KeyboardInterrupt()):
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_cancelled_by_user(self):
        """Test handling when user cancels editing with Ctrl+C (cancelled state)."""
        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock("", submitted=False, cancelled=True)
            result = edit_commit_message_inplace("Initial message")
            assert result is None

    def test_edit_commit_message_multiline(self):
        """Test that multiline messages are preserved."""
        multiline_message = "feat: add feature\n\nDetailed description\nacross multiple lines"

        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock(multiline_message, submitted=True)
            result = edit_commit_message_inplace("Original")
            assert result == multiline_message
            assert "\n\n" in result

    def test_edit_commit_message_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock("  \n  feat: message  \n\n  ", submitted=True)
            result = edit_commit_message_inplace("Original")
            assert result == "feat: message"

    def test_edit_commit_message_preserves_internal_whitespace(self):
        """Test that internal whitespace and formatting is preserved."""
        formatted_message = "feat: add feature\n\n- Added component A\n- Modified component B\n\nRelated to #123"

        with mock.patch("prompt_toolkit.Application.run") as mock_run:
            mock_run.side_effect = self._setup_app_mock(formatted_message, submitted=True)
            result = edit_commit_message_inplace("Original")
            assert result == formatted_message
            assert "- Added component A" in result
            assert "- Modified component B" in result

    def test_edit_commit_message_exception_handling(self):
        """Test that unexpected exceptions are handled gracefully."""
        with mock.patch("prompt_toolkit.Application.run", side_effect=Exception("Unexpected error")):
            result = edit_commit_message_inplace("original")
            assert result is None

    def test_edit_commit_message_cursor_at_beginning(self):
        """Test that cursor starts at the beginning of the message."""
        initial_message = "feat: add feature"

        with mock.patch("prompt_toolkit.Application") as mock_app_class:
            mock_app = mock.MagicMock()
            mock_app_class.return_value = mock_app

            with mock.patch("prompt_toolkit.buffer.Buffer") as mock_buffer_class:
                mock_buffer = mock.MagicMock()
                mock_buffer_class.return_value = mock_buffer

                with mock.patch("prompt_toolkit.document.Document") as mock_document_class:
                    edit_commit_message_inplace(initial_message)

                    # Verify Document was created with cursor at position 0
                    mock_document_class.assert_called_once_with(text=initial_message, cursor_position=0)

    def test_edit_commit_message_vi_mode_set(self):
        """Test that vi mode is enabled."""
        with mock.patch("prompt_toolkit.Application") as mock_app_class:
            mock_app = mock.MagicMock()
            mock_app_class.return_value = mock_app

            edit_commit_message_inplace("test message")

            # Verify Application was called with EditingMode.VI
            call_kwargs = mock_app_class.call_args.kwargs
            from prompt_toolkit.enums import EditingMode

            assert call_kwargs["editing_mode"] == EditingMode.VI
