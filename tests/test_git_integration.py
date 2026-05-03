"""Integration tests that exercise git commands in a real temp repository.

These tests verify actual failure modes — not a git repo, corrupted index,
missing refs — using the real ``git`` binary rather than mocks.

Run with: ``uv run pytest tests/test_git_integration.py -v``
"""

from __future__ import annotations

import os
import subprocess

import pytest

from gac.errors import GitError
from gac.git import (
    get_commit_hash,
    get_current_branch,
    get_repo_root,
    get_staged_files,
    get_staged_status,
    run_git_command,
)


@pytest.fixture()
def git_repo(tmp_path):
    """Create a minimal git repo with one committed file."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], check=True, capture_output=True)
    (tmp_path / "hello.txt").write_text("hello")
    subprocess.run(["git", "add", "hello.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], check=True, capture_output=True)
    yield tmp_path
    os.chdir(cwd)


@pytest.fixture()
def non_git_dir(tmp_path):
    """A temp directory that is NOT a git repo."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


# ── Risk 3: Live git failure modes ──────────────────────────────────────────


class TestNotAGitRepo:
    """Verify that running git commands outside a repo raises GitError."""

    def test_get_repo_root_raises(self, non_git_dir):
        with pytest.raises(GitError, match="repo root"):
            get_repo_root()

    def test_get_current_branch_raises(self, non_git_dir):
        with pytest.raises(GitError, match="current branch"):
            get_current_branch()

    def test_get_commit_hash_raises(self, non_git_dir):
        with pytest.raises(GitError, match="commit hash"):
            get_commit_hash()

    def test_get_staged_files_raises(self, non_git_dir):
        with pytest.raises(GitError, match="staged files"):
            get_staged_files()

    def test_get_staged_status_raises(self, non_git_dir):
        with pytest.raises(GitError, match="staged status"):
            get_staged_status()

    def test_run_git_command_returns_fail(self, non_git_dir):
        result = run_git_command(["rev-parse", "--show-toplevel"])
        assert not result.success
        assert result.returncode == 128
        assert "not a git repository" in result.stderr.lower()

    def test_require_success_raises_with_stderr(self, non_git_dir):
        result = run_git_command(["rev-parse", "--show-toplevel"])
        with pytest.raises(GitError, match="not a git repository"):
            result.require_success()


class TestHappyPathInRepo:
    """Verify basic operations succeed in a real repo."""

    def test_get_repo_root(self, git_repo):
        root = get_repo_root()
        assert root == str(git_repo)

    def test_get_current_branch(self, git_repo):
        branch = get_current_branch()
        # Could be main or master depending on git config
        assert branch in ("main", "master")

    def test_get_commit_hash(self, git_repo):
        h = get_commit_hash()
        assert len(h) == 40

    def test_get_staged_files_empty(self, git_repo):
        files = get_staged_files()
        assert files == []

    def test_get_staged_status_fallback(self, git_repo):
        status = get_staged_status()
        assert status == "No changes staged for commit."

    def test_run_git_command_success(self, git_repo):
        result = run_git_command(["status", "--porcelain"])
        assert result.success
        assert result.output == ""


class TestStagedFilesDetection:
    """Verify get_staged_files distinguishes staged from unstaged from failure."""

    def test_staged_file_detected(self, git_repo):
        (git_repo / "new.py").write_text("print('hi')")
        subprocess.run(["git", "add", "new.py"], check=True, capture_output=True)
        files = get_staged_files()
        assert "new.py" in files

    def test_unstaged_file_not_in_staged(self, git_repo):
        (git_repo / "unstaged.py").write_text("x = 1")
        # Don't git add — it's unstaged
        files = get_staged_files()
        assert "unstaged.py" not in files

    def test_deleted_staged_file(self, git_repo):
        (git_repo / "gone.txt").write_text("bye")
        subprocess.run(["git", "add", "gone.txt"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add gone"], check=True, capture_output=True)
        os.remove(git_repo / "gone.txt")
        subprocess.run(["git", "add", "gone.txt"], check=True, capture_output=True)
        files = get_staged_files()
        assert "gone.txt" in files


class TestCorruptedGitState:
    """Test behavior when git state is unusual."""

    def test_detached_head_still_works(self, git_repo):
        """Detached HEAD shouldn't crash get_current_branch."""
        h = get_commit_hash()
        subprocess.run(["git", "checkout", h], check=True, capture_output=True)
        # In detached HEAD, rev-parse --abbrev-ref HEAD returns "HEAD"
        branch = get_current_branch()
        assert branch == "HEAD"

    def test_empty_repo_commit_hash_raises(self, tmp_path):
        """A repo with no commits should fail get_commit_hash."""
        cwd = os.getcwd()
        os.chdir(tmp_path)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], check=True, capture_output=True)
        try:
            with pytest.raises(GitError, match="commit hash"):
                get_commit_hash()
        finally:
            os.chdir(cwd)
