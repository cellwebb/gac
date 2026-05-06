from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Tree
from textual.widgets.tree import TreeNode

from gac.errors import GitError
from gac.utils import console

logger = logging.getLogger(__name__)


@dataclass
class FileStatus:
    path: str
    xy: str

    @property
    def staged_code(self) -> str:
        return self.xy[0] if len(self.xy) >= 1 else " "

    @property
    def worktree_code(self) -> str:
        return self.xy[1] if len(self.xy) >= 2 else " "

    @property
    def is_staged(self) -> bool:
        return self.staged_code not in (" ", "?", "!")

    @property
    def is_untracked(self) -> bool:
        return self.xy == "??"

    @property
    def display_status(self) -> str:
        if self.is_untracked:
            return "??"
        if self.staged_code != " ":
            return self.staged_code
        return self.worktree_code


def parse_git_status() -> list[FileStatus]:
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotePath=false", "status", "--porcelain", "-u"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            raise GitError(f"git status failed: {result.stderr.strip()}")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        raise GitError(f"Failed to run git status: {e}") from e

    entries: list[FileStatus] = []
    for line in result.stdout.splitlines():
        line = line.rstrip("\n")
        if not line or len(line) < 4:
            continue
        xy = line[:2]
        rest = line[3:]
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        entries.append(FileStatus(path=rest, xy=xy))
    return entries


FileTree = dict[str, Any]


def build_file_tree(entries: list[FileStatus]) -> FileTree:
    root: FileTree = {}
    for entry in entries:
        parts = PurePosixPath(entry.path).parts
        node = root
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            node = node[part]
        node[parts[-1]] = entry

    def _sort(d: FileTree) -> FileTree:
        dirs = sorted((k for k, v in d.items() if isinstance(v, dict)), key=str.lower)
        files = sorted((k for k, v in d.items() if isinstance(v, FileStatus)), key=str.lower)
        return {k: (_sort(d[k]) if isinstance(d[k], dict) else d[k]) for k in dirs + files}

    return _sort(root)


def stage_files(file_paths: list[str]) -> bool:
    if not file_paths:
        return True
    try:
        result = subprocess.run(
            ["git", "add", *file_paths],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if result.returncode != 0:
            logger.error(f"git add failed: {result.stderr.strip()}")
            console.print(f"[red]Failed to stage files: {result.stderr.strip()}[/red]")
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.error(f"Failed to run git add: {e}")
        console.print(f"[red]Failed to stage files: {e}[/red]")
        return False


_STATUS_COLOR: dict[str, str] = {
    "M": "yellow",
    "A": "green",
    "D": "red",
    "R": "cyan",
    "??": "bright_red",
}


def _file_label(name: str, status: FileStatus, selected: bool) -> str:
    check = "[green]☑[/green]" if selected else "[dim]☐[/dim]"
    color = _STATUS_COLOR.get(status.display_status, "white")
    badge = f"[{color}][{status.display_status}][/{color}]"
    return f"{check} {name}  {badge}"


def _dir_label(name: str, sel_count: int, total: int) -> str:
    if total == 0:
        check = "[dim]☐[/dim]"
    elif sel_count == total:
        check = "[green]☑[/green]"
    else:
        check = "[yellow]◻[/yellow]"
    icon = "📂" if sel_count > 0 else "📁"
    return f"{check} {icon} {name}/"


class StagingApp(App[list[str] | None]):
    """Textual app for interactively selecting files to stage."""

    BINDINGS = [
        Binding("space", "toggle_selection", "Toggle", show=True),
        Binding("a", "select_all", "All", show=True),
        Binding("A", "deselect_all", "None", show=True),
        Binding("enter", "confirm", "Confirm", show=True, priority=True),
        Binding("q", "abort", "Abort", show=True),
    ]

    def __init__(self, entries: list[FileStatus]) -> None:
        super().__init__()
        self._entries = entries
        self._selected: set[str] = {e.path for e in entries if e.is_staged}
        self._file_nodes: dict[str, TreeNode[Any]] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Tree("Repository", id="file-tree")
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one("#file-tree", Tree)
        tree.root.expand()
        self._populate_tree(tree.root, build_file_tree(self._entries), "")

    def _populate_tree(self, parent: TreeNode[Any], subtree: FileTree, prefix: str) -> None:
        for name, value in subtree.items():
            path = f"{name}" if not prefix else f"{prefix}/{name}"
            if isinstance(value, dict):
                counts = self._count_selected(value, path + "/")
                label = _dir_label(name, counts[0], counts[1])
                node = parent.add(label, data={"type": "dir", "path": path, "name": name, "subtree": value})
                node.expand()
                self._file_nodes[path] = node
                self._populate_tree(node, value, path)
            else:
                label = _file_label(name, value, path in self._selected)
                node = parent.add_leaf(label, data={"type": "file", "path": path, "name": name, "status": value})
                self._file_nodes[path] = node

    def _count_selected(self, subtree: FileTree, prefix: str) -> tuple[int, int]:
        sel = total = 0
        for name, value in subtree.items():
            path = f"{prefix}{name}"
            if isinstance(value, dict):
                s, t = self._count_selected(value, path + "/")
                sel += s
                total += t
            else:
                total += 1
                if path in self._selected:
                    sel += 1
        return sel, total

    def _file_paths_under(self, subtree: FileTree, prefix: str) -> list[str]:
        paths: list[str] = []
        for name, value in subtree.items():
            path = f"{prefix}{name}"
            if isinstance(value, dict):
                paths.extend(self._file_paths_under(value, path + "/"))
            else:
                paths.append(path)
        return paths

    def _update_labels(self) -> None:
        for path, node in self._file_nodes.items():
            data = node.data
            if data is None:
                continue
            if data["type"] == "file":
                node.set_label(_file_label(data["name"], data["status"], path in self._selected))
            else:
                node.set_label(_dir_label(data["name"], *self._count_selected(data["subtree"], path + "/")))

    def action_toggle_selection(self) -> None:
        tree = self.query_one("#file-tree", Tree)
        node = tree.cursor_node
        if node is None or node.data is None:
            return
        data = node.data
        if data["type"] == "file":
            path = data["path"]
            if path in self._selected:
                self._selected.discard(path)
            else:
                self._selected.add(path)
        else:
            paths = self._file_paths_under(data["subtree"], data["path"] + "/")
            if all(p in self._selected for p in paths):
                self._selected.difference_update(paths)
            else:
                self._selected.update(paths)
        self._update_labels()

    def action_select_all(self) -> None:
        self._selected = {e.path for e in self._entries}
        self._update_labels()

    def action_deselect_all(self) -> None:
        self._selected.clear()
        self._update_labels()

    def action_confirm(self) -> None:
        self.exit(sorted(self._selected))

    def action_abort(self) -> None:
        self.exit(None)


def run_staging_tui() -> list[str] | None:
    try:
        entries = parse_git_status()
    except GitError as e:
        console.print(f"[red]Error reading git status: {e}[/red]")
        return None

    if not entries:
        console.print("[yellow]No changes found in the repository.[/yellow]")
        return None

    return StagingApp(entries).run()
