from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.diff_cli import _diff_implementation, diff
from gac.errors import GitError


class TestDiffCLI:
    """Comprehensive tests for diff_cli.py."""

    def test_no_staged_changes_exit_direct(self):
        """Test exit when no staged changes found (line 54-57) - direct call."""
        with (
            patch("gac.diff_cli.get_staged_files") as mock_get_staged_files,
            patch("gac.diff_cli.print_message") as mock_print,
        ):
            mock_get_staged_files.return_value = []

            with pytest.raises(SystemExit) as exc_info:
                _diff_implementation(
                    filter=False,
                    truncate=False,
                    max_tokens=None,
                    staged=True,
                    color=False,
                    commit1=None,
                    commit2=None,
                )

            assert exc_info.value.code == 1
            mock_print.assert_called_once_with(
                "No staged changes found. Use 'git add' to stage changes.", level="error"
            )

    @patch("gac.diff_cli.get_staged_files")
    def test_has_staged_files_continues_direct(self, mock_get_staged_files):
        """Test continuation when staged changes exist - direct call."""
        mock_get_staged_files.return_value = ["file1.py", "file2.py"]

        with patch("gac.diff_cli.get_diff") as mock_get_diff, patch("builtins.print"):
            mock_get_diff.return_value = "diff content"

            _diff_implementation(
                filter=False,
                truncate=False,
                max_tokens=None,
                staged=True,
                color=False,
            )

            mock_get_diff.assert_called_once_with(staged=True, color=False, commit1=None, commit2=None)

    @patch("gac.diff_cli.get_diff")
    def test_no_changes_to_display_exit_direct(self, mock_get_diff):
        """Test exit when no changes to display (line 61) - direct call."""
        mock_get_diff.return_value = ""

        with patch("gac.diff_cli.print_message") as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                _diff_implementation(
                    filter=False,
                    truncate=False,
                    max_tokens=None,
                    staged=False,
                    color=False,
                )

            assert exc_info.value.code == 1
            mock_print.assert_called_once_with("No changes to display.", level="error")

    @patch("gac.diff_cli.get_diff")
    def test_git_error_handling_exit_direct(self, mock_get_diff):
        """Test GitError handling exit (lines 64-66) - direct call."""
        mock_get_diff.side_effect = GitError("Git command failed")

        with patch("gac.diff_cli.print_message") as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                _diff_implementation(
                    filter=False,
                    truncate=False,
                    max_tokens=None,
                    staged=False,
                    color=False,
                )

            assert exc_info.value.code == 1
            mock_print.assert_called_once_with("Error getting diff: Git command failed", level="error")

    @patch("gac.diff_cli.get_diff")
    @patch("gac.diff_cli.filter_binary_and_minified")
    def test_filter_removes_all_content_exit_direct(self, mock_filter, mock_get_diff):
        """Test exit when filtering removes all content (lines 70-73) - direct call."""
        mock_get_diff.return_value = "some diff content"
        mock_filter.return_value = ""  # Filter removes everything

        with patch("gac.diff_cli.print_message") as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                _diff_implementation(
                    filter=True,
                    truncate=False,
                    max_tokens=None,
                    staged=False,
                    color=False,
                )

            assert exc_info.value.code == 1
            mock_print.assert_called_once_with("No changes to display after filtering.", level="error")

    @patch("gac.diff_cli.get_diff")
    @patch("gac.diff_cli.filter_binary_and_minified")
    def test_filter_preserves_content_direct(self, mock_filter, mock_get_diff):
        """Test filter preserves content successfully - direct call."""
        mock_get_diff.return_value = "original diff"
        mock_filter.return_value = "filtered diff"

        with patch("builtins.print"):
            _diff_implementation(
                filter=True,
                truncate=False,
                max_tokens=None,
                staged=False,
                color=False,
            )

        mock_filter.assert_called_once_with("original diff")

    @patch("gac.diff_cli.get_diff")
    @patch("gac.diff_cli.split_diff_into_sections")
    @patch("gac.diff_cli.smart_truncate_diff")
    def test_truncate_with_string_diff_direct(self, mock_truncate, mock_split, mock_get_diff):
        """Test truncation with string diff (lines 77-84) - direct call."""
        mock_get_diff.return_value = "long diff content"
        mock_split.return_value = ["section1", "section2"]
        mock_truncate.return_value = "truncated diff"

        with patch("builtins.print"):
            _diff_implementation(
                filter=False,
                truncate=True,
                max_tokens=1000,
                staged=False,
                color=False,
            )

        mock_split.assert_called_once_with("long diff content")
        expected_sections = [("section1", 1.0), ("section2", 1.0)]
        mock_truncate.assert_called_once_with(expected_sections, 1000, "anthropic:claude-3-haiku-latest")

    @patch("gac.diff_cli.get_diff")
    @patch("gac.diff_cli.split_diff_into_sections")
    @patch("gac.diff_cli.smart_truncate_diff")
    def test_truncate_with_default_max_tokens_direct(self, mock_truncate, mock_split, mock_get_diff):
        """Test truncation with default max_tokens (line 83) - direct call."""
        mock_get_diff.return_value = "diff content"
        mock_split.return_value = ["section1"]
        mock_truncate.return_value = "truncated"

        with patch("builtins.print"):
            _diff_implementation(
                filter=False,
                truncate=True,
                max_tokens=None,  # Should default to 1000
                staged=False,
                color=False,
            )

        # Verify default max_tokens is used
        call_args = mock_truncate.call_args[0]
        assert call_args[1] == 1000

    @patch("gac.diff_cli.get_diff")
    def test_color_output_direct(self, mock_get_diff):
        """Test color output preservation (line 87) - direct call."""
        mock_get_diff.return_value = "\x1b[32m+new line\x1b[0m"

        with patch("builtins.print") as mock_print:
            _diff_implementation(
                filter=False,
                truncate=False,
                max_tokens=None,
                staged=False,
                color=True,
            )

        mock_print.assert_called_once_with("\x1b[32m+new line\x1b[0m")

    @patch("gac.diff_cli.get_diff")
    def test_no_color_output_stripping_direct(self, mock_get_diff):
        """Test ANSI color code stripping (lines 90-94) - direct call."""
        colored_diff = "\x1b[32m+new line\x1b[0m\x1b[31m-old line\x1b[0m"
        mock_get_diff.return_value = colored_diff

        with patch("builtins.print") as mock_print:
            _diff_implementation(
                filter=False,
                truncate=False,
                max_tokens=None,
                staged=False,
                color=False,
            )

        # Should strip ANSI codes
        mock_print.assert_called_once_with("+new line-old line")

    def test_commit_comparison_skips_staged_check_direct(self):
        """Test that commit comparison skips staged files check (lines 49-50) - direct call."""
        with patch("gac.diff_cli.get_diff") as mock_get_diff, patch("gac.diff_cli.get_staged_files") as mock_get_staged:
            mock_get_diff.return_value = "diff content"

            with patch("builtins.print"):
                _diff_implementation(
                    filter=False,
                    truncate=False,
                    max_tokens=None,
                    staged=True,
                    color=False,
                    commit1="commit1",
                    commit2="commit2",
                )

            # Should not call get_staged_files when commits are provided
            mock_get_staged.assert_not_called()
            mock_get_diff.assert_called_once_with(staged=True, color=False, commit1="commit1", commit2="commit2")

    def test_diff_function_max_tokens(self):
        """Test the diff function with max_tokens parameter."""
        with patch("gac.diff_cli.get_staged_files") as mock_get_staged, patch("gac.diff_cli.get_diff") as mock_get_diff:
            mock_get_staged.return_value = ["file1.py"]
            mock_get_diff.return_value = "diff content"

            runner = CliRunner()
            result = runner.invoke(
                diff,
                [
                    "--filter",
                    "--truncate",
                    "--max-tokens",
                    "500",
                    "--staged",
                    "--color",
                ],
            )
            assert result.exit_code == 0


class TestDiffLine151:
    """Test to hit line 151 in diff_cli.py (deprecated, kept for compatibility)."""

    def test_diff_function_max_tokens_line_151(self):
        """Test the diff function to hit line 151 (max_tokens parameter)."""
        with patch("gac.diff_cli.get_staged_files") as mock_get_staged, patch("gac.diff_cli.get_diff") as mock_get_diff:
            mock_get_staged.return_value = ["file1.py"]
            mock_get_diff.return_value = "diff content"

            runner = CliRunner()
            result = runner.invoke(
                diff,
                [
                    "--filter",
                    "--truncate",
                    "--max-tokens",
                    "500",
                    "--staged",
                    "--color",
                ],
            )
            assert result.exit_code == 0
            mock_get_staged.assert_called_once()
            mock_get_diff.assert_called_once()
            # Additional assertion to match line 151 context
            call_kwargs = mock_get_diff.call_args[1]
            assert call_kwargs["staged"] is True
