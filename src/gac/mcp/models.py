"""Pydantic models for MCP tool requests and responses.

These models define the structured input/output for GAC's MCP tools.
Pydantic provides automatic schema generation for the MCP protocol.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# COMMIT TOOL MODELS
# =============================================================================


class CommitRequest(BaseModel):
    """Request model for gac_commit tool.

    This single model covers all commit operations through parameter combinations.
    Like RGB colors, different parameter combinations enable different workflows:

    Basic commit: stage_all=True
    Preview only: dry_run=True
    Message only: message_only=True (returns message without committing)
    Group commits: group=True (analyze changes and suggest multiple commits)
    Quick commit: stage_all=True, push=True, one_liner=True

    The tool uses the configured AI model from the user's environment.
    """

    # What to commit
    stage_all: bool = Field(
        default=False,
        description="Stage all changes before committing (equivalent to git add -A)",
    )
    files: list[str] = Field(
        default_factory=list,
        description="Specific files to stage. Empty list uses currently staged files.",
    )

    # How to commit
    dry_run: bool = Field(
        default=False,
        description="Preview the commit workflow without executing. Shows what would happen.",
    )
    message_only: bool = Field(
        default=False,
        description="Generate and return the commit message without committing. Useful for review.",
    )
    push: bool = Field(
        default=False,
        description="Push to remote after successful commit.",
    )
    group: bool = Field(
        default=False,
        description="Analyze changes and suggest multiple logical commits. Returns grouped suggestions.",
    )

    # Message style
    one_liner: bool = Field(
        default=False,
        description="Generate a single-line commit message (no body).",
    )
    scope: str | None = Field(
        default=None,
        description="Conventional commit scope (e.g., 'auth', 'api', 'ui'). Auto-detected if not provided.",
    )
    hint: str = Field(
        default="",
        description="Additional context to help the AI generate a better commit message. "
        "Include ticket numbers, context, or specific changes to highlight.",
    )

    # Overrides
    model: str | None = Field(
        default=None,
        description="Override the configured AI model. Format: 'provider:model_name' "
        "(e.g., 'openai:gpt-4', 'anthropic:claude-3-sonnet').",
    )
    language: str | None = Field(
        default=None,
        description="Override the commit message language (e.g., 'Spanish', 'zh-CN', 'ja').",
    )

    # Safety
    skip_secret_scan: bool = Field(
        default=False,
        description="Skip the security scan for secrets in staged changes. Use with caution.",
    )
    no_verify: bool = Field(
        default=False,
        description="Skip pre-commit and lefthook hooks when committing.",
    )

    # Confirmation
    auto_confirm: bool = Field(
        default=False,
        description="Skip confirmation prompts. Required for non-interactive agent use.",
    )


class CommitResult(BaseModel):
    """Response model for gac_commit tool.

    Contains the result of the commit operation, including the generated
    message, commit hash (if committed), and list of changed files.
    """

    success: bool = Field(description="Whether the operation completed successfully.")
    commit_message: str = Field(description="The generated commit message.")
    commit_hash: str | None = Field(
        default=None,
        description="The commit hash if the commit was executed. None for dry_run or message_only.",
    )
    files_changed: list[str] = Field(
        default_factory=list,
        description="List of files that were staged/committed.",
    )
    grouped_commits: list[GroupedCommit] | None = Field(
        default=None,
        description="When group=True, contains suggested commit groupings.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if success is False.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings (e.g., secrets detected, long lines).",
    )


class GroupedCommit(BaseModel):
    """A suggested commit grouping when group=True."""

    scope: str = Field(description="Suggested scope for this group.")
    files: list[str] = Field(description="Files in this group.")
    suggested_message: str = Field(description="Suggested commit message for this group.")


# =============================================================================
# STATUS TOOL MODELS
# =============================================================================


class StatusRequest(BaseModel):
    """Request model for gac_status tool.

    This single model covers all repository inspection operations:

    Basic status: No parameters
    With diff: include_diff=True
    With history: include_history=N
    Full context: include_diff=True, include_history=5

    Use this tool before gac_commit to understand what will be committed.
    """

    # Output format
    format: Literal["summary", "detailed", "json"] = Field(
        default="summary",
        description="Output format: 'summary' (clean human-readable), "
        "'detailed' (includes file lists), 'json' (raw data for programmatic use).",
    )

    # What to include
    include_diff: bool = Field(
        default=False,
        description="Include the full diff content in the response.",
    )
    include_stats: bool = Field(
        default=True,
        description="Include line change statistics (additions/deletions per file).",
    )
    include_history: int = Field(
        default=0,
        description="Include N most recent commits in the response. 0 = no history.",
    )

    # Diff options
    staged_only: bool = Field(
        default=False,
        description="Only show staged changes in diff. Default shows both staged and unstaged.",
    )
    include_untracked: bool = Field(
        default=True,
        description="Include untracked files in the status.",
    )

    # Diff size limits
    max_diff_lines: int = Field(
        default=500,
        description="Maximum lines to include in diff output. 0 = no limit. "
        "Prevents overwhelming output for large changes.",
    )


class StatusResult(BaseModel):
    """Response model for gac_status tool.

    Provides a complete view of the repository state, including branch info,
    file status, and optionally diffs and commit history.

    When format='summary' or 'detailed', the 'summary' field contains the
    human-readable formatted output. When format='json', use the individual fields.
    """

    # Formatted output (primary for agents)
    summary: str = Field(
        default="",
        description="Human-readable formatted summary of repository state. Use this field for clean output in agents.",
    )

    # Core status
    branch: str = Field(default="", description="Current git branch name.")
    is_clean: bool = Field(default=False, description="True if no staged, unstaged, or untracked files.")
    is_repo: bool = Field(default=True, description="True if inside a git repository.")

    # File status
    staged_files: list[str] = Field(
        default_factory=list,
        description="Files staged for commit.",
    )
    unstaged_files: list[str] = Field(
        default_factory=list,
        description="Modified but not staged files.",
    )
    untracked_files: list[str] = Field(
        default_factory=list,
        description="Untracked files (not in git).",
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="Files with merge conflicts.",
    )

    # Optional details
    diff: str | None = Field(
        default=None,
        description="Full diff content if include_diff=True.",
    )
    diff_stats: DiffStats | None = Field(
        default=None,
        description="Line change statistics if include_stats=True.",
    )
    recent_commits: list[CommitInfo] | None = Field(
        default=None,
        description="Recent commits if include_history > 0.",
    )
    diff_truncated: bool = Field(
        default=False,
        description="True if diff was truncated due to max_diff_lines.",
    )

    error: str | None = Field(
        default=None,
        description="Error message if status check failed.",
    )


class DiffStats(BaseModel):
    """Line change statistics for the diff."""

    files_changed: int = Field(description="Number of files with changes.")
    insertions: int = Field(description="Total lines added.")
    deletions: int = Field(description="Total lines deleted.")
    file_stats: list[FileStat] = Field(
        default_factory=list,
        description="Per-file statistics.",
    )


class FileStat(BaseModel):
    """Statistics for a single file."""

    file: str = Field(description="File path.")
    insertions: int = Field(description="Lines added.")
    deletions: int = Field(description="Lines deleted.")


class CommitInfo(BaseModel):
    """Information about a single commit."""

    hash: str = Field(description="Commit hash (short form).")
    message: str = Field(description="Commit message (first line).")
    author: str = Field(description="Commit author name.")
    date: str = Field(description="Commit date (relative format).")
