#!/usr/bin/env python3
"""Staging TUI application and rendering for gac.

Contains the prompt_toolkit-based interactive file selector and all
display-related helpers.  The data model and tree-building logic live
in ``staging_tui.py``; this module provides the visual layer.

Key bindings:
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
import subprocess
from dataclasses import dataclass
from typing import Any

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from gac.staging_tui import FileStatus, TreeNode, _flatten_tree, _propagate_selection_downward, _selection_indicator
from gac.utils import console

logger = logging.getLogger(__name__)

# ── display helpers ────────────────────────────────────────────────────────


def _dir_icon(node: TreeNode) -> str:
    """Return the icon for a directory node."""
    if node.expanded:
        return "📂"
    return "📁"


def _file_icon(node: TreeNode) -> str:
    """Return an icon for a file based on its status."""
    if node.file_status is None:
        return "📄"
    if node.file_status.is_untracked:
        return "❓"
    if node.file_status.is_staged:
        return "✅"
    return "📝"


def _status_badge(node: TreeNode) -> str:
    """Return the full XY status string for a file (e.g. 'M·', '·M', '??')."""
    if node.file_status is None:
        return ""
    return node.file_status.display_xy


# ── TUI style ───────────────────────────────────────────────────────────────

TUI_STYLE = Style.from_dict(
    {
        "cursor": "reverse",
        "checkbox-selected": "fg:#50fa7b bold",
        "checkbox-unselected": "fg:#6272a4",
        "checkbox-indeterminate": "fg:#f1fa8c",
        "dir-icon": "fg:#bd93f9",
        "file-icon": "fg:#8be9fd",
        "status-staged": "fg:#50fa7b bold",
        "status-modified": "fg:#ffb86c",
        "status-untracked": "fg:#ff5555",
        "status-default": "fg:#6272a4",
        "hint": "fg:#6272a4",
        "header": "fg:#f8f8f2 bold",
        "selected-path": "fg:#50fa7b",
        "branch": "fg:#bd93f9",
        "count": "fg:#8be9fd",
    }
)


# ── TUI state ───────────────────────────────────────────────────────────────


@dataclass
class TUIState:
    """Mutable state for the staging TUI."""

    root: TreeNode
    cursor_index: int = 0
    aborted: bool = False
    confirmed: bool = False


# ── TUI application ────────────────────────────────────────────────────────


class StagingTUI:
    """Interactive file staging TUI built on prompt_toolkit."""

    def __init__(self, file_statuses: list[FileStatus]) -> None:
        from gac.staging_tui import build_file_tree

        self.entries = file_statuses
        self.root = build_file_tree(file_statuses)
        self.state = TUIState(root=self.root)
        self._branch = self._get_current_branch()

    @staticmethod
    def _get_current_branch() -> str:
        """Get the current git branch name for display."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return "unknown"

    def _flat_items(self) -> list[tuple[TreeNode, int]]:
        """Get the current flat list of visible items."""
        return _flatten_tree(self.state.root)

    def _current_node(self) -> TreeNode | None:
        """Get the currently highlighted node."""
        items = self._flat_items()
        if not items or self.state.cursor_index >= len(items):
            return None
        return items[self.state.cursor_index][0]

    # ── rendering ──────────────────────────────────────────────────────

    def _render(self) -> StyleAndTextTuples:
        """Render the full TUI display as formatted text."""
        lines: StyleAndTextTuples = []

        # Header: branch + summary + hint about checkboxes
        num_staged = sum(1 for e in self.entries if e.is_staged)
        num_total = len(self.entries)
        lines.append(("class:header", f" 🌿 {self._branch} "))
        lines.append(("", "  "))
        lines.append(("class:count", f"{num_total} file(s)"))
        if num_staged > 0:
            lines.append(("", "  "))
            lines.append(("class:status-staged", f"{num_staged} already staged"))
        lines.append(("", "\n"))
        lines.append(("class:hint", "   ☑ = will stage  ☐ = skip  [XY] = index/worktree status"))
        lines.append(("", "\n"))

        # Tree items
        items = self._flat_items()
        for i, (node, depth) in enumerate(items):
            self._render_node(lines, i, node, depth)

        # Footer: hints
        lines.append(("", "\n"))
        lines.append(
            (
                "class:hint",
                " ↑/↓ navigate │ Space select │ ←/→ expand/collapse │ a/A select/deselect all │ Enter confirm │ q abort ",
            )
        )

        return lines

    def _render_node(self, lines: StyleAndTextTuples, i: int, node: TreeNode, depth: int) -> None:
        """Render a single node in the tree display."""
        is_cursor = i == self.state.cursor_index
        indent = "  " * depth
        prefix = "▶ " if is_cursor else "  "

        # Checkbox
        indicator = _selection_indicator(node)
        if indicator == "☑":
            cb_style = "class:checkbox-selected"
        elif indicator == "◻":
            cb_style = "class:checkbox-indeterminate"
        else:
            cb_style = "class:checkbox-unselected"

        # Indent + cursor prefix
        if is_cursor:
            lines.append(("class:cursor", f"{indent}{prefix}"))
        else:
            lines.append(("", f"{indent}{prefix}"))

        lines.append((cb_style, f"{indicator} "))

        if node.is_dir:
            self._render_dir_node(lines, node, is_cursor)
        else:
            self._render_file_node(lines, node, is_cursor)

        lines.append(("", "\n"))

    def _render_dir_node(self, lines: StyleAndTextTuples, node: TreeNode, is_cursor: bool) -> None:
        """Render a directory node."""
        icon = _dir_icon(node)
        lines.append(("class:dir-icon", f"{icon} "))
        name_style = "class:cursor" if is_cursor else "class:dir-icon"
        lines.append((name_style, f"{node.name}/"))
        if not node.expanded:
            lines.append(("class:hint", f" ({len(node.children)})"))

    def _render_file_node(self, lines: StyleAndTextTuples, node: TreeNode, is_cursor: bool) -> None:
        """Render a file node."""
        icon = _file_icon(node)
        lines.append(("class:file-icon", f"{icon} "))
        name_style = "class:selected-path" if node.selected else ("class:cursor" if is_cursor else "")
        lines.append((name_style, node.name))

        # Render two-column XY badge with split coloring
        #   Left char  = index (staging area) → green
        #   Right char = worktree (unstaged)  → orange
        #   ??         = untracked            → red
        if node.file_status is not None:
            lines.append(("", "  "))
            self._render_xy_badge(lines, node.file_status)

    @staticmethod
    def _render_xy_badge(lines: StyleAndTextTuples, fs: FileStatus) -> None:
        """Render the two-column git XY status badge with per-column coloring.

        Format: ``[XY]`` where X=index, Y=worktree, spaces→·.
        Index (left) chars are green, worktree (right) chars are orange,
        ``??`` is red, ``··`` is dim.
        """
        if fs.is_untracked:
            lines.append(("class:status-untracked", "[??]"))
            return

        xy = fs.display_xy
        left, right = xy[0], xy[1] if len(xy) >= 2 else "·"

        lines.append(("class:status-default", "["))
        # Left column: index status
        left_style = "class:status-staged" if left != "·" else "class:status-default"
        lines.append((left_style, left))
        # Right column: worktree status
        right_style = "class:status-modified" if right != "·" else "class:status-default"
        lines.append((right_style, right))
        lines.append(("class:status-default", "]"))

    # ── interaction handlers ────────────────────────────────────────────

    def _toggle_selection(self) -> None:
        """Toggle selection on the current node."""
        node = self._current_node()
        if node is None:
            return

        if node.is_dir:
            all_selected = all(c.selected for c in node.children)
            _propagate_selection_downward(node, not all_selected)
            self._update_parent_selection(node)
        else:
            node.selected = not node.selected
            self._update_parent_selection(node)

    def _update_parent_selection(self, node: TreeNode) -> None:
        """Update selection state of all ancestor directories."""
        self._update_parent_selection_in(self.state.root, node)

    def _update_parent_selection_in(self, current: TreeNode, target: TreeNode) -> bool:
        """Walk tree to find target's parent and update selection. Returns True if found."""
        for child in current.children:
            if child is target:
                if current.is_dir and current.children:
                    current.selected = all(c.selected for c in current.children)
                return True
            if child.is_dir and child.children:
                found = self._update_parent_selection_in(child, target)
                if found:
                    if current.is_dir and current.children:
                        current.selected = all(c.selected for c in current.children)
                    return True
        return False

    def _expand_current(self) -> None:
        """Expand the current node (if directory)."""
        node = self._current_node()
        if node is not None and node.is_dir:
            node.expanded = True

    def _collapse_current(self) -> None:
        """Collapse the current node (if directory)."""
        node = self._current_node()
        if node is not None and node.is_dir:
            node.expanded = False

    def _select_all(self) -> None:
        """Select all nodes."""
        _propagate_selection_downward(self.state.root, True)

    def _deselect_all(self) -> None:
        """Deselect all nodes."""
        _propagate_selection_downward(self.state.root, False)

    def _move_cursor(self, delta: int) -> None:
        """Move the cursor by delta positions, clamping to valid range."""
        items = self._flat_items()
        if not items:
            return
        self.state.cursor_index = max(0, min(len(items) - 1, self.state.cursor_index + delta))

    def get_selected_files(self) -> list[str]:
        """Get the list of file paths that are selected (leaf files only)."""
        return self._collect_selected(self.state.root)

    def _collect_selected(self, node: TreeNode) -> list[str]:
        """Recursively collect selected file paths."""
        result: list[str] = []
        if not node.is_dir and node.selected:
            result.append(node.path)
        for child in node.children:
            result.extend(self._collect_selected(child))
        return result

    # ── main run loop ──────────────────────────────────────────────────

    def run(self) -> list[str] | None:
        """Run the staging TUI and return selected file paths, or None if aborted.

        Returns:
            List of selected file paths to stage, or None if the user aborted.
        """
        if not self.entries:
            console.print("[yellow]No changes found in the repository.[/yellow]")
            return []

        # Set initial cursor to first unselected file
        items = self._flat_items()
        if items:
            for i, (node, _) in enumerate(items):
                if not node.is_dir and not node.selected:
                    self.state.cursor_index = i
                    break

        content = FormattedTextControl(text=lambda: self._render())
        text_window = Window(content=content, dont_extend_height=True)

        root_container = HSplit([text_window])
        layout = Layout(root_container)

        kb = self._build_key_bindings()

        app: Application[None] = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
            mouse_support=False,
            style=TUI_STYLE,
        )

        try:
            app.run()
        except (EOFError, KeyboardInterrupt):
            self.state.aborted = True

        if self.state.aborted:
            return None

        return self.get_selected_files()

    def _build_key_bindings(self) -> KeyBindings:
        """Build and return the key binding registry."""
        kb = KeyBindings()

        @kb.add("up")
        @kb.add("k")
        def _move_up(event: Any) -> None:
            self._move_cursor(-1)

        @kb.add("down")
        @kb.add("j")
        def _move_down(event: Any) -> None:
            self._move_cursor(1)

        @kb.add("space")
        def _toggle(event: Any) -> None:
            self._toggle_selection()

        @kb.add("right")
        @kb.add("l")
        def _expand(event: Any) -> None:
            self._expand_current()

        @kb.add("left")
        @kb.add("h")
        def _collapse(event: Any) -> None:
            self._collapse_current()

        @kb.add("a")
        def _sel_all(event: Any) -> None:
            self._select_all()

        @kb.add("A")
        def _desel_all(event: Any) -> None:
            self._deselect_all()

        @kb.add("enter")
        def _confirm(event: Any) -> None:
            self.state.confirmed = True
            event.app.exit()

        @kb.add("q")
        @kb.add("c-c")
        def _abort(event: Any) -> None:
            self.state.aborted = True
            event.app.exit()

        return kb
