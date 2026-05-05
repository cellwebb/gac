#!/usr/bin/env python3
"""Interactive file staging TUI for gac.

Provides a tree-based, navigable file selector that displays `git status` output
and lets the user select files, directories, or the entire root to stage —
replacing the need for manual `git add <file>` calls.

The visual TUI layer lives in ``staging_tui_app.py``; this module contains
the data model, git-status parsing, tree building, and the high-level
entry point ``run_staging_tui()``.

Key bindings (in the TUI):
    ↑/k       Move cursor up
    ↓/j       Move cursor down
    Space     Toggle selection (file / directory / root)
    →/l       Expand directory
    ←/h       Collapse directory
    a         Select all
    A         Deselect all
    Enter     Confirm and stage selected files
    q/Ctrl+C  Abort without staging
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from gac.errors import GitError
from gac.git import run_git_command
from gac.utils import console

logger = logging.getLogger(__name__)

# ── git status parsing ────────────────────────────────────────────────────


@dataclass
class FileStatus:
    """Parsed status of a single file from `git status --porcelain`."""

    path: str
    xy: str  # Two-char XY code, e.g. "M ", " A", "??", "AM"

    @property
    def staged_code(self) -> str:
        """First char: index (staging area) status."""
        return self.xy[0] if len(self.xy) >= 1 else " "

    @property
    def worktree_code(self) -> str:
        """Second char: working tree status."""
        return self.xy[1] if len(self.xy) >= 2 else " "

    @property
    def is_staged(self) -> bool:
        """True when the file has changes staged in the index."""
        return self.staged_code not in (" ", "?", "!")

    @property
    def is_untracked(self) -> bool:
        return self.xy == "??"

    @property
    def display_xy(self) -> str:
        """Full XY status pair with · replacing spaces for display.

        Handles all standard git XY codes: M (modified), A (added), D (deleted),
        R (renamed), C (copied), T (type change), U (unmerged), ? (untracked),
        ! (ignored).  Any non-space character passes through as-is.

        Examples: ``M·`` (staged mod), ``·M`` (unstaged mod), ``AM`` (staged + unstaged),
        ``??`` (untracked), ``T·`` (staged type change), ``U·`` (unmerged).
        """
        left = self.staged_code if self.staged_code != " " else "·"
        right = self.worktree_code if self.worktree_code != " " else "·"
        return f"{left}{right}"

    @property
    def display_status(self) -> str:
        """Human-friendly short status for display.

        Deprecated: prefer :py:meth:`display_xy` which shows both index and
        worktree status unambiguously.
        """
        if self.is_untracked:
            return "??"
        if self.staged_code != " ":
            return self.staged_code
        return self.worktree_code


def parse_git_status() -> list[FileStatus]:
    """Run `git status --porcelain -u` and parse the output.

    Returns:
        List of FileStatus entries, one per file.

    Raises:
        GitError: If the git command fails.
    """
    result = run_git_command(["status", "--porcelain", "-u"], timeout=10)
    if not result.success:
        raise GitError(result.fail_message("git status failed"))

    entries: list[FileStatus] = []
    for line in result.output.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue

        # porcelain format: "XY PATH" or "XY ORIG -> PATH"
        # XY is always exactly 3 chars (2 status + 1 space) before the path
        if len(line) < 4:
            continue

        xy = line[:2]
        rest = line[3:]

        # Handle renames: "XY ORIG_PATH -> NEW_PATH"
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]

        entries.append(FileStatus(path=rest, xy=xy))

    return entries


# ── tree data structure ───────────────────────────────────────────────────


@dataclass
class TreeNode:
    """A node in the file tree (directory or file)."""

    name: str
    path: str  # Relative path from repo root
    is_dir: bool
    expanded: bool = True  # Directories start expanded
    selected: bool = False
    children: list[TreeNode] = field(default_factory=list)
    file_status: FileStatus | None = None  # Only set for leaf files


def build_file_tree(entries: list[FileStatus]) -> TreeNode:
    """Build a tree from flat file status entries.

    Returns:
        Root TreeNode (virtual, not displayed).
    """
    root = TreeNode(name="<root>", path="", is_dir=True, expanded=True)

    for entry in entries:
        # PurePosixPath because git always uses forward slashes, even on Windows
        parts = PurePosixPath(entry.path).parts
        current = root

        # Walk through directory parts
        for i, part in enumerate(parts[:-1]):
            dir_path = str(PurePosixPath(*parts[: i + 1]))
            child = _find_child(current, part)
            if child is None:
                child = TreeNode(name=part, path=dir_path, is_dir=True, expanded=True)
                current.children.append(child)
            current = child

        # Add the leaf file
        leaf = TreeNode(
            name=parts[-1],
            path=entry.path,
            is_dir=False,
            selected=entry.is_staged,
            file_status=entry,
        )
        current.children.append(leaf)

    # Sort: directories first, then files; alphabetical within each group
    _sort_tree(root)

    # Propagate directory selection state from pre-selected files
    _propagate_selection_upward(root)

    return root


def _find_child(node: TreeNode, name: str) -> TreeNode | None:
    """Find a child node by name."""
    for child in node.children:
        if child.name == name and child.is_dir:
            return child
    return None


def _sort_tree(node: TreeNode) -> None:
    """Sort children: directories first (alphabetical), then files (alphabetical)."""
    node.children.sort(key=lambda c: (not c.is_dir, c.name.lower()))
    for child in node.children:
        if child.is_dir:
            _sort_tree(child)


def _propagate_selection_upward(node: TreeNode) -> None:
    """After setting leaf selections, compute directory selection states upward.

    A directory is selected iff ALL its children are selected.
    """
    if not node.is_dir:
        return

    for child in node.children:
        _propagate_selection_upward(child)

    if node.children:
        node.selected = all(c.selected for c in node.children)


def _propagate_selection_downward(node: TreeNode, selected: bool) -> None:
    """Set a node and all its descendants to the given selection state."""
    node.selected = selected
    for child in node.children:
        _propagate_selection_downward(child, selected)


# ── display helpers (shared with staging_tui_app) ────────────────────────


def _selection_indicator(node: TreeNode) -> str:
    """Return the checkbox character for a node.

    For directories: ☑ all selected, ☐ none selected, ◻ some selected (indeterminate).
    For files: ☑ selected, ☐ unselected.
    """
    if node.is_dir:
        if not node.children:
            return "☐"
        all_sel = all(c.selected for c in node.children)
        any_sel = any(c.selected for c in node.children)
        if all_sel:
            return "☑"
        if any_sel:
            return "◻"
        return "☐"
    return "☑" if node.selected else "☐"


def _flatten_tree(node: TreeNode, depth: int = 0) -> list[tuple[TreeNode, int]]:
    """Flatten the visible tree into a list of (node, depth) for display.

    Collapsed directories don't show their children.
    """
    result: list[tuple[TreeNode, int]] = []
    for child in node.children:
        result.append((child, depth))
        if child.is_dir and child.expanded:
            result.extend(_flatten_tree(child, depth + 1))
    return result


# ── staging operations ────────────────────────────────────────────────────


def stage_files(file_paths: list[str]) -> bool:
    """Stage the given files using `git add`.

    Args:
        file_paths: List of file paths to stage.

    Returns:
        True if all files were staged successfully, False otherwise.
    """
    if not file_paths:
        return True

    result = run_git_command(["add", *file_paths], timeout=30)
    if not result.success:
        logger.error(f"git add failed: {result.stderr}")
        console.print(f"[red]Failed to stage files: {result.stderr}[/red]")
        return False
    return True


def run_staging_tui() -> list[str] | None:
    """High-level entry point: parse git status, run TUI, return selected files.

    Returns:
        List of selected file paths, or None if the user aborted.
    """
    from gac.staging_tui_app import StagingTUI

    try:
        entries = parse_git_status()
    except GitError as e:
        console.print(f"[red]Error reading git status: {e}[/red]")
        return None

    if not entries:
        console.print("[yellow]No changes found in the repository.[/yellow]")
        return []

    tui = StagingTUI(entries)
    selected = tui.run()

    if selected is None:
        console.print("[yellow]Staging aborted.[/yellow]")
        return None

    if not selected:
        console.print("[yellow]No files selected for staging.[/yellow]")
        return []

    return selected
