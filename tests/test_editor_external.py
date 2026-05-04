"""Unit tests for external $EDITOR commit message editing functionality."""

import os
from unittest import mock

import pytest

from gac.editor import (
    _maybe_add_wait_flag,
    _resolve_editor,
    _run_git_var_editor,
    _split_editor_command,
    edit_commit_message_in_editor,
)


class TestSplitEditorCommand:
    """Tests for _split_editor_command() — shlex splitting with quote stripping."""

    def test_simple_command(self):
        """Simple editor name with no args."""
        with mock.patch("gac.editor.os.name", "posix"):
            assert _split_editor_command("vim") == ["vim"]

    def test_command_with_args(self):
        """Editor with arguments."""
        with mock.patch("gac.editor.os.name", "posix"):
            assert _split_editor_command("code --wait") == ["code", "--wait"]

    def test_quoted_path_posix(self):
        """Quoted path with spaces on Unix — posix mode strips quotes."""
        with mock.patch("gac.editor.os.name", "posix"):
            result = _split_editor_command('"/usr/local/bin/my editor" --flag')
            assert result == ["/usr/local/bin/my editor", "--flag"]

    def test_quoted_path_windows(self):
        """Quoted path with spaces on Windows — non-posix preserves backslashes, strips quotes."""
        with mock.patch("gac.editor.os.name", "nt"):
            result = _split_editor_command(r'"C:\Program Files\Vim\gvim.exe" --nofork')
            assert result[0] == r"C:\Program Files\Vim\gvim.exe"
            assert result[1] == "--nofork"

    def test_unquoted_path_no_spaces_windows(self):
        """Unquoted path without spaces on Windows."""
        with mock.patch("gac.editor.os.name", "nt"):
            result = _split_editor_command(r"C:\Tools\vim\gvim.exe --nofork")
            assert result[0] == r"C:\Tools\vim\gvim.exe"
            assert result[1] == "--nofork"

    def test_single_quotes_posix(self):
        """Single-quoted path on Unix."""
        with mock.patch("gac.editor.os.name", "posix"):
            result = _split_editor_command("'/opt/my editor' --flag")
            assert result == ["/opt/my editor", "--flag"]

    def test_single_quotes_windows_stripped(self):
        """Single-quoted path on Windows — quotes stripped by post-processing."""
        with mock.patch("gac.editor.os.name", "nt"):
            result = _split_editor_command("'C:\\Editor\\editor.exe' --flag")
            assert result[0] == r"C:\Editor\editor.exe"
            assert result[1] == "--flag"

    def test_unclosed_quote_raises_valueerror(self):
        """Unclosed quotes raise ValueError — shlex rejects malformed input.

        This is correct: a malformed $EDITOR value should fail explicitly
        rather than silently produce a broken argv. The caller
        (edit_commit_message_in_editor) catches this via its
        generic Exception handler.
        """
        with mock.patch("gac.editor.os.name", "nt"):
            with pytest.raises(ValueError, match="No closing quotation"):
                _split_editor_command('"foo --flag')

    def test_empty_string(self):
        """Empty editor string returns empty list."""
        with mock.patch("gac.editor.os.name", "posix"):
            assert _split_editor_command("") == []

    def test_multiple_args(self):
        """Editor with multiple arguments."""
        with mock.patch("gac.editor.os.name", "posix"):
            result = _split_editor_command("vim -u ~/.vimrc -c 'set ft=gitcommit'")
            assert result[0] == "vim"
            assert "-u" in result
            assert "set ft=gitcommit" in result


class TestMaybeAddWaitFlag:
    """Tests for _maybe_add_wait_flag() — auto-insert wait flags for GUI editors."""

    def test_code_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["code"])
        assert added is True
        assert argv == ["code", "--wait"]

    def test_code_insiders_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["code-insiders"])
        assert added is True
        assert argv == ["code-insiders", "--wait"]

    def test_codium_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["codium"])
        assert added is True
        assert argv == ["codium", "--wait"]

    def test_code_oss_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["code-oss"])
        assert added is True
        assert argv == ["code-oss", "--wait"]

    def test_cursor_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["cursor"])
        assert added is True
        assert argv == ["cursor", "--wait"]

    def test_zed_adds_wait(self):
        argv, added = _maybe_add_wait_flag(["zed"])
        assert added is True
        assert argv == ["zed", "--wait"]

    def test_subl_adds_w(self):
        """Sublime Text uses -w (not --wait)."""
        argv, added = _maybe_add_wait_flag(["subl"])
        assert added is True
        assert argv == ["subl", "-w"]

    def test_code_with_wait_not_duplicated(self):
        argv, added = _maybe_add_wait_flag(["code", "--wait"])
        assert added is False
        assert argv == ["code", "--wait"]

    def test_code_with_w_shorthand_not_duplicated(self):
        """-w is an accepted shorthand for --wait."""
        argv, added = _maybe_add_wait_flag(["code", "-w"])
        assert added is False
        assert argv == ["code", "-w"]

    def test_subl_with_w_not_duplicated(self):
        argv, added = _maybe_add_wait_flag(["subl", "-w"])
        assert added is False
        assert argv == ["subl", "-w"]

    def test_vim_unchanged(self):
        argv, added = _maybe_add_wait_flag(["vim"])
        assert added is False
        assert argv == ["vim"]

    def test_nano_unchanged(self):
        argv, added = _maybe_add_wait_flag(["nano"])
        assert added is False
        assert argv == ["nano"]

    def test_full_path_code_detected(self):
        """Even /usr/local/bin/code is detected via basename."""
        argv, added = _maybe_add_wait_flag(["/usr/local/bin/code"])
        assert added is True
        assert argv == ["/usr/local/bin/code", "--wait"]

    def test_exe_extension_stripped(self):
        """Windows .exe extension is stripped before lookup."""
        argv, added = _maybe_add_wait_flag(["code.exe"])
        assert added is True
        assert argv == ["code.exe", "--wait"]

    def test_wait_flag_inserted_before_existing_args(self):
        """Wait flag goes right after the binary, before other args."""
        argv, added = _maybe_add_wait_flag(["code", "--new-window"])
        assert added is True
        assert argv == ["code", "--wait", "--new-window"]

    def test_empty_argv(self):
        argv, added = _maybe_add_wait_flag([])
        assert added is False
        assert argv == []


class TestRunGitVarEditor:
    """Tests for _run_git_var_editor() — the git var GIT_EDITOR query."""

    def test_returns_editor_on_success(self):
        """Returns the editor string when git var succeeds."""
        mock_result = mock.MagicMock(returncode=0, stdout="vim\n")
        with mock.patch("gac.editor.subprocess.run", return_value=mock_result):
            assert _run_git_var_editor() == "vim"

    def test_returns_none_on_nonzero_exit(self):
        """Returns None when git var exits non-zero."""
        mock_result = mock.MagicMock(returncode=1, stdout="")
        with mock.patch("gac.editor.subprocess.run", return_value=mock_result):
            assert _run_git_var_editor() is None

    def test_returns_none_on_empty_stdout(self):
        """Returns None when git var succeeds but outputs nothing."""
        mock_result = mock.MagicMock(returncode=0, stdout="  \n")
        with mock.patch("gac.editor.subprocess.run", return_value=mock_result):
            assert _run_git_var_editor() is None

    def test_returns_none_when_git_not_found(self):
        """Returns None when git binary is not installed."""
        with mock.patch("gac.editor.subprocess.run", side_effect=FileNotFoundError):
            assert _run_git_var_editor() is None

    def test_returns_none_on_timeout(self):
        """Returns None when git var times out."""
        import subprocess

        with mock.patch("gac.editor.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert _run_git_var_editor() is None

    def test_includes_core_editor(self):
        """git var GIT_EDITOR respects core.editor (tested via mock)."""
        mock_result = mock.MagicMock(returncode=0, stdout="nano\n")
        with mock.patch("gac.editor.subprocess.run", return_value=mock_result):
            # Even without any env vars, git resolves it from config
            assert _run_git_var_editor() == "nano"


class TestResolveEditor:
    """Tests for _resolve_editor() precedence logic."""

    def test_gac_editor_highest_priority(self):
        """GAC_EDITOR wins over everything including git var."""
        env = {"GAC_EDITOR": "gac-editor", "GIT_EDITOR": "git-editor", "VISUAL": "visual", "EDITOR": "editor"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value="git-resolved"),
        ):
            assert _resolve_editor() == "gac-editor"

    def test_gac_editor_over_git_var(self):
        """GAC_EDITOR takes precedence over git var GIT_EDITOR."""
        env = {"GAC_EDITOR": "code --wait"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value="vim"),
        ):
            assert _resolve_editor() == "code --wait"

    def test_git_var_takes_precedence_over_env_vars(self):
        """git var GIT_EDITOR wins over all env vars (except GAC_EDITOR)."""
        env = {"GIT_EDITOR": "env-editor", "VISUAL": "visual", "EDITOR": "editor"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value="git-resolved"),
        ):
            assert _resolve_editor() == "git-resolved"

    def test_env_git_editor_when_git_var_fails(self):
        """$GIT_EDITOR is used when git var fails."""
        env = {"GIT_EDITOR": "emacs", "VISUAL": "visual", "EDITOR": "nano"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value=None),
        ):
            assert _resolve_editor() == "emacs"

    def test_visual_over_editor(self):
        """VISUAL wins over EDITOR when GIT_EDITOR is unset."""
        env = {"VISUAL": "visual-editor", "EDITOR": "editor"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value=None),
        ):
            assert _resolve_editor() == "visual-editor"

    def test_editor_when_no_visual(self):
        """EDITOR is used when GIT_EDITOR and VISUAL are unset."""
        env = {"EDITOR": "nano"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value=None),
        ):
            assert _resolve_editor() == "nano"

    def test_vi_fallback(self):
        """Falls back to 'vi' when nothing is set."""
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("gac.editor._run_git_var_editor", return_value=None),
        ):
            assert _resolve_editor() == "vi"


def _mock_tmp_file(name: str = "/tmp/test.commitmsg"):
    """Create a properly-wired NamedTemporaryFile mock.

    The context manager `with tempfile.NamedTemporaryFile(...) as tmp:` means
    `tmp` is the return value of `__enter__`, so we must set attributes on
    `__enter__.return_value`, not on the call return value directly.
    """
    mock_tmp_cls = mock.MagicMock()
    enter_result = mock_tmp_cls.return_value.__enter__.return_value
    enter_result.name = name
    return mock_tmp_cls, enter_result


class TestEditCommitMessageInEditor:
    """Tests for edit_commit_message_in_editor() function."""

    def test_successful_edit(self):
        """Test successful editing with $EDITOR."""
        mock_tmp, enter_result = _mock_tmp_file()
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", mock_tmp),
            mock.patch("builtins.open", mock.mock_open(read_data="feat: edited by vim\n\nWith details")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("feat: original")
            assert result == "feat: edited by vim\n\nWith details"
            # Verify message was written to the temp file
            enter_result.write.assert_called_once_with("feat: original")

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped from editor output."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="  \n  feat: message  \n\n  ")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("original")
            assert result == "feat: message"

    def test_empty_message_returns_none(self):
        """Test that an empty message after editing returns None."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="   \n\n   ")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("original")
            assert result is None

    def test_nonzero_exit_code_returns_none(self):
        """Test that a non-zero exit code from the editor returns None."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=1)
            result = edit_commit_message_in_editor("original")
            assert result is None

    def test_editor_not_found(self):
        """Test FileNotFoundError when editor binary doesn't exist."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=FileNotFoundError("No such file")),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
        ):
            result = edit_commit_message_in_editor("original")
            assert result is None

    def test_keyboard_interrupt_returns_none(self):
        """Test that KeyboardInterrupt during editing returns None."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=KeyboardInterrupt()),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
        ):
            result = edit_commit_message_in_editor("original")
            assert result is None

    def test_generic_exception_returns_none(self):
        """Test that unexpected exceptions are handled gracefully."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=RuntimeError("boom")),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
        ):
            result = edit_commit_message_in_editor("original")
            assert result is None

    def test_generic_exception_uses_logger_exception(self):
        """Test that unexpected exceptions use logger.exception (not logger.error)."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=RuntimeError("boom")),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
            mock.patch("gac.editor.logger") as mock_logger,
        ):
            edit_commit_message_in_editor("original")
            mock_logger.exception.assert_called_once()

    def test_generic_exception_shows_error_text(self):
        """Test that unexpected exception messages are shown to the user."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=RuntimeError("bad quoting in $EDITOR")),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("os.unlink"),
            mock.patch("gac.editor.console") as mock_console,
        ):
            edit_commit_message_in_editor("original")
            # Find the error print call
            error_calls = [c for c in mock_console.print.call_args_list if "error" in str(c)]
            assert any("bad quoting" in str(c) for c in error_calls)

    def test_shlex_split_editor_with_args(self):
        """Test that editors with arguments (e.g. 'code --wait') are split correctly."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="code --wait"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            edit_commit_message_in_editor("original")
            cmd = mock_run.call_args[0][0]
            assert cmd == ["code", "--wait", "/tmp/test.commitmsg"]

    def test_shlex_split_posix_false_preserves_backslashes(self):
        """Test that shlex.split with posix=False preserves backslashes.

        With posix=True (default on Unix), backslashes are escape chars.
        With posix=False (Windows), backslashes are literal — critical for
        Windows paths. We test a simple case (no spaces in path) since
        paths with spaces require quoting which shlex non-posix retains.
        """
        # A Windows-style path without spaces, plus a flag
        editor_value = r"C:\Tools\vim\gvim.exe --nofork"
        with (
            mock.patch("gac.editor._resolve_editor", return_value=editor_value),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
            mock.patch("os.unlink"),
            mock.patch("gac.editor.os.name", "nt"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            edit_commit_message_in_editor("original")
            cmd = mock_run.call_args[0][0]
            # On Windows (posix=False), backslashes are preserved as-is
            assert cmd[0] == r"C:\Tools\vim\gvim.exe"
            assert cmd[1] == "--nofork"

    def test_shlex_split_windows_quoted_path_with_spaces(self):
        """Quoted Windows paths should execute without retaining the quotes."""
        # This mirrors the `git var GIT_EDITOR` documentation examples:
        # "C:\Program Files\Vim\gvim.exe" --nofork
        editor_value = r'"C:\Program Files\Vim\gvim.exe" --nofork'
        with (
            mock.patch("gac.editor._resolve_editor", return_value=editor_value),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
            mock.patch("os.unlink"),
            mock.patch("gac.editor.os.name", "nt"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            edit_commit_message_in_editor("original")
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == r"C:\Program Files\Vim\gvim.exe"
            assert cmd[1] == "--nofork"

    def test_uses_git_var_resolved_editor(self):
        """Test that the editor from git var is used for launching."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="nano"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            edit_commit_message_in_editor("original")
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "nano"

    def test_multiline_message_preserved(self):
        """Test that multiline messages are preserved through the editor."""
        multiline = "feat: add feature\n\n- Added component A\n- Modified component B"
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data=multiline)),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("original")
            assert result == multiline
            assert "- Added component A" in result

    def test_temp_file_cleaned_up_on_success(self, tmp_path):
        """Test that temp file is cleaned up after successful edit using a real file."""
        real_file = tmp_path / "test.commitmsg"
        real_file.write_text("initial")

        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile") as mock_tmp_cls,
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            mock_tmp_cls.return_value.__enter__.return_value.name = str(real_file)
            mock_tmp_cls.return_value.__enter__.return_value.write = mock.MagicMock()
            edit_commit_message_in_editor("initial")

        # Real os.unlink should have deleted the file
        assert not real_file.exists()

    def test_temp_file_cleaned_up_on_error(self, tmp_path):
        """Test that temp file is cleaned up even when editor fails using a real file."""
        real_file = tmp_path / "test.commitmsg"
        real_file.write_text("initial")

        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run", side_effect=FileNotFoundError()),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile") as mock_tmp_cls,
        ):
            mock_tmp_cls.return_value.__enter__.return_value.name = str(real_file)
            mock_tmp_cls.return_value.__enter__.return_value.write = mock.MagicMock()
            edit_commit_message_in_editor("initial")

        assert not real_file.exists()

    def test_no_unlink_when_tmp_path_is_none(self):
        """Test that os.unlink is NOT called when tmp_path was never assigned."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run"),
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", side_effect=OSError("no temp dir")),
            mock.patch("os.unlink") as mock_unlink,
        ):
            edit_commit_message_in_editor("original")
            # tmp_path stays None, so os.unlink should never be called
            mock_unlink.assert_not_called()

    def test_unchanged_message_returns_none(self):
        """Test that an unchanged message (forking editor) returns None with warning."""
        # Simulates: editor is configured as a forking GUI editor ("code") but the
        # message is unchanged. We treat unchanged as "no edit".
        with (
            mock.patch("gac.editor._resolve_editor", return_value="code"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="feat: original")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("feat: original")
            assert result is None
            # Wait flag is auto-inserted so we don't race VS Code.
            cmd = mock_run.call_args[0][0]
            assert cmd[0:2] == ["code", "--wait"]

    def test_code_without_wait_auto_adds_wait(self):
        """Known forking editors get a wait flag inserted automatically."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="code"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="feat: edited in vs code")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("feat: original")
            assert result == "feat: edited in vs code"
            cmd = mock_run.call_args[0][0]
            assert cmd[0:2] == ["code", "--wait"]

    def test_unchanged_message_with_blocking_editor_returns_none(self):
        """Even vim with an unchanged message returns None (user chose not to edit)."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="feat: original")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("feat: original")
            assert result is None

    def test_changed_message_succeeds_despite_forking_editor_name(self):
        """If the message WAS changed, succeed even if editor is named 'code'."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="code --wait"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="feat: edited in vs code")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            result = edit_commit_message_in_editor("feat: original")
            assert result == "feat: edited in vs code"

    def test_tmp_file_appended_to_editor_cmd(self):
        """Test that the temp file path is the last argument to the editor command."""
        with (
            mock.patch("gac.editor._resolve_editor", return_value="vim"),
            mock.patch("gac.editor.subprocess.run") as mock_run,
            mock.patch("gac.editor.tempfile.NamedTemporaryFile", _mock_tmp_file()[0]),
            mock.patch("builtins.open", mock.mock_open(read_data="edited")),
            mock.patch("os.unlink"),
        ):
            mock_run.return_value = mock.MagicMock(returncode=0)
            edit_commit_message_in_editor("original")
            cmd = mock_run.call_args[0][0]
            assert cmd[-1] == "/tmp/test.commitmsg"
