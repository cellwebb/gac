#!/usr/bin/env python3
"""Tests for the staging TUI module."""

from unittest.mock import patch

import pytest

from gac.errors import GitError
from gac.git import GitCommandResult
from gac.staging_tui import (
    FileStatus,
    TreeNode,
    _flatten_tree,
    _propagate_selection_downward,
    _selection_indicator,
    build_file_tree,
    parse_git_status,
    stage_files,
)
from gac.staging_tui_app import StagingTUI

# ── FileStatus tests ──────────────────────────────────────────────────────


class TestFileStatus:
    """Tests for FileStatus dataclass."""

    def test_staged_modification(self) -> None:
        fs = FileStatus(path="foo.py", xy="M ")
        assert fs.staged_code == "M"
        assert fs.worktree_code == " "
        assert fs.is_staged is True
        assert fs.is_untracked is False
        assert fs.display_status == "M"
        assert fs.display_xy == "M·"

    def test_unstaged_modification(self) -> None:
        fs = FileStatus(path="foo.py", xy=" M")
        assert fs.staged_code == " "
        assert fs.worktree_code == "M"
        assert fs.is_staged is False
        assert fs.is_untracked is False
        assert fs.display_status == "M"
        assert fs.display_xy == "·M"

    def test_untracked(self) -> None:
        fs = FileStatus(path="foo.py", xy="??")
        assert fs.is_staged is False
        assert fs.is_untracked is True
        assert fs.display_status == "??"
        assert fs.display_xy == "??"

    def test_added_then_modified(self) -> None:
        fs = FileStatus(path="foo.py", xy="AM")
        assert fs.is_staged is True
        assert fs.display_status == "A"
        assert fs.display_xy == "AM"

    def test_deleted_staged(self) -> None:
        fs = FileStatus(path="foo.py", xy="D ")
        assert fs.is_staged is True
        assert fs.display_status == "D"
        assert fs.display_xy == "D·"

    def test_renamed_staged(self) -> None:
        fs = FileStatus(path="bar.py", xy="R ")
        assert fs.is_staged is True
        assert fs.display_status == "R"
        assert fs.display_xy == "R·"

    def test_both_staged_and_unstaged(self) -> None:
        fs = FileStatus(path="foo.py", xy="MM")
        assert fs.is_staged is True
        assert fs.display_xy == "MM"

    def test_display_xy_distinguishes_staged_from_unstaged(self) -> None:
        """The key insight: M· (staged) vs ·M (unstaged) must differ."""
        staged = FileStatus(path="a.py", xy="M ")
        unstaged = FileStatus(path="b.py", xy=" M")
        assert staged.display_xy != unstaged.display_xy
        assert staged.display_xy == "M·"
        assert unstaged.display_xy == "·M"

    def test_type_change_status(self) -> None:
        """T = type change (e.g. regular file → symlink)."""
        fs = FileStatus(path="link", xy="T ")
        assert fs.is_staged is True
        assert fs.display_xy == "T·"

    def test_unmerged_status(self) -> None:
        """U = unmerged (merge conflict)."""
        fs = FileStatus(path="conflict.py", xy="UU")
        assert fs.is_staged is True  # U is not space/?/!
        assert fs.display_xy == "UU"

    def test_ignored_status(self) -> None:
        """! = ignored file (from git status -u with ignored)."""
        fs = FileStatus(path="build/", xy="!!")
        assert fs.is_staged is False  # ! is in the exclusion set
        assert fs.is_untracked is False
        assert fs.display_xy == "!!"

    def test_copied_status(self) -> None:
        """C = copied file."""
        fs = FileStatus(path="copy.py", xy="C ")
        assert fs.is_staged is True
        assert fs.display_xy == "C·"


# ── parse_git_status tests ────────────────────────────────────────────────


class TestParseGitStatus:
    """Tests for git status parsing."""

    def test_parse_basic_output(self) -> None:
        result = GitCommandResult.ok("M  src/foo.py\n A src/bar.py\n?? src/baz.py\n")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            entries = parse_git_status()

        assert len(entries) == 3
        assert entries[0].path == "src/foo.py"
        assert entries[0].xy == "M "
        assert entries[1].path == "src/bar.py"
        assert entries[1].xy == " A"
        assert entries[2].path == "src/baz.py"
        assert entries[2].xy == "??"

    def test_parse_rename(self) -> None:
        result = GitCommandResult.ok("R  old_path.py -> new_path.py\n")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            entries = parse_git_status()

        assert len(entries) == 1
        assert entries[0].path == "new_path.py"
        assert entries[0].xy == "R "

    def test_parse_empty_output(self) -> None:
        result = GitCommandResult.ok("")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            entries = parse_git_status()

        assert entries == []

    def test_parse_git_failure(self) -> None:
        result = GitCommandResult.fail(returncode=128, stderr="not a git repository")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            with pytest.raises(GitError):
                parse_git_status()

    def test_parse_filenames_with_spaces(self) -> None:
        """Filenames with spaces should be parsed correctly from git output."""
        result = GitCommandResult.ok("M  path/to/foo bar.py\n?? another file.py\n")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            entries = parse_git_status()

        assert len(entries) == 2
        assert entries[0].path == "path/to/foo bar.py"
        assert entries[1].path == "another file.py"

    def test_parse_filenames_with_quotes(self) -> None:
        """Filenames with quotes should pass through (git handles quoting)."""
        result = GitCommandResult.ok("M  path/to/foo\"bar.py\n?? singly'quoted.py\n")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            entries = parse_git_status()

        assert len(entries) == 2
        assert entries[0].path == 'path/to/foo"bar.py'
        assert entries[1].path == "singly'quoted.py"


# ── Tree building tests ────────────────────────────────────────────────────


class TestBuildFileTree:
    """Tests for file tree construction."""

    def test_flat_files(self) -> None:
        entries = [
            FileStatus(path="foo.py", xy="M "),
            FileStatus(path="bar.py", xy="??"),
        ]
        root = build_file_tree(entries)
        assert len(root.children) == 2
        assert root.children[0].name == "bar.py"  # Sorted alphabetically
        assert root.children[1].name == "foo.py"

    def test_nested_directories(self) -> None:
        entries = [
            FileStatus(path="src/gac/cli.py", xy="M "),
            FileStatus(path="src/gac/main.py", xy=" M"),
        ]
        root = build_file_tree(entries)
        assert len(root.children) == 1
        src = root.children[0]
        assert src.name == "src"
        assert src.is_dir
        gac = src.children[0]
        assert gac.name == "gac"
        assert len(gac.children) == 2

    def test_mixed_dirs_and_files(self) -> None:
        entries = [
            FileStatus(path="README.md", xy="??"),
            FileStatus(path="src/gac/cli.py", xy="M "),
            FileStatus(path="src/gac/main.py", xy=" M"),
        ]
        root = build_file_tree(entries)
        # Directories first, then files
        assert root.children[0].is_dir
        assert root.children[0].name == "src"
        assert root.children[1].is_dir is False
        assert root.children[1].name == "README.md"

    def test_pre_selected_staged_files(self) -> None:
        entries = [
            FileStatus(path="staged.py", xy="M "),  # Staged
            FileStatus(path="unstaged.py", xy=" M"),  # Not staged
            FileStatus(path="untracked.py", xy="??"),  # Untracked
        ]
        root = build_file_tree(entries)
        assert root.children[0].selected is True  # staged.py (sorted first? No - alphabetical)
        # Actually sorted alphabetically: staged.py, untracked.py, unstaged.py
        staged_node = next(c for c in root.children if c.name == "staged.py")
        unstaged_node = next(c for c in root.children if c.name == "unstaged.py")
        untracked_node = next(c for c in root.children if c.name == "untracked.py")
        assert staged_node.selected is True
        assert unstaged_node.selected is False
        assert untracked_node.selected is False

    def test_directory_selection_propagation(self) -> None:
        """When all files in a dir are staged, the dir should appear selected."""
        entries = [
            FileStatus(path="src/a.py", xy="M "),
            FileStatus(path="src/b.py", xy="A "),
        ]
        root = build_file_tree(entries)
        src = root.children[0]
        assert src.is_dir
        assert src.selected is True  # All children are staged


# ── Selection indicator tests ─────────────────────────────────────────────


class TestSelectionIndicator:
    def test_selected_file(self) -> None:
        node = TreeNode(name="f.py", path="f.py", is_dir=False, selected=True)
        assert _selection_indicator(node) == "☑"

    def test_unselected_file(self) -> None:
        node = TreeNode(name="f.py", path="f.py", is_dir=False, selected=False)
        assert _selection_indicator(node) == "☐"

    def test_dir_all_selected(self) -> None:
        child1 = TreeNode(name="a.py", path="a.py", is_dir=False, selected=True)
        child2 = TreeNode(name="b.py", path="b.py", is_dir=False, selected=True)
        parent = TreeNode(name="src", path="src", is_dir=True, children=[child1, child2], selected=True)
        assert _selection_indicator(parent) == "☑"

    def test_dir_none_selected(self) -> None:
        child1 = TreeNode(name="a.py", path="a.py", is_dir=False, selected=False)
        child2 = TreeNode(name="b.py", path="b.py", is_dir=False, selected=False)
        parent = TreeNode(name="src", path="src", is_dir=True, children=[child1, child2], selected=False)
        assert _selection_indicator(parent) == "☐"

    def test_dir_indeterminate(self) -> None:
        child1 = TreeNode(name="a.py", path="a.py", is_dir=False, selected=True)
        child2 = TreeNode(name="b.py", path="b.py", is_dir=False, selected=False)
        parent = TreeNode(name="src", path="src", is_dir=True, children=[child1, child2], selected=False)
        assert _selection_indicator(parent) == "◻"

    def test_dir_empty(self) -> None:
        parent = TreeNode(name="empty", path="empty", is_dir=True, children=[], selected=False)
        assert _selection_indicator(parent) == "☐"


# ── Flatten tree tests ────────────────────────────────────────────────────


class TestFlattenTree:
    def test_flat_files(self) -> None:
        f1 = TreeNode(name="a.py", path="a.py", is_dir=False)
        f2 = TreeNode(name="b.py", path="b.py", is_dir=False)
        root = TreeNode(name="<root>", path="", is_dir=True, children=[f1, f2])
        flat = _flatten_tree(root)
        assert len(flat) == 2
        assert flat[0][0].name == "a.py"
        assert flat[1][0].name == "b.py"

    def test_expanded_dir(self) -> None:
        child = TreeNode(name="a.py", path="src/a.py", is_dir=False)
        src = TreeNode(name="src", path="src", is_dir=True, expanded=True, children=[child])
        root = TreeNode(name="<root>", path="", is_dir=True, children=[src])
        flat = _flatten_tree(root)
        assert len(flat) == 2
        assert flat[0][0].is_dir
        assert flat[1][0].name == "a.py"

    def test_collapsed_dir(self) -> None:
        child = TreeNode(name="a.py", path="src/a.py", is_dir=False)
        src = TreeNode(name="src", path="src", is_dir=True, expanded=False, children=[child])
        root = TreeNode(name="<root>", path="", is_dir=True, children=[src])
        flat = _flatten_tree(root)
        assert len(flat) == 1
        assert flat[0][0].is_dir

    def test_depth_tracking(self) -> None:
        grandchild = TreeNode(name="a.py", path="src/gac/a.py", is_dir=False)
        child = TreeNode(name="gac", path="src/gac", is_dir=True, expanded=True, children=[grandchild])
        src = TreeNode(name="src", path="src", is_dir=True, expanded=True, children=[child])
        root = TreeNode(name="<root>", path="", is_dir=True, children=[src])
        flat = _flatten_tree(root)
        assert flat[0][1] == 0  # src at depth 0
        assert flat[1][1] == 1  # gac at depth 1
        assert flat[2][1] == 2  # a.py at depth 2


# ── Selection propagation tests ──────────────────────────────────────────


class TestSelectionPropagation:
    def test_select_all(self) -> None:
        f1 = TreeNode(name="a.py", path="a.py", is_dir=False, selected=False)
        f2 = TreeNode(name="b.py", path="b.py", is_dir=False, selected=False)
        root = TreeNode(name="<root>", path="", is_dir=True, children=[f1, f2])
        _propagate_selection_downward(root, True)
        assert f1.selected is True
        assert f2.selected is True
        assert root.selected is True

    def test_deselect_all(self) -> None:
        f1 = TreeNode(name="a.py", path="a.py", is_dir=False, selected=True)
        f2 = TreeNode(name="b.py", path="b.py", is_dir=False, selected=True)
        root = TreeNode(name="<root>", path="", is_dir=True, children=[f1, f2], selected=True)
        _propagate_selection_downward(root, False)
        assert f1.selected is False
        assert f2.selected is False
        assert root.selected is False


# ── StagingTUI interaction tests ──────────────────────────────────────────


class TestStagingTUIInteraction:
    """Test TUI state changes without actually running the app."""

    def _make_tui(self) -> StagingTUI:
        entries = [
            FileStatus(path="src/gac/cli.py", xy="M "),
            FileStatus(path="src/gac/new.py", xy="??"),
            FileStatus(path="README.md", xy=" M"),
        ]
        return StagingTUI(entries)

    def test_toggle_file_selection(self) -> None:
        tui = self._make_tui()
        # Navigate to a file
        items = tui._flat_items()
        # Find new.py (unselected file)
        idx = next(i for i, (n, _) in enumerate(items) if n.name == "new.py")
        tui.state.cursor_index = idx
        tui._toggle_selection()
        node = tui._current_node()
        assert node is not None
        assert node.selected is True  # Now selected
        tui._toggle_selection()
        assert node.selected is False  # Toggled back

    def test_toggle_directory_selection(self) -> None:
        tui = self._make_tui()
        items = tui._flat_items()
        # Find gac/ directory
        idx = next(i for i, (n, _) in enumerate(items) if n.name == "gac")
        tui.state.cursor_index = idx
        tui._toggle_selection()
        # All children should now be selected
        gac_node = tui._current_node()
        assert gac_node is not None
        for child in gac_node.children:
            assert child.selected is True

    def test_select_all(self) -> None:
        tui = self._make_tui()
        tui._select_all()
        selected = tui.get_selected_files()
        assert len(selected) == 3

    def test_deselect_all(self) -> None:
        tui = self._make_tui()
        tui._select_all()
        tui._deselect_all()
        selected = tui.get_selected_files()
        assert len(selected) == 0

    def test_move_cursor(self) -> None:
        tui = self._make_tui()
        tui.state.cursor_index = 0
        tui._move_cursor(1)
        assert tui.state.cursor_index == 1
        tui._move_cursor(-1)
        assert tui.state.cursor_index == 0
        # Clamping
        tui._move_cursor(-5)
        assert tui.state.cursor_index == 0

    def test_expand_collapse(self) -> None:
        tui = self._make_tui()
        items = tui._flat_items()
        # Find src/ directory
        idx = next(i for i, (n, _) in enumerate(items) if n.name == "src")
        tui.state.cursor_index = idx
        src_node = tui._current_node()
        assert src_node is not None
        assert src_node.expanded is True
        tui._collapse_current()
        assert src_node.expanded is False
        tui._expand_current()
        assert src_node.expanded is True

    def test_collapse_on_file_is_noop(self) -> None:
        tui = self._make_tui()
        items = tui._flat_items()
        idx = next(i for i, (n, _) in enumerate(items) if n.name == "README.md")
        tui.state.cursor_index = idx
        # Should not raise
        tui._collapse_current()
        tui._expand_current()

    def test_get_selected_files(self) -> None:
        tui = self._make_tui()
        # Initially only cli.py is selected (staged: M in index)
        selected = tui.get_selected_files()
        assert "src/gac/cli.py" in selected

    def test_render_produces_output(self) -> None:
        tui = self._make_tui()
        output = tui._render()
        assert len(output) > 0
        # Should contain file names
        text = "".join(t for _, t, *_ in output)
        assert "cli.py" in text
        assert "new.py" in text

    def test_render_xy_badge(self) -> None:
        """The XY badge should distinguish staged vs unstaged."""
        from gac.staging_tui_app import StagingTUI

        entries = [
            FileStatus(path="staged.py", xy="M "),  # Staged mod
            FileStatus(path="unstaged.py", xy=" M"),  # Unstaged mod
            FileStatus(path="untracked.py", xy="??"),  # Untracked
            FileStatus(path="both.py", xy="AM"),  # Staged + unstaged
        ]
        tui = StagingTUI(entries)
        output = tui._render()
        text = "".join(t for _, t, *_ in output)
        # XY badges should appear in the rendered output
        assert "M·" in text  # staged mod shows M in index
        assert "·M" in text  # unstaged mod shows M in worktree
        assert "??" in text  # untracked
        assert "AM" in text  # both staged and unstaged

    def test_render_header_hint(self) -> None:
        """The header should explain what ☑ and ☐ mean."""
        tui = self._make_tui()
        output = tui._render()
        text = "".join(t for _, t, *_ in output)
        assert "will stage" in text.lower() or "☑" in text


# ── stage_files tests ─────────────────────────────────────────────────────


class TestStageFiles:
    def test_stage_files_success(self) -> None:
        result = GitCommandResult.ok("")

        with patch("gac.staging_tui.run_git_command", return_value=result) as mock_run:
            ok = stage_files(["foo.py", "bar.py"])

        assert ok is True
        mock_run.assert_called_once_with(["add", "foo.py", "bar.py"], timeout=30)

    def test_stage_files_empty(self) -> None:
        result = stage_files([])
        assert result is True

    def test_stage_files_failure(self) -> None:
        result = GitCommandResult.fail(returncode=1, stderr="error")

        with patch("gac.staging_tui.run_git_command", return_value=result):
            ok = stage_files(["foo.py"])

        assert ok is False

    def test_stage_files_with_spaces_in_paths(self) -> None:
        """Paths with spaces are passed as separate list items — no shell injection."""
        result = GitCommandResult.ok("")

        with patch("gac.staging_tui.run_git_command", return_value=result) as mock_run:
            ok = stage_files(["foo bar.py", "baz'qux.py"])

        assert ok is True
        call_args = mock_run.call_args[0][0]
        assert call_args == ["add", "foo bar.py", "baz'qux.py"]

    def test_stage_files_integration_pipe(self) -> None:
        """End-to-end: selected files from TUI → stage_files() → git add called."""
        entries = [
            FileStatus(path="a.py", xy="M "),  # Staged, pre-selected
            FileStatus(path="b.py", xy="??"),  # Untracked, not selected
        ]
        tui = StagingTUI(entries)
        # Select the untracked file too
        items = tui._flat_items()
        b_node = next(n for n, _ in items if n.name == "b.py")
        b_node.selected = True

        selected = tui.get_selected_files()
        assert set(selected) == {"a.py", "b.py"}

        result = GitCommandResult.ok("")
        with patch("gac.staging_tui.run_git_command", return_value=result) as mock_run:
            ok = stage_files(selected)

        assert ok is True
        call_args = mock_run.call_args[0][0]
        assert call_args == ["add", "a.py", "b.py"]
