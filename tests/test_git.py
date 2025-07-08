import subprocess
from unittest.mock import patch

from gac.git import get_commit_hash, get_current_branch, get_diff, get_repo_root, get_unstaged_files


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


def test_get_unstaged_files_with_untracked():
    with patch("gac.git.run_git_command") as mock_run:
        # Mock the two git commands that get_unstaged_files calls
        mock_run.side_effect = [
            "file1.txt\nfile2.py",  # git diff --name-only
            "untracked1.txt\nuntracked2.py",  # git ls-files --others --exclude-standard
        ]
        result = get_unstaged_files(include_untracked=True)
        assert result == ["file1.txt", "file2.py", "untracked1.txt", "untracked2.py"]
        assert mock_run.call_count == 2


def test_get_unstaged_files_without_untracked():
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.return_value = "file1.txt\nfile2.py"
        result = get_unstaged_files(include_untracked=False)
        assert result == ["file1.txt", "file2.py"]
        mock_run.assert_called_once_with(["diff", "--name-only"])


def test_get_unstaged_files_empty():
    with patch("gac.git.run_git_command") as mock_run:
        mock_run.side_effect = ["", ""]  # No modified files, no untracked files
        result = get_unstaged_files(include_untracked=True)
        assert result == []
        assert mock_run.call_count == 2


def test_get_unstaged_files_git_error():
    from gac.errors import GitError

    with patch("gac.git.run_git_command") as mock_run:
        mock_run.side_effect = GitError("Git command failed")
        result = get_unstaged_files(include_untracked=True)
        assert result == []  # Should return empty list on error
