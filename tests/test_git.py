import subprocess

from gac.git import get_commit_hash, get_current_branch, get_repo_root


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
