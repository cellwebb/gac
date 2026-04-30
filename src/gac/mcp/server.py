"""FastMCP server for GAC - Git Auto Commit MCP Tools.

This module exposes GAC's commit generation capabilities to AI agents
through the Model Context Protocol using FastMCP.

Two primary tools:
    - gac_commit: Generate and optionally execute git commits
    - gac_status: Get repository status and diff information

Usage:
    gac serve            # Start MCP server (stdio transport)
    uvx gac serve        # Same, via uvx
"""

from __future__ import annotations

import contextlib
import logging
import re
from collections.abc import Generator

from mcp.server.fastmcp import FastMCP

from gac.mcp.models import (
    CommitInfo,
    CommitRequest,
    CommitResult,
    DiffStats,
    FileStat,
    GroupedCommit,
    StatusRequest,
    StatusResult,
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name="gac-mcp",
    instructions="Git Auto Commit (GAC) - AI-powered commit message generation for agents. "
    "Use gac_status to see repository state, then gac_commit to generate and execute commits.",
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def _check_git_repo() -> tuple[bool, str]:
    """Check if we're in a git repository.

    Returns:
        Tuple of (is_repo, error_message)
    """
    try:
        from gac.git import run_git_command

        run_git_command(["rev-parse", "--show-toplevel"])
        return True, ""
    except Exception as e:
        return False, str(e)


def _get_file_status() -> dict[str, list[str]]:
    """Get file status categories (staged, unstaged, untracked, conflicts)."""
    try:
        from gac.git import run_git_command

        result: dict[str, list[str]] = {
            "staged": [],
            "unstaged": [],
            "untracked": [],
            "conflicts": [],
        }

        # Get porcelain status
        status_output = run_git_command(["status", "--porcelain"])

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
                result["conflicts"].append(filename)
            elif index_status in "MADRC":
                result["staged"].append(filename)
            elif worktree_status in "MAD":
                result["unstaged"].append(filename)
            elif index_status == "?":
                result["untracked"].append(filename)

        return result
    except Exception:
        return {"staged": [], "unstaged": [], "untracked": [], "conflicts": []}


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


def _get_recent_commits(count: int) -> list[CommitInfo]:
    """Get N most recent commits."""
    try:
        from gac.git import run_git_command

        # Format: hash|message|author|date
        format_str = "%h|%s|%an|%cr"
        output = run_git_command(["log", f"-{count}", f"--format={format_str}"])

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
        return commits
    except Exception:
        return []


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


def _stderr_console_redirect() -> contextlib.AbstractContextManager[None]:
    """Context manager that redirects all Rich console output to stderr.

    MCP communicates over stdio (stdin/stdout).  Any writes to stdout from
    Rich's Console instances corrupt the JSON-RPC framing.  This patches the
    module-level ``console`` objects in every GAC module that prints during
    commit execution so their output goes to stderr instead.
    """
    from rich.console import Console as RichConsole

    @contextlib.contextmanager
    def _ctx() -> Generator[None, None, None]:
        import gac.commit_executor as _ce
        import gac.grouped_commit_workflow as _gcw
        import gac.workflow_utils as _wu

        stderr_con = RichConsole(stderr=True)
        saved = {_ce: _ce.console, _gcw: _gcw.console, _wu: _wu.console}
        for mod in saved:
            mod.console = stderr_con  # type: ignore[attr-defined]
        try:
            yield
        finally:
            for mod, orig in saved.items():
                mod.console = orig  # type: ignore[attr-defined]

    return _ctx()


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


# =============================================================================
# MCP TOOLS
# =============================================================================


@mcp.tool()
def gac_status(request: StatusRequest) -> StatusResult:
    """Get comprehensive git repository status.

    This is your "vision" tool - use it to understand repository state before
    making commits. It provides information about staged, unstaged, and untracked
    files, along with optional diff content and commit history.

    WHEN TO USE:
    - Before calling gac_commit to understand what will be committed
    - To check if there are any merge conflicts
    - To see recent commit history and patterns
    - To review diff content before committing

    PARAMETERS:
    - format: Output format ('summary', 'detailed', 'json')
        - 'summary': Clean human-readable output (default)
        - 'detailed': Shows all file names and per-file stats
        - 'json': Raw data for programmatic use
    - include_diff: Set True to see the full diff content
    - include_stats: Set True to see line change statistics
    - include_history: Set N > 0 to include N most recent commits
    - staged_only: Set True to only show staged changes in diff
    - include_untracked: Set False to exclude untracked files
    - max_diff_lines: Maximum diff lines to include (default 500)

    WORKFLOW:
    1. Call gac_status() to see what files changed
    2. Call gac_status(include_diff=True) to understand the changes
    3. Call gac_commit() with appropriate parameters

    RETURNS:
    StatusResult with 'summary' field containing formatted output.
    Use the summary field for clean, readable output in agents.

    EXAMPLE:
        # Basic status check
        status = gac_status(StatusRequest())

        # Full context before committing
        status = gac_status(StatusRequest(
            include_diff=True,
            include_stats=True,
            include_history=5
        ))
    """
    # Check if we're in a git repo
    is_repo, error = _check_git_repo()
    if not is_repo:
        return StatusResult(
            branch="",
            is_clean=False,
            is_repo=False,
            summary=f"❌ Not in a git repository: {error}",
            error=f"Not in a git repository: {error}",
        )

    try:
        from gac.git import get_current_branch, run_git_command

        # Get basic status
        branch = get_current_branch()
        file_status = _get_file_status()

        staged = file_status["staged"]
        unstaged = file_status["unstaged"]
        untracked = file_status["untracked"] if request.include_untracked else []
        conflicts = file_status["conflicts"]

        # Determine if clean
        is_clean = not staged and not unstaged and (not untracked or not request.include_untracked) and not conflicts

        # Get diff if requested
        diff_output: str | None = None
        diff_stats: DiffStats | None = None
        diff_truncated = False

        if request.include_diff:
            diff_args = ["diff"]
            if request.staged_only:
                diff_args.append("--cached")
            else:
                diff_args.append("HEAD")

            raw_diff = run_git_command(diff_args)
            diff_output, diff_truncated = _truncate_diff(raw_diff, request.max_diff_lines)

            # Include stats
            if request.include_stats:
                diff_stats = _get_diff_stats(raw_diff)

        # Get history if requested
        recent_commits = None
        if request.include_history > 0:
            recent_commits = _get_recent_commits(request.include_history)

        # Generate formatted summary
        summary = _format_status_summary(
            branch=branch,
            is_clean=is_clean,
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            conflicts=conflicts,
            diff_stats=diff_stats,
            recent_commits=recent_commits,
            format_type=request.format,
        )

        # Add diff to summary if included
        if diff_output:
            summary += f"\n\n{'─' * 40}\nDIFF:\n{'─' * 40}\n{diff_output}"
            if diff_truncated:
                summary += f"\n\n... (diff truncated at {request.max_diff_lines} lines)"

        return StatusResult(
            branch=branch,
            is_clean=is_clean,
            is_repo=True,
            summary=summary,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            conflicts=conflicts,
            diff=diff_output,
            diff_stats=diff_stats,
            recent_commits=recent_commits,
            diff_truncated=diff_truncated,
        )

    except Exception as e:
        logger.exception("Error getting git status")
        return StatusResult(
            branch="",
            is_clean=False,
            is_repo=True,
            summary=f"❌ Error getting git status: {e}",
            error=str(e),
        )


@mcp.tool()
def gac_commit(request: CommitRequest) -> CommitResult:
    """Generate and optionally execute a git commit using AI.

    This is your "action" tool - use it to create commit messages and execute
    commits. GAC analyzes staged changes and generates conventional commit
    messages using the configured AI model.

    WHEN TO USE:
    - You need to commit changes to a git repository
    - You want AI-generated commit messages following best practices
    - You need to stage, commit, and optionally push in one operation

    IMPORTANT WORKFLOW:
    1. Call gac_status() FIRST to understand repository state
    2. If no staged files, either stage them first or use stage_all=True
    3. Use dry_run=True to preview before executing
    4. Use message_only=True to get just the message without committing
    5. Use auto_confirm=True for non-interactive agent workflows

    KEY PARAMETERS:
    - stage_all: Stage all changes (equivalent to git add -A)
    - group: Split changes into multiple logical commits (AI-driven grouping)
    - dry_run: Preview what would happen without committing
    - message_only: Generate message without committing (NO commit is made!)
    - push: Push to remote after successful commit
    - hint: Additional context for better commit messages
    - auto_confirm: Skip confirmation prompts (REQUIRED for agents)

    GROUP MODE (group=True):
    When group=True the AI analyzes all staged changes and groups them into
    multiple logical commits. Each group gets its own message. The result
    includes a 'grouped_commits' list with scope, files, and suggested_message
    for each group. Use with dry_run=True or message_only=True to preview the
    groupings before committing.

    COMMIT MESSAGE OPTIONS:
    - one_liner: Single-line message (no body)
    - scope: Conventional commit scope (e.g., 'auth', 'api')
    - language: Commit message language (e.g., 'Spanish', 'zh-CN')

    SAFETY OPTIONS:
    - skip_secret_scan: Skip security scan (use with caution)
    - no_verify: Skip pre-commit hooks

    RETURNS:
    CommitResult with success status, message, hash, and files changed.
    When message_only=True or dry_run=True, commit_hash will be None.

    EXAMPLES:
        # Preview a commit
        result = gac_commit(CommitRequest(
            stage_all=True,
            dry_run=True
        ))

        # Quick commit with push
        result = gac_commit(CommitRequest(
            stage_all=True,
            push=True,
            auto_confirm=True
        ))

        # Get message only for review (NO commit is made)
        result = gac_commit(CommitRequest(
            message_only=True
        ))

        # Commit with context hint
        result = gac_commit(CommitRequest(
            hint="Fixes login bug reported in issue #123",
            auto_confirm=True
        ))

        # Preview grouped commits (no commits created)
        result = gac_commit(CommitRequest(
            stage_all=True,
            group=True,
            dry_run=True
        ))

        # Execute grouped commits
        result = gac_commit(CommitRequest(
            group=True,
            auto_confirm=True
        ))
    """
    # Check if we're in a git repo
    is_repo, error = _check_git_repo()
    if not is_repo:
        return CommitResult(
            success=False,
            commit_message="",
            error=f"Not in a git repository: {error}",
        )

    try:
        from gac.ai import generate_commit_message
        from gac.config import load_config
        from gac.git import get_staged_files, run_git_command
        from gac.git_state_validator import GitStateValidator
        from gac.postprocess import clean_commit_message
        from gac.prompt_builder import PromptBuilder

        # Load configuration
        config = load_config()

        # Determine model
        model = request.model or config.get("model")
        if not model:
            return CommitResult(
                success=False,
                commit_message="",
                error="No model configured. Run 'gac init' or provide model parameter.",
            )

        # Stage files if requested
        # NOTE: We stage even for dry_run/message_only to see what WOULD be committed
        if request.stage_all:
            run_git_command(["add", "--all"])

        # Get staged files
        staged_files = get_staged_files(existing_only=False)

        if not staged_files:
            return CommitResult(
                success=False,
                commit_message="",
                files_changed=[],
                error="No staged changes found. Use stage_all=True or stage files manually.",
            )

        # Get git state for prompt building
        validator = GitStateValidator(config)
        git_state = validator.get_git_state(
            stage_all=False,  # Already staged above
            dry_run=True,  # Always dry run for state collection
            skip_secret_scan=request.skip_secret_scan,
            quiet=True,
            model=model,
            hint=request.hint,
            one_liner=request.one_liner,
            infer_scope=request.scope is None,
            verbose=False,
            language=request.language,
        )

        if not git_state:
            return CommitResult(
                success=False,
                commit_message="",
                files_changed=staged_files,
                error="Failed to get git state. Ensure there are staged changes.",
            )

        # Collect warnings
        warnings: list[str] = []
        if git_state.has_secrets and not request.skip_secret_scan:
            warnings.append("⚠️ Potential secrets detected in staged changes. Review carefully before committing.")

        # Get generation config
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_output_tokens", 1000)
        max_retries = config.get("max_retries", 3)

        prompt_builder = PromptBuilder(config)

        # =====================================================================
        # GROUP MODE: split staged changes into multiple logical commits
        # =====================================================================
        if request.group:
            from gac.grouped_commit_workflow import GroupedCommitWorkflow

            workflow = GroupedCommitWorkflow(config)

            # Scale output tokens proportionally to number of files being grouped
            num_files = len(staged_files)
            token_multiplier = min(5, 2 + (num_files // 10))
            group_max_tokens = int(max_tokens) * token_multiplier

            # Build group-aware prompts
            group_bundle = prompt_builder.build_prompts(
                git_state=git_state,
                group=True,
                hint=request.hint,
                one_liner=request.one_liner,
                infer_scope=request.scope is None,
                language=request.language,
            )

            group_conversation: list[dict[str, str]] = []
            if group_bundle.system_prompt:
                group_conversation.append({"role": "system", "content": group_bundle.system_prompt})
            group_conversation.append({"role": "user", "content": group_bundle.user_prompt})

            # Generate grouped commits (no interactive confirmation for MCP)
            group_result = workflow.generate_grouped_commits_with_retry(
                model=model,
                conversation_messages=group_conversation,
                temperature=temperature,
                max_output_tokens=group_max_tokens,
                max_retries=max_retries,
                quiet=True,
                staged_files_set=set(staged_files),
                require_confirmation=False,
            )

            if isinstance(group_result, int):
                return CommitResult(
                    success=False,
                    commit_message="",
                    files_changed=staged_files,
                    error="Failed to generate grouped commits. The AI model could not produce valid groupings.",
                    warnings=warnings,
                )

            grouped_commits = [
                GroupedCommit(
                    scope=_extract_scope(commit["message"]),
                    files=commit["files"],
                    suggested_message=commit["message"].strip(),
                )
                for commit in group_result.commits
            ]

            num_groups = len(grouped_commits)

            # ── message_only: return grouped suggestions, don't commit ──────
            if request.message_only:
                return CommitResult(
                    success=True,
                    commit_message=f"[{num_groups} grouped commits]",
                    grouped_commits=grouped_commits,
                    files_changed=staged_files,
                    warnings=warnings + [f"ℹ️ message_only=True: {num_groups} commit groups generated, none created."],
                )

            # ── dry_run: return grouped suggestions, don't commit ───────────
            if request.dry_run:
                return CommitResult(
                    success=True,
                    commit_message=f"[{num_groups} grouped commits]",
                    grouped_commits=grouped_commits,
                    files_changed=staged_files,
                    warnings=warnings + [f"ℹ️ dry_run=True: {num_groups} commit groups generated, none created."],
                )

            # ── execute all grouped commits ──────────────────────────────────
            with _stderr_console_redirect():
                exit_code = workflow.execute_grouped_commits(
                    result=group_result,
                    dry_run=False,
                    push=request.push,
                    no_verify=request.no_verify,
                    hook_timeout=120,
                    model=model,
                )

            if exit_code != 0:
                return CommitResult(
                    success=False,
                    commit_message="",
                    files_changed=staged_files,
                    grouped_commits=grouped_commits,
                    error="One or more grouped commits failed. Staging area has been restored.",
                    warnings=warnings,
                )

            return CommitResult(
                success=True,
                commit_message=f"[{num_groups} grouped commits]",
                grouped_commits=grouped_commits,
                files_changed=staged_files,
                warnings=warnings,
            )

        # =====================================================================
        # SINGLE COMMIT MODE (default)
        # =====================================================================
        prompt_bundle = prompt_builder.build_prompts(
            git_state=git_state,
            hint=request.hint,
            one_liner=request.one_liner,
            infer_scope=request.scope is None,
            language=request.language,
        )

        # Build conversation messages
        conversation_messages: list[dict[str, str]] = []
        if prompt_bundle.system_prompt:
            conversation_messages.append({"role": "system", "content": prompt_bundle.system_prompt})
        conversation_messages.append({"role": "user", "content": prompt_bundle.user_prompt})

        # Generate commit message using AI
        from gac.stats import record_tokens

        raw_commit_message, prov_pt, prov_ct, duration_ms, _reasoning_tokens = generate_commit_message(
            model=model,
            prompt=conversation_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            quiet=True,
        )
        record_tokens(prov_pt, prov_ct, model=model, duration_ms=duration_ms, reasoning_tokens=_reasoning_tokens)
        commit_message = clean_commit_message(raw_commit_message)

        if not commit_message:
            return CommitResult(
                success=False,
                commit_message="",
                files_changed=staged_files,
                error="Failed to generate commit message. Check AI model configuration.",
            )

        # ── message_only: return message, don't commit ───────────────────────
        if request.message_only:
            return CommitResult(
                success=True,
                commit_message=commit_message,
                commit_hash=None,  # No commit was made
                files_changed=staged_files,
                warnings=warnings + ["ℹ️ message_only=True: No commit was created."],
            )

        # ── dry_run: return message, don't commit ────────────────────────────
        if request.dry_run:
            return CommitResult(
                success=True,
                commit_message=commit_message,
                commit_hash=None,  # No commit was made
                files_changed=staged_files,
                warnings=warnings + ["ℹ️ dry_run=True: No commit was created."],
            )

        # ── execute commit ───────────────────────────────────────────────────
        from gac.commit_executor import CommitExecutor

        executor = CommitExecutor(
            dry_run=False,
            quiet=True,
            no_verify=request.no_verify,
            hook_timeout=120,
        )
        with _stderr_console_redirect():
            executor.create_commit(commit_message)

        # Record stats (create_commit no longer tracks stats internally)
        from gac.stats import record_commit, record_gac

        record_commit()
        record_gac(model=model)

        # Get commit hash
        commit_hash = run_git_command(["rev-parse", "HEAD"])[:7]

        # Push if requested
        if request.push:
            with _stderr_console_redirect():
                executor.push_to_remote()

        return CommitResult(
            success=True,
            commit_message=commit_message,
            commit_hash=commit_hash,
            files_changed=staged_files,
            warnings=warnings,
        )

    except Exception as e:
        logger.exception("Error in commit workflow")
        return CommitResult(
            success=False,
            commit_message="",
            error=str(e),
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main() -> None:
    """Main entry point for the GAC MCP server."""
    # Run the FastMCP server with stdio transport (default for agents)
    mcp.run()


if __name__ == "__main__":
    main()
