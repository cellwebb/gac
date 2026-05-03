"""Integration tests for grouped commit staging/restore behavior.

These tests exercise the actual ``execute_grouped_commits`` and
``restore_staging`` code paths in a real git repo, verifying that:

- The staging area is properly saved and restored on failure.
- Partial commits don't leave the staging area in an inconsistent state.
- Dry-run mode doesn't touch the staging area at all.

Run with: ``uv run pytest tests/test_grouped_staging_integration.py -v``
"""

from __future__ import annotations

import os
import subprocess

import pytest

from gac.git import get_staged_files, run_git_command
from gac.grouped_commit_executor import GroupedCommitResult, execute_grouped_commits
from gac.workflow_utils import restore_staging


@pytest.fixture()
def git_repo_with_multiple_files(tmp_path):
    """Create a repo with several staged files suitable for grouped commits."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], check=True, capture_output=True)

    # Create and commit an initial file
    (tmp_path / "initial.txt").write_text("initial")
    subprocess.run(["git", "add", "initial.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], check=True, capture_output=True)

    # Create multiple new files and stage them
    (tmp_path / "feature.py").write_text("# feature code")
    (tmp_path / "test_feature.py").write_text("# test code")
    (tmp_path / "docs.md").write_text("# docs")
    subprocess.run(["git", "add", "feature.py", "test_feature.py", "docs.md"], check=True, capture_output=True)

    yield tmp_path
    os.chdir(cwd)


def _get_staged_snapshot() -> tuple[list[str], str]:
    """Capture current staging area state."""
    files = get_staged_files()
    diff = run_git_command(["diff", "--cached", "--binary"], silent=True).require_success()
    return files, diff


class TestRestoreStaging:
    """Verify restore_staging properly resets and re-stages."""

    def test_restore_preserves_staged_files(self, git_repo_with_multiple_files):
        original_files, original_diff = _get_staged_snapshot()
        assert len(original_files) == 3

        # Simulate what execute_grouped_commits does: unstage everything
        run_git_command(["reset", "HEAD"]).require_success()
        assert get_staged_files() == []

        # Now restore
        restore_staging(original_files, original_diff)
        restored_files = get_staged_files()
        assert set(restored_files) == set(original_files)

    def test_restore_after_partial_unstage(self, git_repo_with_multiple_files):
        original_files, original_diff = _get_staged_snapshot()

        # Unstage, then stage only one file (simulating a partial commit)
        run_git_command(["reset", "HEAD"]).require_success()
        run_git_command(["add", "feature.py"]).require_success()
        assert get_staged_files() == ["feature.py"]

        # Restore should bring back all three
        restore_staging(original_files, original_diff)
        restored_files = get_staged_files()
        assert set(restored_files) == set(original_files)

    def test_restore_with_empty_diff(self, git_repo_with_multiple_files):
        """Restore with no diff should still work via file list fallback."""
        original_files = get_staged_files()

        run_git_command(["reset", "HEAD"]).require_success()
        assert get_staged_files() == []

        # Restore without diff — uses file-by-file fallback
        restore_staging(original_files, staged_diff=None)
        restored_files = get_staged_files()
        assert set(restored_files) == set(original_files)


class TestDryRunPreservesStaging:
    """Verify dry-run mode doesn't modify the staging area."""

    def test_dry_run_does_not_commit(self, git_repo_with_multiple_files):
        original_files, original_diff = _get_staged_snapshot()
        commit_count_before = int(run_git_command(["rev-list", "--count", "HEAD"]).require_success())

        result = GroupedCommitResult(
            commits=[
                {"files": ["feature.py"], "message": "feat: add feature"},
                {"files": ["test_feature.py", "docs.md"], "message": "chore: tests and docs"},
            ],
            raw_response="...",
        )

        exit_code = execute_grouped_commits(
            result=result,
            dry_run=True,
            push=False,
            no_verify=True,
            hook_timeout=30,
        )

        assert exit_code == 0

        # Staging area should be unchanged
        assert set(get_staged_files()) == set(original_files)

        # No new commits
        commit_count_after = int(run_git_command(["rev-list", "--count", "HEAD"]).require_success())
        assert commit_count_after == commit_count_before


class TestGroupedCommitExecution:
    """Verify actual grouped commit execution and staging state."""

    def test_successful_execution_commits_all(self, git_repo_with_multiple_files):
        original_files, _ = _get_staged_snapshot()

        result = GroupedCommitResult(
            commits=[
                {"files": ["feature.py"], "message": "feat: add feature"},
                {"files": ["test_feature.py", "docs.md"], "message": "chore: tests and docs"},
            ],
            raw_response="...",
        )

        exit_code = execute_grouped_commits(
            result=result,
            dry_run=False,
            push=False,
            no_verify=True,
            hook_timeout=30,
        )

        assert exit_code == 0

        # Staging area should be clean after successful commits
        assert get_staged_files() == []

        # Two new commits (most recent first in git log)
        log_output = run_git_command(["log", "--oneline", "-3"]).require_success()
        lines = [line for line in log_output.splitlines() if line.strip()]
        assert len(lines) == 3  # initial + 2 new
        assert "tests and docs" in lines[0]
        assert "add feature" in lines[1]

    def test_failed_file_restores_remaining_staging(self, git_repo_with_multiple_files):
        """If a commit fails mid-way, remaining files should be restored to staging.

        Note: files that were successfully committed are no longer "changes",
        so they won't appear in the restored staging area. The restore ensures
        the uncommitted files are re-staged.
        """
        original_files, original_diff = _get_staged_snapshot()

        result = GroupedCommitResult(
            commits=[
                {"files": ["feature.py"], "message": "feat: add feature"},
                {"files": ["nonexistent_file.py"], "message": "chore: this will fail"},
            ],
            raw_response="...",
        )

        exit_code = execute_grouped_commits(
            result=result,
            dry_run=False,
            push=False,
            no_verify=True,
            hook_timeout=30,
        )

        assert exit_code == 1

        # The first commit (feature.py) succeeded, so it's committed.
        # The restore should re-stage the remaining files that were NOT committed.
        restored_files = get_staged_files()
        # feature.py was committed, so it shouldn't be staged anymore
        assert "feature.py" not in restored_files
        # The other two files should be restored
        assert "test_feature.py" in restored_files
        assert "docs.md" in restored_files

        # Only the first commit should have been created
        log_output = run_git_command(["log", "--oneline", "-3"]).require_success()
        lines = [line for line in log_output.splitlines() if line.strip()]
        assert len(lines) == 2  # initial + 1 successful commit
        assert "add feature" in lines[0]
