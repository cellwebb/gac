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

import logging

from mcp.server.fastmcp import FastMCP

from gac.mcp.models import (
    CommitRequest,
    CommitResult,
    DiffStats,
    GroupedCommit,
    StatusRequest,
    StatusResult,
)
from gac.mcp.server_utils import (
    _check_git_repo,
    _extract_scope,
    _format_status_summary,
    _get_diff_stats,
    _get_file_status,
    _get_recent_commits,
    _stderr_console_redirect,
    _truncate_diff,
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

        staged = file_status.staged
        unstaged = file_status.unstaged
        untracked = file_status.untracked if request.include_untracked else []
        conflicts = file_status.conflicts
        status_error = file_status.error

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

            raw_diff = run_git_command(diff_args).require_success()
            diff_output, diff_truncated = _truncate_diff(raw_diff, request.max_diff_lines)

            # Include stats
            if request.include_stats:
                diff_stats = _get_diff_stats(raw_diff)

        # Get history if requested
        recent_commits = None
        if request.include_history > 0:
            commit_result = _get_recent_commits(request.include_history)
            recent_commits = commit_result.commits
            if commit_result.error:
                status_error = (
                    f"{status_error}; {commit_result.error}".strip("; ") if status_error else commit_result.error
                )

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
            error=status_error or None,
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
        # Preview: CommitRequest(stage_all=True, dry_run=True)
        # Quick commit: CommitRequest(stage_all=True, push=True, auto_confirm=True)
        # Message only: CommitRequest(message_only=True)
        # With hint: CommitRequest(hint="Fixes issue #123", auto_confirm=True)
        # Group preview: CommitRequest(stage_all=True, group=True, dry_run=True)
        # Group execute: CommitRequest(group=True, auto_confirm=True)
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
        from gac.stats import reset_gac_token_accumulator

        # Reset accumulator at the start of every request so stale tokens from
        # a failed previous request can never leak into this one.
        reset_gac_token_accumulator()

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
            run_git_command(["add", "--all"]).require_success()

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
            stage_all=False,
            dry_run=True,
            skip_secret_scan=request.skip_secret_scan,
            quiet=True,
            model=model,
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

            if not group_result.success:
                reset_gac_token_accumulator()  # Don't leak tokens into next request
                return CommitResult(
                    success=False,
                    commit_message="",
                    files_changed=staged_files,
                    error="Failed to generate grouped commits. The AI model could not produce valid groupings.",
                    warnings=warnings,
                )

            commit_data = group_result.result
            assert commit_data is not None

            grouped_commits = [
                GroupedCommit(
                    scope=_extract_scope(commit["message"]),
                    files=commit["files"],
                    suggested_message=commit["message"].strip(),
                )
                for commit in commit_data.commits
            ]

            num_groups = len(grouped_commits)

            # ── message_only: return grouped suggestions, don't commit ──────
            if request.message_only:
                reset_gac_token_accumulator()  # Don't leak tokens into next request
                return CommitResult(
                    success=True,
                    commit_message=f"[{num_groups} grouped commits]",
                    grouped_commits=grouped_commits,
                    files_changed=staged_files,
                    warnings=warnings + [f"ℹ️ message_only=True: {num_groups} commit groups generated, none created."],
                )

            # ── dry_run: return grouped suggestions, don't commit ───────────
            if request.dry_run:
                reset_gac_token_accumulator()  # Don't leak tokens into next request
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
                    result=commit_data,
                    dry_run=False,
                    push=request.push,
                    no_verify=request.no_verify,
                    hook_timeout=120,
                    model=model,
                )

            if exit_code != 0:
                reset_gac_token_accumulator()  # Don't leak tokens into next request
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
            reset_gac_token_accumulator()  # Don't leak tokens into next request
            return CommitResult(
                success=False,
                commit_message="",
                files_changed=staged_files,
                error="Failed to generate commit message. Check AI model configuration.",
            )

        # ── message_only: return message, don't commit ───────────────────────
        if request.message_only:
            reset_gac_token_accumulator()  # Don't leak tokens into next request
            return CommitResult(
                success=True,
                commit_message=commit_message,
                commit_hash=None,  # No commit was made
                files_changed=staged_files,
                warnings=warnings + ["ℹ️ message_only=True: No commit was created."],
            )

        # ── dry_run: return message, don't commit ────────────────────────────
        if request.dry_run:
            reset_gac_token_accumulator()  # Don't leak tokens into next request
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
        commit_hash = run_git_command(["rev-parse", "HEAD"]).require_success()[:7]

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
        reset_gac_token_accumulator()  # Don't leak tokens into next request
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
