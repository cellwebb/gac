import subprocess
from unittest.mock import patch

from gac.git import get_commit_hash, get_current_branch, get_diff, get_repo_root


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
