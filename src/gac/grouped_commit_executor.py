"""Execute grouped commits with staging-area save/restore.

This module handles the mechanics of turning a ``GroupedCommitResult``
into actual git commits, including:

- Saving and restoring the staging area on failure.
- Handling file renames during per-commit staging.
- Pushing after successful commits (with rollback on push failure).
- Dry-run preview.
"""

from __future__ import annotations

import logging
import subprocess
from typing import Any, NamedTuple

from gac.errors import AIError, ConfigError, GitError
from gac.git import detect_rename_mappings, get_staged_files, run_git_command
from gac.postprocess import clean_commit_message
from gac.stats import record_commit, record_gac
from gac.utils import console
from gac.workflow_utils import execute_commit, restore_staging

logger = logging.getLogger(__name__)


class GroupedCommitResult(NamedTuple):
    """Container for the AI's grouped-commit output."""

    commits: list[dict[str, Any]]
    raw_response: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0


def execute_grouped_commits(
    result: GroupedCommitResult,
    dry_run: bool,
    push: bool,
    no_verify: bool,
    hook_timeout: int,
    fifty_seventy_two: bool = False,
    signoff: bool = False,
    model: str | None = None,
) -> int:
    """Execute the grouped commits by creating multiple individual commits.

    Returns:
        Exit code: 0 for success, non-zero for failure.
    """
    num_commits = len(result.commits)

    restore_needed = False
    original_staged_files: list[str] | None = None
    original_staged_diff: str | None = None

    if dry_run:
        console.print(f"[yellow]Dry run: Would create {num_commits} commits[/yellow]")
        for idx, commit in enumerate(result.commits, 1):
            console.print(f"\n[cyan]Commit {idx}/{num_commits}:[/cyan]")
            console.print(f"  Files: {', '.join(commit['files'])}")
            console.print(f"  Message: {commit['message'].strip()[:50]}...")
    else:
        original_staged_files = get_staged_files(existing_only=False)
        original_staged_diff = run_git_command(["diff", "--cached", "--binary"], silent=True).require_success()
        run_git_command(["reset", "HEAD"]).require_success()

        try:
            rename_mappings = detect_rename_mappings(original_staged_diff)

            for idx, commit in enumerate(result.commits, 1):
                try:
                    for file_path in commit["files"]:
                        if file_path in rename_mappings:
                            old_file = rename_mappings[file_path]
                            run_git_command(["add", "-A", old_file]).require_success()
                            run_git_command(["add", "-A", file_path]).require_success()
                        else:
                            run_git_command(["add", "-A", file_path]).require_success()
                    cleaned_message = clean_commit_message(
                        commit["message"].strip(),
                        fifty_seventy_two=fifty_seventy_two,
                    )
                    execute_commit(cleaned_message, no_verify, hook_timeout, signoff)
                    record_commit()
                    console.print(f"[green]✓ Commit {idx}/{num_commits} created[/green]")
                except (AIError, ConfigError, GitError, subprocess.SubprocessError, OSError) as e:
                    restore_needed = True
                    console.print(f"[red]✗ Failed at commit {idx}/{num_commits}: {e}[/red]")
                    console.print(f"[yellow]Completed {idx - 1}/{num_commits} commits.[/yellow]")
                    break
        except KeyboardInterrupt:
            restore_needed = True
            console.print("\n[yellow]Interrupted by user. Restoring original staging area...[/yellow]")

        if restore_needed:
            console.print("[yellow]Restoring original staging area...[/yellow]")
            restore_staging(original_staged_files or [], original_staged_diff)
            console.print("[green]Original staging area restored.[/green]")
            return 1

        record_gac(model=model)

    if push:
        try:
            if dry_run:
                console.print("[yellow]Dry run: Would push changes[/yellow]")
                return 0
            from gac.git import push_changes

            if push_changes():
                logger.info("Changes pushed successfully")
                console.print("[green]Changes pushed successfully[/green]")
            else:
                restore_needed = True
                console.print(
                    "[red]Failed to push changes. Check your remote configuration and network connection.[/red]"
                )
        except (GitError, OSError) as e:
            restore_needed = True
            console.print(f"[red]Error pushing changes: {e}[/red]")

        if restore_needed:
            console.print("[yellow]Restoring original staging area...[/yellow]")
            if original_staged_files is None or original_staged_diff is None:
                original_staged_files = get_staged_files(existing_only=False)
                original_staged_diff = run_git_command(["diff", "--cached", "--binary"]).require_success()
            restore_staging(original_staged_files, original_staged_diff)
            console.print("[green]Original staging area restored.[/green]")
            return 1

    return 0
