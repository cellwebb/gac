#!/usr/bin/env python3
"""Commit execution logic for gac."""

import logging

from rich.console import Console

from gac.errors import GitError
from gac.git import get_staged_files, push_changes
from gac.workflow_utils import execute_commit

logger = logging.getLogger(__name__)
console = Console()


class CommitExecutor:
    """Handles commit creation and related operations."""

    def __init__(self, dry_run: bool = False, quiet: bool = False, no_verify: bool = False, hook_timeout: int = 120):
        self.dry_run = dry_run
        self.quiet = quiet
        self.no_verify = no_verify
        self.hook_timeout = hook_timeout

    def create_commit(self, commit_message: str) -> None:
        """Create a single commit with the given message."""
        if self.dry_run:
            console.print("[yellow]Dry run: Commit message generated but not applied[/yellow]")
            console.print("Would commit with message:")
            from rich.panel import Panel

            console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
            staged_files = get_staged_files(existing_only=False)
            console.print(f"Would commit {len(staged_files)} files")
            logger.info(f"Would commit {len(staged_files)} files")
        else:
            execute_commit(commit_message, self.no_verify, self.hook_timeout)

    def push_to_remote(self) -> None:
        """Push changes to remote repository.

        Raises:
            GitError: If push fails or remote is not configured.
        """
        if self.dry_run:
            staged_files = get_staged_files(existing_only=False)
            logger.info("Dry run: Would push changes")
            logger.info(f"Would push {len(staged_files)} files")
            console.print("[yellow]Dry run: Would push changes[/yellow]")
            console.print(f"Would push {len(staged_files)} files")
            return

        if push_changes():
            logger.info("Changes pushed successfully")
            if not self.quiet:
                console.print("[green]Changes pushed successfully[/green]")
        else:
            console.print("[red]Failed to push changes. Check your remote configuration and network connection.[/red]")
            raise GitError("Failed to push changes")
