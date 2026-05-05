from unittest.mock import MagicMock, patch

import pytest

from gac.staging_tui import FileStatus, build_file_tree, parse_git_status, stage_files


class TestFileStatus:
    def test_staged_modification(self) -> None:
        fs = FileStatus(path="foo.py", xy="M ")
        assert fs.is_staged is True
        assert fs.is_untracked is False
        assert fs.display_status == "M"

    def test_unstaged_modification(self) -> None:
        fs = FileStatus(path="foo.py", xy=" M")
        assert fs.is_staged is False
        assert fs.display_status == "M"

    def test_untracked(self) -> None:
        fs = FileStatus(path="foo.py", xy="??")
        assert fs.is_staged is False
        assert fs.is_untracked is True
        assert fs.display_status == "??"

    def test_added_then_modified(self) -> None:
        fs = FileStatus(path="foo.py", xy="AM")
        assert fs.is_staged is True
        assert fs.display_status == "A"


class TestParseGitStatus:
    def test_parse_basic_output(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "M  src/foo.py\n A src/bar.py\n?? src/baz.py\n"
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result):
            entries = parse_git_status()
        assert len(entries) == 3
        assert entries[0].path == "src/foo.py"
        assert entries[0].xy == "M "
        assert entries[2].xy == "??"

    def test_parse_rename(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "R  old.py -> new.py\n"
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result):
            entries = parse_git_status()
        assert entries[0].path == "new.py"

    def test_parse_empty_output(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result):
            assert parse_git_status() == []

    def test_parse_git_failure(self) -> None:
        from gac.errors import GitError

        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stderr = "not a git repository"
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result):
            with pytest.raises(GitError):
                parse_git_status()


class TestBuildFileTree:
    def test_flat_files_sorted(self) -> None:
        entries = [FileStatus("foo.py", "M "), FileStatus("bar.py", "??")]
        tree = build_file_tree(entries)
        names = list(tree)
        assert names == ["bar.py", "foo.py"]

    def test_nested_directories(self) -> None:
        entries = [FileStatus("src/a.py", "M "), FileStatus("src/b.py", " M")]
        tree = build_file_tree(entries)
        assert "src" in tree
        assert list(tree["src"].keys()) == ["a.py", "b.py"]

    def test_pre_selected_staged_files(self) -> None:
        entries = [FileStatus("staged.py", "M "), FileStatus("unstaged.py", " M")]
        tree = build_file_tree(entries)
        assert tree["staged.py"].is_staged is True
        assert tree["unstaged.py"].is_staged is False

    def test_dirs_before_files(self) -> None:
        entries = [FileStatus("README.md", "??"), FileStatus("src/a.py", "M ")]
        tree = build_file_tree(entries)
        keys = list(tree.keys())
        assert keys[0] == "src"


class TestStageFiles:
    def test_success(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result) as m:
            assert stage_files(["foo.py", "bar.py"]) is True
        assert m.call_args[0][0] == ["git", "add", "foo.py", "bar.py"]

    def test_empty_list(self) -> None:
        assert stage_files([]) is True

    def test_failure(self) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error"
        with patch("gac.staging_tui.subprocess.run", return_value=mock_result):
            assert stage_files(["foo.py"]) is False


class TestStagingApp:
    """Tests for the Textual StagingApp — runs headlessly."""

    def _entries(self) -> list[FileStatus]:
        return [
            FileStatus("src/gac/cli.py", "M "),
            FileStatus("src/gac/new.py", "??"),
            FileStatus("README.md", " M"),
        ]

    @pytest.mark.asyncio
    async def test_initially_staged_files_are_selected(self) -> None:
        from gac.staging_tui import StagingApp

        app = StagingApp(self._entries())
        async with app.run_test() as pilot:
            await pilot.pause()
        assert "src/gac/cli.py" in (app.return_value or [])
        assert "src/gac/new.py" not in (app.return_value or [])

    @pytest.mark.asyncio
    async def test_enter_returns_selected_files(self) -> None:
        from gac.staging_tui import StagingApp

        app = StagingApp(self._entries())
        async with app.run_test() as pilot:
            await pilot.press("enter")
        assert isinstance(app.return_value, list)

    @pytest.mark.asyncio
    async def test_quit_returns_none(self) -> None:
        from gac.staging_tui import StagingApp

        app = StagingApp(self._entries())
        async with app.run_test() as pilot:
            await pilot.press("q")
        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_select_all_then_confirm(self) -> None:
        from gac.staging_tui import StagingApp

        app = StagingApp(self._entries())
        async with app.run_test() as pilot:
            await pilot.press("a")
            await pilot.press("enter")
        result = app.return_value
        assert result is not None
        assert sorted(result) == sorted(["src/gac/cli.py", "src/gac/new.py", "README.md"])

    @pytest.mark.asyncio
    async def test_deselect_all_then_confirm(self) -> None:
        from gac.staging_tui import StagingApp

        app = StagingApp(self._entries())
        async with app.run_test() as pilot:
            await pilot.press("A")
            await pilot.press("enter")
        assert app.return_value == []
