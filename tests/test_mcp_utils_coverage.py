"""Coverage tests for mcp/server_utils.py — targeting uncovered format_status branches and edge cases."""

from gac.mcp.models import CommitInfo, DiffStats, FileStat
from gac.mcp.server_utils import (
    _format_status_summary,
    _get_diff_stats,
)

# ---------------------------------------------------------------------------
# _format_status_summary — uncovered branches
# ---------------------------------------------------------------------------


class TestFormatStatusSummaryEdgeCases:
    def test_many_conflicts_more_than_10(self):
        """More than 10 conflicts shows truncation."""
        conflicts = [f"conflict_{i}.py" for i in range(15)]
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=[],
            untracked=[],
            conflicts=conflicts,
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "MERGE CONFLICTS (15 files)" in result
        assert "... and 5 more" in result

    def test_many_directories_more_than_5_in_summary(self):
        """More than 5 directories in summary shows truncation."""
        staged = [f"dir{i}/file.py" for i in range(8)]
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=staged,
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "... and 3 more directories" in result

    def test_unstaged_detailed_mode(self):
        """Unstaged files in detailed mode list all files."""
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=["a.py", "b.py"],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="detailed",
        )
        assert "UNSTAGED (2 files)" in result
        assert "a.py" in result
        assert "b.py" in result

    def test_untracked_detailed_mode(self):
        """Untracked files in detailed mode list all files."""
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=[],
            untracked=["new1.py", "new2.py"],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="detailed",
        )
        assert "UNTRACKED (2 files)" in result
        assert "new1.py" in result
        assert "new2.py" in result

    def test_untracked_summary_truncation(self):
        """Untracked files in summary mode truncates to 5."""
        untracked = [f"new_{i}.py" for i in range(8)]
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=[],
            unstaged=[],
            untracked=untracked,
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "UNTRACKED (8 files)" in result
        assert "... and 3 more" in result

    def test_diff_stats_more_than_10_file_stats(self):
        """More than 10 file stats in detailed shows truncation."""
        file_stats = [FileStat(file=f"file_{i}.py", insertions=i, deletions=i) for i in range(15)]
        stats = DiffStats(files_changed=15, insertions=100, deletions=50, file_stats=file_stats)
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["file_0.py"],
            unstaged=[],
            untracked=[],
            conflicts=[],
            diff_stats=stats,
            recent_commits=None,
            format_type="detailed",
        )
        assert "Per file:" in result
        assert "... and 5 more" in result

    def test_recent_commits_short_message(self):
        """Recent commits with short message (no truncation)."""
        commits = [CommitInfo(hash="abc1234", message="short msg", author="Bob", date="1 hour ago")]
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
        assert "short msg" in result
        assert "..." not in result  # no truncation needed

    def test_mixed_staged_and_unstaged_action_hint(self):
        """Both staged and unstaged gives 'Stage changes' hint."""
        result = _format_status_summary(
            branch="main",
            is_clean=False,
            staged=["a.py"],
            unstaged=["b.py"],
            untracked=[],
            conflicts=[],
            diff_stats=None,
            recent_commits=None,
            format_type="summary",
        )
        assert "Stage changes" in result


# ---------------------------------------------------------------------------
# _get_diff_stats — edge cases
# ---------------------------------------------------------------------------


class TestGetDiffStatsEdgeCases:
    def test_empty_diff(self):
        """Empty diff returns zero stats."""
        stats = _get_diff_stats("")
        assert stats.files_changed == 0
        assert stats.insertions == 0
        assert stats.deletions == 0

    def test_diff_with_only_additions(self):
        """Diff with only added lines."""
        diff = "diff --git a/new.py b/new.py\n+new line 1\n+new line 2\n"
        stats = _get_diff_stats(diff)
        assert stats.files_changed == 1
        assert stats.insertions == 2
        assert stats.deletions == 0

    def test_diff_ignores_file_headers(self):
        """+++ and --- headers are not counted as additions/deletions."""
        diff = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n+actual addition\n-actual deletion\n"
        stats = _get_diff_stats(diff)
        assert stats.insertions == 1
        assert stats.deletions == 1
