#!/usr/bin/env python3
"""Git state validation and management for gac."""

import logging
import subprocess
from typing import Any, NamedTuple

from rich.console import Console

from gac.config import GACConfig
from gac.errors import ConfigError, GitError, handle_error
from gac.git import get_staged_files, get_staged_status, run_git_command
from gac.preprocess import preprocess_diff
from gac.security import get_affected_files, scan_staged_diff

logger = logging.getLogger(__name__)
console = Console()


class GitState(NamedTuple):
    """Structured representation of git repository state."""

    repo_root: str
    staged_files: list[str]
    status: str
    diff: str
    diff_stat: str
    processed_diff: str
    has_secrets: bool
    secrets: list[Any]


class GitStateValidator:
    """Validates and manages git repository state."""

    def __init__(self, config: GACConfig):
        self.config = config

    def validate_repository(self) -> str:
        """Validate that we're in a git repository and return the repo root."""
        try:
            git_dir = run_git_command(["rev-parse", "--show-toplevel"])
            if not git_dir:
                raise GitError("Not in a git repository")
            return git_dir
        except (subprocess.SubprocessError, GitError, OSError) as e:
            logger.error(f"Error checking git repository: {e}")
            handle_error(GitError("Not in a git repository"), exit_program=True)
            return ""  # Never reached, but required for type safety

    def stage_all_if_requested(self, stage_all: bool, dry_run: bool) -> None:
        """Stage all changes if requested and not in dry run mode."""
        if stage_all and (not dry_run):
            logger.info("Staging all changes")
            run_git_command(["add", "--all"])

    def get_git_state(
        self,
        stage_all: bool = False,
        dry_run: bool = False,
        skip_secret_scan: bool = False,
        quiet: bool = False,
        model: str | None = None,
        hint: str = "",
        one_liner: bool = False,
        infer_scope: bool = False,
        verbose: bool = False,
        language: str | None = None,
    ) -> GitState | None:
        """Get complete git state including validation and processing.

        Returns:
            GitState if staged changes exist, None if no staged changes found.
        """
        from gac.constants import Utility

        # Validate repository
        repo_root = self.validate_repository()

        # Stage files if requested
        self.stage_all_if_requested(stage_all, dry_run)

        # Get staged files
        staged_files = get_staged_files(existing_only=False)

        if not staged_files:
            console.print(
                "[yellow]No staged changes found. Stage your changes with git add first or use --add-all.[/yellow]"
            )
            return None

        # Get git status and diffs
        status = get_staged_status()
        diff = run_git_command(["diff", "--staged"])
        diff_stat = " " + run_git_command(["diff", "--stat", "--cached"])

        # Scan for secrets
        has_secrets = False
        secrets = []
        if not skip_secret_scan:
            logger.info("Scanning staged changes for potential secrets...")
            secrets = scan_staged_diff(diff)
            has_secrets = bool(secrets)

        # Process diff for AI consumption
        logger.debug(f"Preprocessing diff ({len(diff)} characters)")
        if model is None:
            raise ConfigError("Model must be specified via GAC_MODEL environment variable or --model flag")
        processed_diff = preprocess_diff(diff, token_limit=Utility.DEFAULT_DIFF_TOKEN_LIMIT, model=model)
        logger.debug(f"Processed diff ({len(processed_diff)} characters)")

        return GitState(
            repo_root=repo_root,
            staged_files=staged_files,
            status=status,
            diff=diff,
            diff_stat=diff_stat,
            processed_diff=processed_diff,
            has_secrets=has_secrets,
            secrets=secrets,
        )

    def handle_secret_detection(self, secrets: list[Any], quiet: bool = False) -> bool | None:
        """Handle secret detection and user interaction.

        Returns:
            True: Continue with commit
            False: Re-get git state (files were removed)
            None: Abort workflow
        """
        if not secrets:
            return True

        if not quiet:
            console.print("\n[bold red]⚠️  SECURITY WARNING: Potential secrets detected![/bold red]")
            console.print("[red]The following sensitive information was found in your staged changes:[/red]\n")

        for secret in secrets:
            location = f"{secret.file_path}:{secret.line_number}" if secret.line_number else secret.file_path
            if not quiet:
                console.print(f"  • [yellow]{secret.secret_type}[/yellow] in [cyan]{location}[/cyan]")
                console.print(f"    Match: [dim]{secret.matched_text}[/dim]\n")

        if not quiet:
            console.print("\n[bold]Options:[/bold]")
            console.print("  \\[a] Abort commit (recommended)")
            console.print("  \\[c] [yellow]Continue anyway[/yellow] (not recommended)")
            console.print("  \\[r] Remove affected file(s) and continue")

        try:
            import click

            choice = (
                click.prompt(
                    "\nChoose an option",
                    type=click.Choice(["a", "c", "r"], case_sensitive=False),
                    default="a",
                    show_choices=True,
                    show_default=True,
                )
                .strip()
                .lower()
            )
        except (EOFError, KeyboardInterrupt):
            console.print("\n[red]Aborted by user.[/red]")
            return None

        if choice == "a":
            console.print("[yellow]Commit aborted.[/yellow]")
            return None
        elif choice == "c":
            console.print("[bold yellow]⚠️  Continuing with potential secrets in commit...[/bold yellow]")
            logger.warning("User chose to continue despite detected secrets")
            return True
        elif choice == "r":
            affected_files = get_affected_files(secrets)
            for file_path in affected_files:
                try:
                    run_git_command(["reset", "HEAD", file_path])
                    console.print(f"[green]Unstaged: {file_path}[/green]")
                except GitError as e:
                    console.print(f"[red]Failed to unstage {file_path}: {e}[/red]")

            # Check if there are still staged files
            remaining_staged = get_staged_files(existing_only=False)
            if not remaining_staged:
                console.print("[yellow]No files remain staged. Commit aborted.[/yellow]")
                return None

            console.print(f"[green]Continuing with {len(remaining_staged)} staged file(s)...[/green]")
            return False

        return True
