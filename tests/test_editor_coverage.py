"""Coverage tests for editor.py — targeting FileNotFoundError, empty editor, and inplace editor paths."""

from unittest.mock import MagicMock, patch

from gac.editor import edit_commit_message_in_editor, edit_commit_message_inplace

# ---------------------------------------------------------------------------
# edit_commit_message_in_editor — error paths
# ---------------------------------------------------------------------------


class TestEditInEditorErrorPaths:
    @patch("gac.editor.subprocess.run", side_effect=FileNotFoundError("editor not found"))
    @patch("gac.editor._resolve_editor", return_value="nonexistent_editor")
    @patch("gac.editor._maybe_add_wait_flag", return_value=(["nonexistent_editor"], False))
    def test_file_not_found_error(self, mock_wait, mock_editor, mock_run):
        """FileNotFoundError when editor binary doesn't exist."""
        with patch("gac.editor.console.print"):
            result = edit_commit_message_in_editor("test message")
        assert result is None

    @patch("gac.editor.subprocess.run")
    @patch("gac.editor._resolve_editor", return_value="")
    @patch("gac.editor._maybe_add_wait_flag", return_value=([], False))
    def test_empty_editor_command(self, mock_wait, mock_editor, mock_run):
        """Empty editor command returns None."""
        with patch("gac.editor.console.print") as mock_print:
            result = edit_commit_message_in_editor("test message")
        assert result is None
        # Should print error about no editor configured
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("No editor configured" in c or "empty editor" in c for c in calls)

    @patch("gac.editor.subprocess.run", side_effect=KeyboardInterrupt())
    @patch("gac.editor._resolve_editor", return_value="vim")
    @patch("gac.editor._maybe_add_wait_flag", return_value=(["vim"], False))
    def test_keyboard_interrupt(self, mock_wait, mock_editor, mock_run):
        """KeyboardInterrupt during editor returns None."""
        with patch("gac.editor.console.print"):
            result = edit_commit_message_in_editor("test message")
        assert result is None

    @patch("gac.editor.subprocess.run")
    @patch("gac.editor._resolve_editor", return_value="vim")
    @patch("gac.editor._maybe_add_wait_flag", return_value=(["vim"], False))
    def test_editor_nonzero_exit(self, mock_wait, mock_editor, mock_run):
        """Editor exits with nonzero code returns None."""
        mock_run.return_value = MagicMock(returncode=1)
        with patch("gac.editor.console.print"):
            result = edit_commit_message_in_editor("test message")
        assert result is None


# ---------------------------------------------------------------------------
# edit_commit_message_inplace — branch coverage
# ---------------------------------------------------------------------------


class TestEditInplaceBranchCoverage:
    """Test branches in edit_commit_message_inplace that need coverage."""

    @patch("prompt_toolkit.Application")
    @patch("gac.editor.console.print")
    def test_keyboard_interrupt(self, mock_print, mock_app_class):
        """KeyboardInterrupt during inplace edit returns None."""
        mock_app = MagicMock()
        mock_app.run = MagicMock(side_effect=KeyboardInterrupt())
        mock_app_class.return_value = mock_app

        result = edit_commit_message_inplace("test message")
        assert result is None

    @patch("prompt_toolkit.Application")
    @patch("gac.editor.console.print")
    def test_eof_error(self, mock_print, mock_app_class):
        """EOFError during inplace edit returns None."""
        mock_app = MagicMock()
        mock_app.run = MagicMock(side_effect=EOFError())
        mock_app_class.return_value = mock_app

        result = edit_commit_message_inplace("test message")
        assert result is None

    @patch("prompt_toolkit.Application")
    @patch("gac.editor.console.print")
    def test_generic_exception(self, mock_print, mock_app_class):
        """Generic exception during inplace edit returns None."""
        mock_app = MagicMock()
        mock_app.run = MagicMock(side_effect=Exception("Unexpected error"))
        mock_app_class.return_value = mock_app

        with patch("gac.editor.logger"):
            result = edit_commit_message_inplace("test message")
        assert result is None
