import subprocess
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import GitError
from gac.git import (
    get_commit_hash,
    get_current_branch,
    get_diff,
    get_repo_root,
    get_staged_files,
    get_staged_status,
    push_changes,
    run_lefthook_hooks,
    run_pre_commit_hooks,
)


def test_get_repo_root_success(monkeypatch):
    def mock_check_output(args):
        return b"/repo/path\n"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    assert get_repo_root() == "/repo/path"


def test_get_current_branch_success(monkeypatch):
    def mock_check_output(args):
        return b"main\n"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    assert get_current_branch() == "main"


def test_get_commit_hash_success(monkeypatch):
    def mock_check_output(args):
        return b"abc123\n"

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    assert get_commit_hash() == "abc123"


def test_get_staged_files_all():
    """Test get_staged_files with no filtering."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = "file1.py\nfile2.md\nfile3.txt"
        result = get_staged_files()
        assert result == ["file1.py", "file2.md", "file3.txt"]


def test_get_staged_files_empty():
    """Test get_staged_files when no files are staged."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = ""
        result = get_staged_files()
        assert result == []

    # Also test when run_git_command raises GitError
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.side_effect = GitError("git error")
        result = get_staged_files()
        assert result == []


def test_get_staged_files_filter_by_type():
    """Test get_staged_files with file type filtering."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = "file1.py\nfile2.md\nfile3.txt\nfile4.py"
        result = get_staged_files(file_type=".py")
        assert result == ["file1.py", "file4.py"]


def test_get_staged_files_existing_only():
    """Test get_staged_files with existing_only flag."""
    with patch("gac.git.run_git_command") as mock_run, patch("os.path.isfile") as mock_isfile:
        mock_run.return_value = "file1.py\nfile2.md\nfile3.txt"
        mock_isfile.side_effect = [True, False, True]  # file2.md doesn't exist
        result = get_staged_files(existing_only=True)
        assert result == ["file1.py", "file3.txt"]


@pytest.mark.parametrize(
    "git_output,expected_content",
    [
        (
            "M\tfile1.py\nA\tfile2.md\nD\tfile3.txt",
            ["modified:   file1.py", "new file:   file2.md", "deleted:   file3.txt"],
        ),
        ("R100\told_file.py\tnew_file.py", ["renamed:   new_file.py"]),
        (
            "M\tmodified.py\nA\tadded.py\nD\tdeleted.py\nR100\told.py\tnew.py\nC\tcopied.py\nT\ttype_changed.py",
            [
                "modified:   modified.py",
                "new file:   added.py",
                "deleted:   deleted.py",
                "renamed:   new.py",
                "copied:   copied.py",
                "typechange:   type_changed.py",
            ],
        ),
        ("M\tfile1.py\n\n\nA\tfile2.py\n", ["modified:   file1.py", "new file:   file2.py"]),
    ],
)
def test_get_staged_status_formats(git_output, expected_content):
    """Test get_staged_status with various file statuses."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = git_output
        result = get_staged_status()
        assert "Changes to be committed:" in result
        for expected in expected_content:
            assert expected in result


def test_get_staged_status_empty():
    """Test get_staged_status when no files are staged."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = ""
        result = get_staged_status()
        assert result == "No changes staged for commit."


def test_get_staged_status_git_error():
    """Test get_staged_status when git command fails."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.side_effect = GitError("git error")
        result = get_staged_status()
        assert result == "No changes staged for commit."


def test_get_diff_unstaged():
    """Test get_diff with staged=False."""
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = "diff output"
        result = get_diff(staged=False)
        mock_run.assert_called_once_with(["diff", "--color"])
        assert result == "diff output"


def test_get_diff_exception():
    """Test get_diff when exception is raised."""
    with patch("gac.git.run_git_command") as mock_run, patch("gac.git.logger") as mock_logger:
        mock_run.side_effect = Exception("git error")
        try:
            get_diff()
            raise AssertionError("Expected GitError to be raised")
        except GitError as e:
            assert "Failed to get diff: git error" in str(e)
            mock_logger.error.assert_called_once()


def test_push_changes_no_remote():
    """Test push_changes when no remote is configured."""
    with patch("gac.git.run_git_command") as mock_run, patch("gac.git.logger") as mock_logger:
        mock_run.return_value = ""  # No remote configured
        result = push_changes()
        assert result is False
        mock_logger.error.assert_called_once_with("No configured remote repository.")


def test_push_changes_success():
    """Test push_changes when push is successful."""
    with patch("gac.git.run_git_command") as mock_run_git, patch("gac.git.run_subprocess") as mock_run_sub:
        mock_run_git.return_value = "origin\n"  # For 'git remote'
        mock_run_sub.return_value = ""  # For 'git push'
        result = push_changes()
        assert result is True
        mock_run_git.assert_called_once_with(["remote"])
        mock_run_sub.assert_called_once_with(["git", "push"], raise_on_error=True, strip_output=True)


def test_push_changes_git_error():
    """Test push_changes when push fails with CalledProcessError."""
    import subprocess

    with (
        patch("gac.git.run_git_command") as mock_run_git,
        patch("gac.git.run_subprocess") as mock_run_sub,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_run_git.return_value = "origin\n"  # For 'git remote'
        error = subprocess.CalledProcessError(1, ["git", "push"], "", "Failed to push")
        mock_run_sub.side_effect = error
        result = push_changes()
        assert result is False
        mock_logger.error.assert_called_once_with("Failed to push changes: Failed to push")


def test_push_changes_fatal_error():
    """Test push_changes when fatal error occurs."""
    import subprocess

    with (
        patch("gac.git.run_git_command") as mock_run_git,
        patch("gac.git.run_subprocess") as mock_run_sub,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_run_git.return_value = "origin\n"  # For 'git remote'
        error = subprocess.CalledProcessError(1, ["git", "push"], "", "fatal: No configured push destination")
        mock_run_sub.side_effect = error
        result = push_changes()
        assert result is False
        mock_logger.error.assert_called_once_with("No configured push destination.")


def test_push_changes_generic_exception():
    """Test push_changes when a generic exception occurs."""
    with (
        patch("gac.git.run_git_command") as mock_run_git,
        patch("gac.git.run_subprocess") as mock_run_sub,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_run_git.return_value = "origin\n"  # For 'git remote'
        mock_run_sub.side_effect = Exception("Unexpected error")
        result = push_changes()
        assert result is False
        mock_logger.error.assert_called_once_with("Failed to push changes: Unexpected error")


def test_get_diff_staged():
    with patch("gac.git.run_subprocess") as mock_run:
        mock_run.return_value = "diff output"
        result = get_diff(staged=True)
        mock_run.assert_called_once()
        assert "diff" in mock_run.call_args[0][0]
        assert "--cached" in mock_run.call_args[0][0]
        assert result == "diff output"


def test_get_diff_with_commits():
    with patch("gac.git.run_subprocess") as mock_run:
        mock_run.return_value = "diff output"
        result = get_diff(commit1="abc123", commit2="def456")
        mock_run.assert_called_once()
        assert "diff" in mock_run.call_args[0][0]
        assert "abc123" in mock_run.call_args[0][0]
        assert "def456" in mock_run.call_args[0][0]
        assert result == "diff output"


def test_get_diff_single_commit():
    with patch("gac.git.run_subprocess") as mock_run:
        mock_run.return_value = "diff output"
        result = get_diff(commit1="abc123")
        mock_run.assert_called_once()
        assert "diff" in mock_run.call_args[0][0]
        assert "abc123" in mock_run.call_args[0][0]
        assert result == "diff output"


def test_run_pre_commit_hooks_no_config():
    """Test when .pre-commit-config.yaml doesn't exist."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = run_pre_commit_hooks()
        assert result is True


def test_run_pre_commit_hooks_pre_commit_not_installed():
    """Test when pre-commit is not installed."""
    with patch("os.path.exists") as mock_exists, patch("gac.git.run_subprocess") as mock_run:
        mock_exists.return_value = True
        mock_run.return_value = ""  # Empty result indicates pre-commit not available
        result = run_pre_commit_hooks()
        assert result is True


def test_run_pre_commit_hooks_success():
    """Test when pre-commit hooks pass successfully."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
    ):
        mock_exists.return_value = True
        mock_run.return_value = "pre-commit 3.0.0"  # pre-commit is available

        # Mock successful pre-commit run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_pre_commit_hooks()
        assert result is True


def test_run_pre_commit_hooks_failure_with_output():
    """Test when pre-commit hooks fail with detailed output."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_exists.return_value = True
        mock_run.return_value = "pre-commit 3.0.0"  # pre-commit is available

        # Mock failed pre-commit run with output
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "hook failed: some error details"
        mock_result.stderr = "stderr output"
        mock_subprocess_run.return_value = mock_result

        result = run_pre_commit_hooks()
        assert result is False
        mock_logger.error.assert_called_once()
        assert "Pre-commit hooks failed:" in mock_logger.error.call_args[0][0]
        assert "hook failed: some error details" in mock_logger.error.call_args[0][0]


def test_run_pre_commit_hooks_failure_no_output():
    """Test when pre-commit hooks fail without detailed output."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_exists.return_value = True
        mock_run.return_value = "pre-commit 3.0.0"  # pre-commit is available

        # Mock failed pre-commit run without output
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        result = run_pre_commit_hooks()
        assert result is False
        mock_logger.error.assert_called_once()
        assert "Pre-commit hooks failed with exit code 1" in mock_logger.error.call_args[0][0]


def test_run_pre_commit_hooks_exception_handling():
    """Test exception handling in run_pre_commit_hooks."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        mock_exists.return_value = True
        mock_run.return_value = "pre-commit 3.0.0"  # pre-commit is available
        mock_subprocess_run.side_effect = Exception("subprocess error")

        result = run_pre_commit_hooks()
        assert result is True  # Should return True on exception
        mock_logger.debug.assert_called_once()
        assert "Error running pre-commit:" in mock_logger.debug.call_args[0][0]


def test_run_lefthook_hooks_no_config():
    """Test when no Lefthook configuration files exist."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        result = run_lefthook_hooks()
        assert result is True


def test_run_lefthook_hooks_lefthook_not_installed():
    """Test when lefthook is not installed."""
    with patch("os.path.exists") as mock_exists, patch("gac.git.run_subprocess") as mock_run:
        # Mock that .lefthook.yml exists
        mock_exists.return_value = True
        mock_run.return_value = ""  # Empty result indicates lefthook not available
        result = run_lefthook_hooks()
        assert result is True


def test_run_lefthook_hooks_success():
    """Test when lefthook hooks pass successfully."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
    ):
        # Mock that .lefthook.yml exists
        mock_exists.return_value = True
        mock_run.return_value = "lefthook 1.0.0"  # lefthook is available

        # Mock successful lefthook run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_lefthook_hooks()
        assert result is True


def test_run_lefthook_hooks_failure_with_output():
    """Test when lefthook hooks fail with detailed output."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        # Mock that .lefthook.yml exists
        mock_exists.return_value = True
        mock_run.return_value = "lefthook 1.0.0"  # lefthook is available

        # Mock failed lefthook run with output
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "hook failed: some error details"
        mock_result.stderr = "stderr output"
        mock_subprocess_run.return_value = mock_result

        result = run_lefthook_hooks()
        assert result is False
        mock_logger.error.assert_called_once()
        assert "Lefthook hooks failed:" in mock_logger.error.call_args[0][0]
        assert "hook failed: some error details" in mock_logger.error.call_args[0][0]


def test_run_lefthook_hooks_failure_no_output():
    """Test when lefthook hooks fail without detailed output."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        # Mock that .lefthook.yml exists
        mock_exists.return_value = True
        mock_run.return_value = "lefthook 1.0.0"  # lefthook is available

        # Mock failed lefthook run without output
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        result = run_lefthook_hooks()
        assert result is False
        mock_logger.error.assert_called_once()
        assert "Lefthook hooks failed with exit code 1" in mock_logger.error.call_args[0][0]


def test_run_lefthook_hooks_exception_handling():
    """Test exception handling in run_lefthook_hooks."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
        patch("gac.git.logger") as mock_logger,
    ):
        # Mock that .lefthook.yml exists
        mock_exists.return_value = True
        mock_run.return_value = "lefthook 1.0.0"  # lefthook is available
        mock_subprocess_run.side_effect = Exception("subprocess error")

        result = run_lefthook_hooks()
        assert result is True  # Should return True on exception
        mock_logger.debug.assert_called_once()
        assert "Error running Lefthook:" in mock_logger.debug.call_args[0][0]


def test_run_lefthook_hooks_multiple_config_files():
    """Test when multiple Lefthook configuration files exist."""
    with (
        patch("os.path.exists") as mock_exists,
        patch("gac.git.run_subprocess") as mock_run,
        patch("subprocess.run") as mock_subprocess_run,
    ):
        # Mock that both .lefthook.yml and lefthook.yml exist
        def exists_side_effect(path):
            return path in [".lefthook.yml", "lefthook.yml"]

        mock_exists.side_effect = exists_side_effect
        mock_run.return_value = "lefthook 1.0.0"  # lefthook is available

        # Mock successful lefthook run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = run_lefthook_hooks()
        assert result is True
