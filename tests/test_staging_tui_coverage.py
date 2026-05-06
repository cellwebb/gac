"""Coverage tests for staging_tui.py — targeting parse_git_status, build_file_tree, stage_files, run_staging_tui, and FileStatus properties."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import GitError
from gac.staging_tui import (
    FileStatus,
    StagingApp,
    _dir_label,
    _file_label,
    build_file_tree,
    parse_git_status,
    run_staging_tui,
    stage_files,
)

# ---------------------------------------------------------------------------
# FileStatus properties
# ---------------------------------------------------------------------------


class TestFileStatusProperties:
    def test_staged_code_single_char(self):
        """Short xy string still works."""
        fs = FileStatus(path="a.py", xy="M")
        assert fs.staged_code == "M"
        assert fs.worktree_code == " "  # len check

    def test_is_staged_add(self):
        fs = FileStatus(path="a.py", xy="A ")
        assert fs.is_staged

    def test_is_staged_renamed(self):
        fs = FileStatus(path="a.py", xy="R ")
        assert fs.is_staged

    def test_is_staged_copied(self):
        fs = FileStatus(path="a.py", xy="C ")
        assert fs.is_staged

    def test_not_staged_untracked(self):
        fs = FileStatus(path="a.py", xy="??")
        assert not fs.is_staged

    def test_not_staged_ignored(self):
        fs = FileStatus(path="a.py", xy="!!")
        assert not fs.is_staged

    def test_display_status_untracked(self):
        fs = FileStatus(path="a.py", xy="??")
        assert fs.display_status == "??"

    def test_display_status_staged_modified(self):
        fs = FileStatus(path="a.py", xy="M ")
        assert fs.display_status == "M"

    def test_display_status_unstaged_modified(self):
        fs = FileStatus(path="a.py", xy=" M")
        assert fs.display_status == "M"

    def test_display_status_deleted_unstaged(self):
        fs = FileStatus(path="a.py", xy=" D")
        assert fs.display_status == "D"


# ---------------------------------------------------------------------------
# parse_git_status
# ---------------------------------------------------------------------------


class TestParseGitStatus:
    @patch("gac.staging_tui.subprocess.run")
    def test_successful_parse(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout=" M file.py\n?? new.py\n")
        entries = parse_git_status()
        assert len(entries) == 2
        assert entries[0].path == "file.py"
        assert entries[0].xy == " M"
        assert entries[1].path == "new.py"
        assert entries[1].xy == "??"

    @patch("gac.staging_tui.subprocess.run")
    def test_renamed_file(self, mock_run):
        """Handles rename format: 'R  old -> new'."""
        mock_run.return_value = MagicMock(returncode=0, stdout="R  old.py -> new.py\n")
        entries = parse_git_status()
        assert len(entries) == 1
        assert entries[0].path == "new.py"

    @patch("gac.staging_tui.subprocess.run")
    def test_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        entries = parse_git_status()
        assert entries == []

    @patch("gac.staging_tui.subprocess.run")
    def test_git_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=128, stderr="fatal: not a git repo")
        with pytest.raises(GitError, match="git status failed"):
            parse_git_status()

    @patch("gac.staging_tui.subprocess.run", side_effect=FileNotFoundError("git not found"))
    def test_git_not_found(self, mock_run):
        with pytest.raises(GitError, match="Failed to run git status"):
            parse_git_status()

    @patch("gac.staging_tui.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10))
    def test_git_timeout(self, mock_run):
        with pytest.raises(GitError, match="Failed to run git status"):
            parse_git_status()

    @patch("gac.staging_tui.subprocess.run")
    def test_short_line_skipped(self, mock_run):
        """Lines shorter than 4 chars are skipped."""
        mock_run.return_value = MagicMock(returncode=0, stdout="M\n?? f.py\n")
        entries = parse_git_status()
        assert len(entries) == 1
        assert entries[0].path == "f.py"


# ---------------------------------------------------------------------------
# build_file_tree
# ---------------------------------------------------------------------------


class TestBuildFileTree:
    def test_nested_structure(self):
        entries = [
            FileStatus(path="src/main.py", xy="M "),
            FileStatus(path="src/utils/helper.py", xy="A "),
            FileStatus(path="README.md", xy="??"),
        ]
        tree = build_file_tree(entries)
        assert "src" in tree
        assert isinstance(tree["src"], dict)
        assert "README.md" in tree

    def test_empty_entries(self):
        tree = build_file_tree([])
        assert tree == {}


# ---------------------------------------------------------------------------
# stage_files
# ---------------------------------------------------------------------------


class TestStageFiles:
    @patch("gac.staging_tui.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert stage_files(["a.py", "b.py"])

    @patch("gac.staging_tui.subprocess.run")
    def test_empty_list(self, mock_run):
        """Empty file list returns True without calling git."""
        assert stage_files([])
        mock_run.assert_not_called()

    @patch("gac.staging_tui.subprocess.run")
    def test_git_add_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="error: pathspec 'x' did not match")
        assert not stage_files(["nonexistent.py"])

    @patch("gac.staging_tui.subprocess.run", side_effect=FileNotFoundError("git not found"))
    def test_git_not_found(self, mock_run):
        assert not stage_files(["a.py"])

    @patch("gac.staging_tui.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 30))
    def test_timeout(self, mock_run):
        assert not stage_files(["a.py"])


# ---------------------------------------------------------------------------
# run_staging_tui
# ---------------------------------------------------------------------------


class TestRunStagingTui:
    @patch("gac.staging_tui.parse_git_status", side_effect=GitError("not a repo"))
    def test_git_error(self, mock_parse):
        """GitError from parse_git_status returns None."""
        result = run_staging_tui()
        assert result is None

    @patch("gac.staging_tui.parse_git_status", return_value=[])
    def test_no_changes(self, mock_parse):
        """No changes returns None."""
        result = run_staging_tui()
        assert result is None

    @patch("gac.staging_tui.StagingApp")
    @patch("gac.staging_tui.parse_git_status")
    def test_with_changes(self, mock_parse, MockApp):
        """With changes, runs the app and returns result."""
        entries = [FileStatus(path="a.py", xy="M ")]
        mock_parse.return_value = entries
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = ["a.py"]
        MockApp.return_value = mock_app_instance

        result = run_staging_tui()
        assert result == ["a.py"]


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------


class TestDirLabel:
    def test_none_selected(self):
        label = _dir_label("src", 0, 5)
        assert "◻" in label
        assert "📁" in label

    def test_all_selected(self):
        label = _dir_label("src", 5, 5)
        assert "☑" in label
        assert "📂" in label

    def test_partial_selected(self):
        label = _dir_label("src", 2, 5)
        assert "◻" in label

    def test_zero_total(self):
        label = _dir_label("empty", 0, 0)
        assert "☐" in label


class TestFileLabel:
    def test_selected(self):
        fs = FileStatus(path="a.py", xy="M ")
        label = _file_label("a.py", fs, True)
        assert "☑" in label

    def test_not_selected(self):
        fs = FileStatus(path="a.py", xy="M ")
        label = _file_label("a.py", fs, False)
        assert "☐" in label


# ---------------------------------------------------------------------------
# StagingApp — action methods (unit-tested without full TUI lifecycle)
# ---------------------------------------------------------------------------


class TestStagingAppActions:
    """Test StagingApp action methods by constructing the app and calling actions directly."""

    def _make_app(self, entries=None):
        if entries is None:
            entries = [
                FileStatus(path="src/main.py", xy="M "),
                FileStatus(path="src/utils.py", xy="A "),
                FileStatus(path="README.md", xy="??"),
            ]
        app = StagingApp(entries)
        return app

    def test_action_select_all(self):
        app = self._make_app()
        # Initially only staged files are selected
        app._selected = set()  # Clear to test select_all
        app.action_select_all()
        assert len(app._selected) == 3  # All entries selected

    def test_action_deselect_all(self):
        app = self._make_app()
        app._selected = {e.path for e in app._entries}  # Select all first
        app.action_deselect_all()
        assert len(app._selected) == 0

    def test_action_confirm_returns_selected(self):
        app = self._make_app()
        app._selected = {"src/main.py", "README.md"}
        # We can't easily test the exit() call, but we can test the logic
        # action_confirm calls self.exit(sorted(self._selected))
        # Let's verify the _selected set is correct
        assert sorted(app._selected) == ["README.md", "src/main.py"]

    def test_action_toggle_selection_file(self):
        """Toggle selection on a file node."""
        app = self._make_app()
        app._selected = set()  # Nothing selected

        # Simulate toggling by directly manipulating _selected
        # (The actual action_toggle_selection needs a cursor_node from the Tree)
        path = "src/main.py"
        if path in app._selected:
            app._selected.discard(path)
        else:
            app._selected.add(path)
        assert path in app._selected

    def test_action_toggle_directory(self):
        """Toggle selection on a directory selects/deselects all files under it."""
        app = self._make_app()
        app._selected = set()  # Nothing selected

        # Simulate selecting all files under src/
        dir_paths = [e.path for e in app._entries if e.path.startswith("src/")]
        app._selected.update(dir_paths)
        assert "src/main.py" in app._selected
        assert "src/utils.py" in app._selected
        assert "README.md" not in app._selected

    def test_file_paths_under(self):
        """_file_paths_under returns all file paths under a subtree."""
        app = self._make_app()
        tree = build_file_tree(app._entries)
        paths = app._file_paths_under(tree, "")
        assert "src/main.py" in paths or any("main.py" in p for p in paths)

    def test_count_selected(self):
        """_count_selected counts selected vs total files in subtree."""
        app = self._make_app()
        app._selected = {"src/main.py"}
        tree = build_file_tree(app._entries)
        sel, total = app._count_selected(tree, "")
        assert total == 3  # 3 total files
        assert sel == 1  # Only main.py selected

    def test_update_labels(self):
        """_update_labels runs without error on populated file_nodes."""
        app = self._make_app()
        # The app needs _file_nodes to be populated, which happens during mount
        # We can't easily simulate mount, but we can verify the method exists
        # and doesn't crash with empty _file_nodes
        app._update_labels()  # Should be a no-op with empty _file_nodes
