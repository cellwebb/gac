from unittest.mock import patch

from click.testing import CliRunner

from gac.diff_cli import diff


class TestDiffLine151:
    """Test to hit line 151 in diff_cli.py."""

    @patch("gac.diff_cli._diff_implementation")
    def test_diff_function_max_tokens_line_151(self, mock_impl):
        """Test the diff function to hit line 151 (max_tokens parameter)."""
        # Use Click's CliRunner to test the CLI command properly
        runner = CliRunner()

        # Call the diff CLI command with --max-tokens to hit line 151
        result = runner.invoke(
            diff,
            [
                "--filter",
                "--truncate",
                "--max-tokens",
                "500",  # This will pass max_tokens=500 to line 151
                "--staged",
                "--color",
            ],
        )

        # Should execute successfully
        assert result.exit_code == 0

        # Verify _diff_implementation was called
        mock_impl.assert_called_once()
        call_kwargs = mock_impl.call_args[1]
        assert call_kwargs["max_tokens"] == 500
