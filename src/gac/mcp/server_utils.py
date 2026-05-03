"""Utility functions for the GAC MCP server.

Contains git introspection helpers, diff/stats parsing, and
status formatting used by the MCP tool handlers.
"""

from __future__ import annotations

import contextlib
import logging
import re
from collections.abc import Generator
from typing import NamedTuple

from rich.console import Console as RichConsole

from gac.mcp.models import CommitInfo, DiffStats, FileStat

logger = logging.getLogger(__name__)


# =============================================================================
# GIT INTROSPECTION
# =============================================================================


def _check_git_repo() -> tuple[bool, str]:
    """Check if we're in a git repository.

    Returns:
        Tuple of (is_repo, error_message)
    """
    try:
        from gac.git import run_git_command

        run_git_command(["rev-parse", "--show-toplevel"]).require_success()
        return True, ""
    except Exception as e:
        return False, str(e)


class FileStatus(NamedTuple):
    """Typed result from _get_file_status."""

    staged: list[str]
    unstaged: list[str]
    untracked: list[str]
    conflicts: list[str]
    error: str = ""


def _get_file_status() -> FileStatus:
    """Get file status categories (staged, unstaged, untracked, conflicts).

    Returns:
        A :class:`FileStatus` with file lists and an ``error`` field
        that is empty on success or a diagnostic message on failure.
        Consumers can check ``error`` to distinguish "no staged files"
        from "git failed".
    """
    try:
        from gac.git import run_git_command

        staged: list[str] = []
        unstaged: list[str] = []
        untracked: list[str] = []
        conflicts: list[str] = []

        # Get porcelain status
        status_output = run_git_command(["status", "--porcelain"]).require_success()

        for line in status_output.splitlines():
            if not line.strip():
                continue

            # Parse porcelain status (XY filename)
            xy = line[:2]
            filename = line[3:].strip()

            # X = index status, Y = worktree status
            index_status = xy[0]
            worktree_status = xy[1]

            # Check for conflicts
            if index_status in "U" or worktree_status in "U" or xy in ("AA", "DD"):
                conflicts.append(filename)
            elif index_status in "MADRC":
                staged.append(filename)
            elif worktree_status in "MAD":
                unstaged.append(filename)
            elif index_status == "?":
                untracked.append(filename)

        return FileStatus(staged=staged, unstaged=unstaged, untracked=untracked, conflicts=conflicts)
    except Exception as e:
        error_msg = str(e)
        logger.debug("git status --porcelain failed; returning empty file status", exc_info=True)
        return FileStatus(staged=[], unstaged=[], untracked=[], conflicts=[], error=error_msg)


def _get_diff_stats(diff_output: str) -> DiffStats:
    """Parse diff output to extract statistics."""
    files_changed = 0
    insertions = 0
    deletions = 0
    file_stats: list[FileStat] = []

    current_file = None
    file_insertions = 0
    file_deletions = 0

    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            # Save previous file stats
            if current_file:
                file_stats.append(
                    FileStat(
                        file=current_file,
                        insertions=file_insertions,
                        deletions=file_deletions,
                    )
                )
            # Start new file
            parts = line.split(" b/")
            current_file = parts[-1] if len(parts) > 1 else ""
            file_insertions = 0
            file_deletions = 0
            files_changed += 1
        elif line.startswith("+") and not line.startswith("+++"):
            insertions += 1
            file_insertions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
            file_deletions += 1

    # Save last file
    if current_file:
        file_stats.append(FileStat(file=current_file, insertions=file_insertions, deletions=file_deletions))

    return DiffStats(
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        file_stats=file_stats,
    )


class CommitListResult(NamedTuple):
    """Result from _get_recent_commits, distinguishing empty history from git failure."""

    commits: list[CommitInfo]
    error: str = ""


def _get_recent_commits(count: int) -> CommitListResult:
    """Get N most recent commits.

    Returns:
        A :class:`CommitListResult` with ``commits`` and an ``error`` field
        that is empty on success or contains a diagnostic on failure.
    """
    try:
        from gac.git import run_git_command

        # Format: hash|message|author|date
        format_str = "%h|%s|%an|%cr"
        output = run_git_command(["log", f"-{count}", f"--format={format_str}"]).require_success()

        commits: list[CommitInfo] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) >= 4:
                commits.append(
                    CommitInfo(
                        hash=parts[0],
                        message=parts[1],
                        author=parts[2],
                        date=parts[3],
                    )
                )
        return CommitListResult(commits=commits)
    except Exception as e:
        error_msg = str(e)
        logger.debug("git log --oneline failed; returning empty commit list", exc_info=True)
        return CommitListResult(commits=[], error=error_msg)


# =============================================================================
# TEXT UTILITIES
# =============================================================================


def _truncate_diff(diff: str, max_lines: int) -> tuple[str, bool]:
    """Truncate diff to max_lines, returning (truncated_diff, was_truncated)."""
    if max_lines <= 0:
        return diff, False

    lines = diff.splitlines()
    if len(lines) <= max_lines:
        return diff, False

    truncated = "\n".join(lines[:max_lines])
    return truncated, True


def _extract_scope(message: str) -> str:
    """Extract conventional commit scope from a message like 'feat(scope): ...'."""
    match = re.match(r"^\w+\(([^)]+)\):", message.strip())
    return match.group(1) if match else ""


# =============================================================================
# CONSOLE REDIRECTION
# =============================================================================


def _stderr_console_redirect() -> contextlib.AbstractContextManager[None]:
    """Context manager that redirects all Rich console output to stderr.

    MCP communicates over stdio (stdin/stdout).  Any writes to stdout from
    Rich's Console instances corrupt the JSON-RPC framing.  This patches the
    module-level ``console`` objects in every GAC module that prints during
    commit execution so their output goes to stderr instead.
    """

    @contextlib.contextmanager
    def _ctx() -> Generator[None, None, None]:
        import gac.commit_executor as _ce
        import gac.grouped_commit_workflow as _gcw
        import gac.workflow_utils as _wu

        stderr_con = RichConsole(stderr=True)
        saved = {_ce: _ce.console, _gcw: _gcw.console, _wu: _wu.console}  # type: ignore[attr-defined, unused-ignore]
        for mod in saved:
            mod.console = stderr_con  # type: ignore[attr-defined]
        try:
            yield
        finally:
            for mod, orig in saved.items():
                mod.console = orig  # type: ignore[attr-defined]

    return _ctx()


# =============================================================================
# STATUS FORMATTING
# =============================================================================


def _format_status_summary(
    branch: str,
    is_clean: bool,
    staged: list[str],
    unstaged: list[str],
    untracked: list[str],
    conflicts: list[str],
    diff_stats: DiffStats | None,
    recent_commits: list[CommitInfo] | None,
    format_type: str,
) -> str:
    """Generate a human-readable summary of repository status."""
    lines = []

    # Header with branch and state
    if is_clean:
        lines.append(f"✓ Repository is clean (branch: {branch})")
    else:
        lines.append(f"Branch: {branch}")

    # Conflict warning (always show first if present)
    if conflicts:
        lines.append("")
        lines.append(f"⚠️  MERGE CONFLICTS ({len(conflicts)} files):")
        for f in conflicts[:10]:
            lines.append(f"  • {f}")
        if len(conflicts) > 10:
            lines.append(f"  ... and {len(conflicts) - 10} more")

    # Staged files
    if staged:
        lines.append("")
        lines.append(f"📦 STAGED ({len(staged)} files):")
        if format_type == "detailed":
            for f in staged:
                lines.append(f"  • {f}")
        else:
            # Group by directory for summary
            dirs: dict[str, list[str]] = {}
            for f in staged:
                d = f.split("/")[0] if "/" in f else "."
                dirs[d] = dirs.get(d, []) + [f]
            for d, files in sorted(dirs.items())[:5]:
                if d == ".":
                    lines.append(f"  • {len(files)} file(s) in root")
                else:
                    lines.append(f"  • {d}/ ({len(files)} file(s))")
            if len(dirs) > 5:
                lines.append(f"  ... and {len(dirs) - 5} more directories")

    # Unstaged files
    if unstaged:
        lines.append("")
        lines.append(f"📝 UNSTAGED ({len(unstaged)} files):")
        if format_type == "detailed":
            for f in unstaged:
                lines.append(f"  • {f}")
        else:
            for f in unstaged[:5]:
                lines.append(f"  • {f}")
            if len(unstaged) > 5:
                lines.append(f"  ... and {len(unstaged) - 5} more")

    # Untracked files
    if untracked:
        lines.append("")
        lines.append(f"❓ UNTRACKED ({len(untracked)} files):")
        if format_type == "detailed":
            for f in untracked:
                lines.append(f"  • {f}")
        else:
            for f in untracked[:5]:
                lines.append(f"  • {f}")
            if len(untracked) > 5:
                lines.append(f"  ... and {len(untracked) - 5} more")

    # Diff stats
    if diff_stats and diff_stats.files_changed > 0:
        lines.append("")
        lines.append("📊 CHANGES:")
        lines.append(
            f"  {diff_stats.files_changed} file(s), +{diff_stats.insertions} lines, -{diff_stats.deletions} lines"
        )
        if format_type == "detailed" and diff_stats.file_stats:
            lines.append("  Per file:")
            for fs in diff_stats.file_stats[:10]:
                lines.append(f"    {fs.file}: +{fs.insertions}/-{fs.deletions}")
            if len(diff_stats.file_stats) > 10:
                lines.append(f"    ... and {len(diff_stats.file_stats) - 10} more")

    # Recent commits
    if recent_commits:
        lines.append("")
        lines.append(f"📜 RECENT COMMITS ({len(recent_commits)}):")
        for c in recent_commits:
            lines.append(f"  {c.hash} {c.message[:50]}{'...' if len(c.message) > 50 else ''}")
            lines.append(f"    by {c.author}, {c.date}")

    # Action hint
    lines.append("")
    if is_clean:
        lines.append("No changes to commit.")
    elif staged and not unstaged and not conflicts:
        lines.append("Ready to commit. Use gac_commit to create a commit.")
    elif conflicts:
        lines.append("Resolve conflicts before committing.")
    else:
        lines.append("Stage changes with git add, or use gac_commit(stage_all=True)")

    return "\n".join(lines)
