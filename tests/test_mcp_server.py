"""Tests for gac.mcp.server helpers."""

from unittest.mock import patch

import pytest

from gac.mcp.models import CommitInfo, DiffStats, FileStat
from gac.mcp.server import (
    _check_git_repo,
    _extract_scope,
    _format_status_summary,
    _get_diff_stats,
    _get_file_status,
    _get_recent_commits,
    _stderr_console_redirect,
    _truncate_diff,
)


def test_stderr_console_redirect_patches_and_restores():
    """_stderr_console_redirect swaps module-level consoles to stderr and restores them."""
    import gac.commit_executor as _ce
    import gac.grouped_commit_workflow as _gcw
    import gac.workflow_utils as _wu

    orig_ce = _ce.console
    orig_gcw = _gcw.console
    orig_wu = _wu.console

    with _stderr_console_redirect():
        assert _ce.console is not orig_ce
        assert _gcw.console is not orig_gcw
        assert _wu.console is not orig_wu
        assert _ce.console.stderr is True

    assert _ce.console is orig_ce
    assert _gcw.console is orig_gcw
    assert _wu.console is orig_wu


# =============================================================================
# _extract_scope
# =============================================================================


class TestExtractScope:
    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("feat(auth): add login", "auth"),
            ("fix(api): handle timeout", "api"),
            ("chore(deps): bump versions", "deps"),
            ("fix: typo", ""),
            ("just a message", ""),
            ("", ""),
            ("  feat(auth): padded  ", "auth"),
            ("\n feat(core): newline padded", "core"),
        ],
        ids=[
            "conventional-with-scope",
            "fix-with-scope",
            "chore-with-scope",
            "no-scope",
            "no-convention",
            "empty",
            "whitespace-padded",
            "newline-padded",
        ],
    )
    def test_extract_scope(self, message: str, expected: str):
        assert _extract_scope(message) == expected

    def test_nested_parens_does_not_match(self):
        assert _extract_scope("feat(foo(bar)): msg") == ""


# =============================================================================
# _truncate_diff
# =============================================================================


class TestTruncateDiff:
    @pytest.mark.parametrize(
        ("diff", "max_lines", "expected_truncated"),
        [
            ("a\nb\nc", 5, False),
            ("a\nb\nc", 3, False),
            ("a\nb\nc\nd\ne\nf", 3, True),
            ("a\nb\nc", 0, False),
            ("a\nb\nc", -1, False),
            ("", 5, False),
        ],
        ids=[
            "shorter-than-max",
            "exact-match",
            "longer-than-max",
            "max-zero",
            "max-negative",
            "empty-diff",
        ],
    )
    def test_truncation_flag(self, diff: str, max_lines: int, expected_truncated: bool):
        _, was_truncated = _truncate_diff(diff, max_lines)
        assert was_truncated is expected_truncated

    def test_shorter_returns_original(self):
        diff = "line1\nline2"
        result, _ = _truncate_diff(diff, 10)
        assert result == diff

    def test_longer_returns_first_n_lines(self):
        diff = "a\nb\nc\nd\ne"
        result, was_truncated = _truncate_diff(diff, 3)
        assert result == "a\nb\nc"
        assert was_truncated is True

    def test_max_zero_returns_original(self):
        diff = "a\nb\nc"
        result, _ = _truncate_diff(diff, 0)
        assert result == diff

    def test_empty_diff(self):
        result, was_truncated = _truncate_diff("", 5)
        assert result == ""
        assert was_truncated is False


# =============================================================================
# _get_diff_stats
# =============================================================================


class TestGetDiffStats:
    def test_empty_diff(self):
        stats = _get_diff_stats("")
        assert stats.files_changed == 0
        assert stats.insertions == 0
        assert stats.deletions == 0
        assert stats.file_stats == []

    def test_single_file_insertions_and_deletions(self):
        diff = (
            "diff --git a/foo.py b/foo.py\n"
            "index abc..def 100644\n"
            "--- a/foo.py\n"
            "+++ b/foo.py\n"
            "@@ -1,3 +1,4 @@\n"
            " unchanged\n"
            "-old line\n"
            "+new line\n"
            "+added line\n"
        )
        stats = _get_diff_stats(diff)
        assert stats.files_changed == 1
        assert stats.insertions == 2
        assert stats.deletions == 1
        assert len(stats.file_stats) == 1
        assert stats.file_stats[0].file == "foo.py"
        assert stats.file_stats[0].insertions == 2
        assert stats.file_stats[0].deletions == 1

    def test_multiple_files(self):
        diff = (
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n"
            "+++ b/a.py\n"
            "+new in a\n"
            "diff --git a/b.py b/b.py\n"
            "--- a/b.py\n"
            "+++ b/b.py\n"
            "-removed from b\n"
            "+added to b\n"
        )
        stats = _get_diff_stats(diff)
        assert stats.files_changed == 2
        assert stats.insertions == 2
        assert stats.deletions == 1
        assert len(stats.file_stats) == 2
        assert stats.file_stats[0].file == "a.py"
        assert stats.file_stats[1].file == "b.py"

    def test_only_insertions(self):
        diff = "diff --git a/new.py b/new.py\n--- /dev/null\n+++ b/new.py\n+line1\n+line2\n"
        stats = _get_diff_stats(diff)
        assert stats.files_changed == 1
        assert stats.insertions == 2
        assert stats.deletions == 0

    def test_only_deletions(self):
        diff = "diff --git a/old.py b/old.py\n--- a/old.py\n+++ /dev/null\n-line1\n-line2\n-line3\n"
        stats = _get_diff_stats(diff)
        assert stats.files_changed == 1
        assert stats.insertions == 0
        assert stats.deletions == 3

    def test_per_file_stats(self):
        diff = "diff --git a/x.py b/x.py\n+add1\n+add2\n-del1\ndiff --git a/y.py b/y.py\n+add3\n"
        stats = _get_diff_stats(diff)
        assert stats.file_stats[0] == FileStat(file="x.py", insertions=2, deletions=1)
        assert stats.file_stats[1] == FileStat(file="y.py", insertions=1, deletions=0)


# =============================================================================
# _get_file_status
# =============================================================================


class TestGetFileStatus:
    @patch("gac.git.run_git_command")
    def test_staged_files(self, mock_git):
        mock_git.return_value = "M  src/app.py\nA  src/new.py\nD  src/old.py\nR  src/renamed.py"
        result = _get_file_status()
        assert "src/app.py" in result["staged"]
        assert "src/new.py" in result["staged"]
        assert "src/old.py" in result["staged"]
        assert "src/renamed.py" in result["staged"]
        assert len(result["staged"]) == 4

    @patch("gac.git.run_git_command")
    def test_unstaged_files(self, mock_git):
        mock_git.return_value = " M src/app.py\n A src/new.py\n D src/old.py"
        result = _get_file_status()
        assert "src/app.py" in result["unstaged"]
        assert "src/new.py" in result["unstaged"]
        assert "src/old.py" in result["unstaged"]

    @patch("gac.git.run_git_command")
    def test_untracked_files(self, mock_git):
        mock_git.return_value = "?? new_file.py\n?? another.txt"
        result = _get_file_status()
        assert "new_file.py" in result["untracked"]
        assert "another.txt" in result["untracked"]

    @patch("gac.git.run_git_command")
    def test_merge_conflicts(self, mock_git):
        mock_git.return_value = "UU conflict.py\nAA both_added.py\nDD both_deleted.py"
        result = _get_file_status()
        assert "conflict.py" in result["conflicts"]
        assert "both_added.py" in result["conflicts"]
        assert "both_deleted.py" in result["conflicts"]

    @patch("gac.git.run_git_command")
    def test_mixed_status(self, mock_git):
        mock_git.return_value = "M  staged.py\n M unstaged.py\n?? untracked.py\nUU conflict.py"
        result = _get_file_status()
        assert result["staged"] == ["staged.py"]
        assert result["unstaged"] == ["unstaged.py"]
        assert result["untracked"] == ["untracked.py"]
        assert result["conflicts"] == ["conflict.py"]

    @patch("gac.git.run_git_command")
    def test_exception_returns_empty(self, mock_git):
        mock_git.side_effect = RuntimeError("git failed")
        result = _get_file_status()
        assert result == {"staged": [], "unstaged": [], "untracked": [], "conflicts": []}

    @patch("gac.git.run_git_command")
    def test_empty_output(self, mock_git):
        mock_git.return_value = ""
        result = _get_file_status()
        assert result == {"staged": [], "unstaged": [], "untracked": [], "conflicts": []}


# =============================================================================
# _check_git_repo
# =============================================================================


class TestCheckGitRepo:
    @patch("gac.git.run_git_command")
    def test_success(self, mock_git):
        mock_git.return_value = "/some/repo"
        is_repo, error = _check_git_repo()
        assert is_repo is True
        assert error == ""

    @patch("gac.git.run_git_command")
    def test_failure(self, mock_git):
        mock_git.side_effect = RuntimeError("not a git repository")
        is_repo, error = _check_git_repo()
        assert is_repo is False
        assert "not a git repository" in error


# =============================================================================
# _get_recent_commits
# =============================================================================


class TestGetRecentCommits:
    @patch("gac.git.run_git_command")
    def test_normal_output(self, mock_git):
        mock_git.return_value = "abc1234|feat: add login|Alice|2 hours ago\ndef5678|fix: typo|Bob|1 day ago"
        commits = _get_recent_commits(2)
        assert len(commits) == 2
        assert commits[0].hash == "abc1234"
        assert commits[0].message == "feat: add login"
        assert commits[0].author == "Alice"
        assert commits[0].date == "2 hours ago"
        assert commits[1].hash == "def5678"

    @patch("gac.git.run_git_command")
    def test_empty_output(self, mock_git):
        mock_git.return_value = ""
        assert _get_recent_commits(5) == []

    @patch("gac.git.run_git_command")
    def test_malformed_lines_skipped(self, mock_git):
        mock_git.return_value = "abc|partial\nok1234|msg|author|3 days ago\nbad"
        commits = _get_recent_commits(3)
        assert len(commits) == 1
        assert commits[0].hash == "ok1234"

    @patch("gac.git.run_git_command")
    def test_exception_returns_empty(self, mock_git):
        mock_git.side_effect = RuntimeError("git log failed")
        assert _get_recent_commits(5) == []


# =============================================================================
# _format_status_summary
# =============================================================================


class TestFormatStatusSummary:
    def test_clean_repo(self):
        result = _format_status_summary(
            branch="main",
            is_clean=True,
            staged=[],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "clean" in result.lower()
        assert "main" in result
        assert "No changes to commit." in result

    def test_staged_summary_mode_groups_by_directory(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["src/a.py", "src/b.py", "docs/readme.md"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "STAGED (3 files)" in result
        assert "src/" in result
        assert "docs/" in result

    def test_staged_detailed_mode_lists_files(self):
        result = _format_status_summary(
            branch="dev",
            is_clean=False,
            staged=["src/a.py", "src/b.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="detailed",
        )
        assert "src/a.py" in result
        assert "src/b.py" in result

    def test_unstaged_truncation_in_summary(self):
        files = [f"file{i}.py" for i in range(8)]
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=files,
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "UNSTAGED (8 files)" in result
        assert "... and 3 more" in result

    def test_untracked_files(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=[],
            untracked=["new.py"],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "UNTRACKED (1 files)" in result

    def test_merge_conflicts(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=[],
            untracked=[],
            conflicts=["conflict.py"],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "MERGE CONFLICTS" in result
        assert "conflict.py" in result
        assert "Resolve conflicts before committing." in result

    def test_diff_stats_summary(self):
        stats = DiffStats(
            files_changed=2,
            insertions=10,
            deletions=3,
            file_stats=[
                FileStat(file="a.py", insertions=7, deletions=2),
                FileStat(file="b.py", insertions=3, deletions=1),
            ],
        )
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["a.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=stats,
            recent_commits=None,
            format_type="summary",
        )
        assert "2 file(s), +10 lines, -3 lines" in result
        assert "Per file:" not in result

    def test_diff_stats_detailed(self):
        stats = DiffStats(
            files_changed=1,
            insertions=5,
            deletions=2,
            file_stats=[FileStat(file="a.py", insertions=5, deletions=2)],
        )
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["a.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=stats,
            recent_commits=None,
            format_type="detailed",
        )
        assert "Per file:" in result
        assert "a.py: +5/-2" in result

    def test_recent_commits_with_long_message_truncation(self):
        long_msg = "a" * 60
        commits = [CommitInfo(hash="abc1234", message=long_msg, author="Alice", date="2 hours ago")]
        result = _format_status_summary(
            branch="main",
            is_clean=True,
            staged=[],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=commits,
            format_type="summary",
        )
        assert "RECENT COMMITS" in result
        assert "..." in result
        assert long_msg not in result

    def test_action_hint_ready_to_commit(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["file.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "Ready to commit" in result

    def test_action_hint_unstaged_changes(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=["file.py"],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "Stage changes" in result

    def test_root_files_in_summary_mode(self):
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["README.md", "setup.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "file(s) in root" in result
