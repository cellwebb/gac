"""Tests for the Git command result model – failure vs empty output semantics.

These tests verify that ``GitCommandResult`` and ``run_git_command``
properly distinguish between a command that succeeds with empty output
and a command that fails, and that stderr is preserved through failures.
"""

from __future__ import annotations

import logging
import subprocess
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from gac.errors import GacError, GitError
from gac.git import GitCommandResult, run_git_command


@contextmanager
def assertLogsSafe(logger_name: str, level: str = "WARNING"):
    """Context manager that captures log records at the given level.

    Unlike unittest's assertLogs, this does not fail when no messages are emitted.
    Yields a list that will be populated with formatted messages after the block.
    """
    logger = logging.getLogger(logger_name)
    handler = logging.Handler()
    records: list[logging.LogRecord] = []
    handler.emit = lambda record: records.append(record)  # type: ignore[attr-defined]
    handler.setLevel(getattr(logging, level))
    logger.addHandler(handler)
    old_level = logger.level
    if logger.level > getattr(logging, level):
        logger.setLevel(getattr(logging, level))
    try:

        class _Captured:
            output: list[str] = []

        captured = _Captured()
        yield captured
    finally:
        captured.output = [str(r.getMessage()) for r in records]
        logger.removeHandler(handler)
        logger.setLevel(old_level)


class TestGitCommandResult:
    """Unit tests for the GitCommandResult named tuple."""

    def test_ok_factory_success(self):
        """GitCommandResult.ok() creates a successful result."""
        result = GitCommandResult.ok("output")
        assert result.success
        assert result.output == "output"
        assert result.returncode == 0
        assert result.stderr == ""

    def test_ok_factory_empty_output(self):
        """GitCommandResult.ok("") is a successful result with empty output."""
        result = GitCommandResult.ok("")
        assert result.success
        assert result.output == ""
        assert result.returncode == 0
        assert result.stderr == ""

    def test_fail_factory_with_returncode(self):
        """GitCommandResult.fail() creates a failed result with returncode."""
        result = GitCommandResult.fail(returncode=1)
        assert not result.success
        assert result.output == ""
        assert result.returncode == 1
        assert result.stderr == ""

    def test_fail_factory_with_stderr(self):
        """GitCommandResult.fail() captures stderr."""
        result = GitCommandResult.fail(returncode=128, stderr="fatal: not a git repository")
        assert not result.success
        assert result.returncode == 128
        assert result.stderr == "fatal: not a git repository"

    def test_fail_factory_with_stdout_and_stderr(self):
        """GitCommandResult.fail() can carry both stdout and stderr."""
        result = GitCommandResult.fail(returncode=1, output="partial", stderr="error details")
        assert not result.success
        assert result.output == "partial"
        assert result.stderr == "error details"

    def test_success_vs_empty_output_distinction(self):
        """The key distinction: ok("") ≠ fail(returncode=1)."""
        ok_empty = GitCommandResult.ok("")
        fail_result = GitCommandResult.fail(returncode=1)
        assert ok_empty.success
        assert not fail_result.success
        assert ok_empty.output == fail_result.output  # both ""
        # But the caller can tell them apart via .success
        assert ok_empty.success != fail_result.success

    def test_output_on_failed_result_emits_warning(self):
        """Accessing .output on a failed result emits a logger warning."""
        result = GitCommandResult.fail(returncode=128, stderr="bad repo")
        with assertLogsSafe("gac.git", level="WARNING") as cm:
            _ = result.output
        assert ".output accessed on failed result" in cm.output[0]

    def test_output_on_success_no_warning(self):
        """Accessing .output on a successful result emits no warning."""
        result = GitCommandResult.ok("data")
        with assertLogsSafe("gac.git", level="WARNING") as cm:
            _ = result.output
        assert len(cm.output) == 0

    def test_output_warning_only_once(self):
        """The .output warning only fires once per failed result."""
        result = GitCommandResult.fail(returncode=1)
        with assertLogsSafe("gac.git", level="WARNING") as cm:
            _ = result.output  # First access triggers warning
            _ = result.output  # Second access should not
        assert len(cm.output) == 1


class TestFailMessage:
    """Tests for GitCommandResult.fail_message() — consistent error formatting."""

    def test_context_and_stderr(self):
        """fail_message includes context and stderr."""
        result = GitCommandResult.fail(returncode=128, stderr="not a git repository")
        assert result.fail_message("rev-parse") == "rev-parse (exit code 128): not a git repository"

    def test_context_without_stderr(self):
        """fail_message includes context and exit code when stderr is empty."""
        result = GitCommandResult.fail(returncode=1)
        assert result.fail_message("diff") == "diff (exit code 1)"

    def test_no_context_with_stderr(self):
        """fail_message falls back to generic message when no context given."""
        result = GitCommandResult.fail(returncode=42, stderr="oops")
        assert result.fail_message() == "Git command failed (exit code 42): oops"

    def test_no_context_no_stderr(self):
        """fail_message with no context or stderr gives bare exit code."""
        result = GitCommandResult.fail(returncode=3)
        assert result.fail_message() == "Git command failed (exit code 3)"


class TestRequireSuccess:
    """Tests for GitCommandResult.require_success."""

    def test_returns_output_on_success(self):
        """require_success() returns the output for successful results."""
        result = GitCommandResult.ok("good output")
        assert result.require_success() == "good output"

    def test_returns_empty_string_on_ok_empty(self):
        """require_success() returns '' for ok('') results."""
        result = GitCommandResult.ok("")
        assert result.require_success() == ""

    def test_raises_git_error_on_failure(self):
        """require_success() raises GitError for failed results."""
        result = GitCommandResult.fail(returncode=128)
        with pytest.raises(GitError, match="exit code 128"):
            result.require_success()

    def test_includes_stderr_in_error_message(self):
        """require_success() includes stderr in the GitError message."""
        result = GitCommandResult.fail(returncode=1, stderr="pathspec 'foo' did not match")
        with pytest.raises(GitError, match="pathspec"):
            result.require_success()

    def test_error_format_without_stderr(self):
        """require_success() falls back to return code when stderr is empty."""
        result = GitCommandResult.fail(returncode=42)
        with pytest.raises(GitError, match=r"Git command failed \(exit code 42\)$"):
            result.require_success()

    def test_error_format_with_stderr(self):
        """require_success() joins return code and stderr with ': '."""
        result = GitCommandResult.fail(returncode=1, stderr="some detail")
        with pytest.raises(GitError, match=r"exit code 1\): some detail"):
            result.require_success()


class TestRunGitCommand:
    """Tests for run_git_command distinguishing success vs failure."""

    @patch("gac.git.run_subprocess")
    def test_successful_command_with_output(self, mock_run):
        """A command that succeeds with output yields a success result."""
        mock_run.return_value = "file1.py\nfile2.py"
        result = run_git_command(["diff", "--name-only", "--cached"])
        assert result.success
        assert "file1.py" in result.output
        assert result.returncode == 0
        assert result.stderr == ""

    @patch("gac.git.run_subprocess")
    def test_successful_command_with_empty_output(self, mock_run):
        """A command that succeeds with no output yields ok(''), NOT fail()."""
        mock_run.return_value = ""
        result = run_git_command(["diff", "--name-only", "--cached"])
        assert result.success
        assert result.output == ""
        # This is the KEY distinction from the old API
        assert result.success is True  # empty output ≠ failure

    @patch("gac.git.run_subprocess")
    def test_failed_command_returns_fail_result(self, mock_run):
        """A CalledProcessError yields a fail result (no exception raised)."""
        mock_run.side_effect = subprocess.CalledProcessError(128, "git", stderr="fatal: not a git repository")
        result = run_git_command(["rev-parse", "--show-toplevel"])
        assert not result.success
        assert result.returncode == 128

    @patch("gac.git.run_subprocess")
    def test_failed_command_captures_stdout(self, mock_run):
        """Stdout from a CalledProcessError is captured in the result."""
        exc = subprocess.CalledProcessError(1, "git", stderr="error msg")
        exc.stdout = "partial output"
        mock_run.side_effect = exc
        result = run_git_command(["add", "nonexistent_file"])
        assert not result.success
        assert result.output == "partial output"

    @patch("gac.git.run_subprocess")
    def test_failed_command_captures_stderr(self, mock_run):
        """Stderr from a CalledProcessError is captured in the result."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="error: pathspec 'foo' did not match any known file"
        )
        result = run_git_command(["add", "foo"])
        assert not result.success
        assert "pathspec" in result.stderr
        assert "foo" in result.stderr

    @patch("gac.git.run_subprocess")
    def test_require_success_on_failed_result_includes_stderr(self, mock_run):
        """require_success() on a failed result raises GitError with stderr."""
        mock_run.side_effect = subprocess.CalledProcessError(128, "git", stderr="fatal: not a git repository")
        result = run_git_command(["rev-parse", "--show-toplevel"])
        with pytest.raises(GitError, match="not a git repository"):
            result.require_success()

    @patch("gac.git.run_subprocess")
    def test_oserror_propagates(self, mock_run):
        """OSError from subprocess propagates (not caught by run_git_command)."""
        mock_run.side_effect = OSError("git not found")
        with pytest.raises(OSError, match="git not found"):
            run_git_command(["status"])

    @patch("gac.git.run_subprocess")
    def test_gac_error_propagates(self, mock_run):
        """GacError (e.g. timeout) from run_subprocess propagates."""
        mock_run.side_effect = GacError("Command timed out")
        with pytest.raises(GacError, match="timed out"):
            run_git_command(["status"])


class TestGetStagedFilesFailurePropagation:
    """Verify get_staged_files() raises GitError on command failure."""

    @patch("gac.git.run_git_command")
    def test_raises_git_error_on_failure(self, mock_run):
        """get_staged_files() raises GitError instead of returning []."""
        from gac.git import get_staged_files

        mock_run.return_value = GitCommandResult.fail(returncode=128, stderr="not a git repository")
        with pytest.raises(GitError, match="Failed to list staged files"):
            get_staged_files()

    @patch("gac.git.run_git_command")
    def test_returns_empty_list_on_legitimate_empty(self, mock_run):
        """get_staged_files() returns [] for successful-but-empty output."""
        from gac.git import get_staged_files

        mock_run.return_value = GitCommandResult.ok("")
        assert get_staged_files() == []

    @patch("gac.git.run_git_command")
    def test_error_message_includes_stderr(self, mock_run):
        """get_staged_files() includes stderr in the GitError."""
        from gac.git import get_staged_files

        mock_run.return_value = GitCommandResult.fail(returncode=128, stderr="corrupted index")
        with pytest.raises(GitError, match="corrupted index"):
            get_staged_files()


class TestGetStagedStatusFailurePropagation:
    """Verify get_staged_status() raises GitError on command failure."""

    @patch("gac.git.run_git_command")
    def test_raises_git_error_on_failure(self, mock_run):
        """get_staged_status() raises GitError instead of returning fallback."""
        from gac.git import get_staged_status

        mock_run.return_value = GitCommandResult.fail(returncode=128, stderr="bad config")
        with pytest.raises(GitError, match="Failed to get staged status"):
            get_staged_status()

    @patch("gac.git.run_git_command")
    def test_returns_fallback_on_legitimate_empty(self, mock_run):
        """get_staged_status() returns fallback string for ok('')."""
        from gac.git import get_staged_status

        mock_run.return_value = GitCommandResult.ok("")
        assert get_staged_status() == "No changes staged for commit."


class TestPushChangesFailureVsEmpty:
    """Verify push_changes() distinguishes git-remote failure from no remotes."""

    @patch("gac.git.run_git_command")
    def test_no_remotes_returns_false(self, mock_run):
        """push_changes() returns False when git remote succeeds but is empty."""
        from gac.git import push_changes

        mock_run.return_value = GitCommandResult.ok("")
        assert push_changes() is False

    @patch("gac.git.run_git_command")
    def test_remote_failure_returns_false(self, mock_run):
        """push_changes() returns False when git remote command fails."""
        from gac.git import push_changes

        mock_run.return_value = GitCommandResult.fail(returncode=128, stderr="dubious ownership")
        assert push_changes() is False

    @patch("gac.git.logger")
    @patch("gac.git.run_git_command")
    def test_remote_failure_logs_stderr(self, mock_run, mock_logger):
        """push_changes() logs the stderr from git remote failure."""
        from gac.git import push_changes

        mock_run.return_value = GitCommandResult.fail(returncode=128, stderr="dubious ownership")
        push_changes()
        logged_msg = mock_logger.error.call_args[0][0]
        assert "dubious ownership" in logged_msg

    @patch("gac.git.logger")
    @patch("gac.git.run_git_command")
    def test_no_remotes_logs_correct_message(self, mock_run, mock_logger):
        """push_changes() logs 'No configured remote' for ok('')."""
        from gac.git import push_changes

        mock_run.return_value = GitCommandResult.ok("")
        push_changes()
        mock_logger.error.assert_called_once_with("No configured remote repository.")
