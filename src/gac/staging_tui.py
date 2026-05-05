from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

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
            ["git", "status", "--porcelain", "-u"],
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
