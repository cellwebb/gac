"""Test module for token usage display functionality."""

import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestTokenUsageDisplay:
    """Test suite for token usage display functionality."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_dependencies(self, monkeypatch):
        """Mock all dependencies needed for testing."""
        # Mock config
        mocked_config = {
            "model": "test:model",
            "temperature": 0.7,
            "max_output_tokens": 150,
            "max_retries": 2,
            "log_level": "ERROR",
        }
        monkeypatch.setattr("gac.main.load_config", lambda: mocked_config)
        monkeypatch.setattr("gac.main.config", mocked_config)

        # Mock git commands
        def mock_run_git_command(args, **kwargs):
            if args == ["rev-parse", "--show-toplevel"]:
                return "/mock/repo/path"
            if args == ["status"]:
                return "On branch main"
            if args == ["diff", "--staged"]:
                return "diff --git a/file.py b/file.py\n+New line"
            if args == ["commit", "-m", mock_run_git_command.last_commit_message]:
                return "mock commit"
            elif len(args) >= 3 and args[0] == "commit" and args[1] == "-m":
                mock_run_git_command.last_commit_message = args[2]
                return "mock commit"
            return "mock git output"

        mock_run_git_command.last_commit_message = None
        monkeypatch.setattr("gac.main.run_git_command", mock_run_git_command)
        monkeypatch.setattr("gac.git.run_git_command", mock_run_git_command)

        # Mock staged files
        def mock_get_staged_files(existing_only=False):
            return ["file.py"]

        monkeypatch.setattr("gac.main.get_staged_files", mock_get_staged_files)
        monkeypatch.setattr("gac.git.get_staged_files", mock_get_staged_files)

        # Mock clean_commit_message to return the message as-is
        monkeypatch.setattr("gac.main.clean_commit_message", lambda msg: msg)

        # Mock confirm to always return True
        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

        # Mock pre-commit hooks to succeed
        monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda: True)

    def test_estimated_token_usage_displayed(self, runner, mock_dependencies, monkeypatch):
        """Test that estimated token usage is displayed."""
        # Mock generate_commit_message
        monkeypatch.setattr("gac.main.generate_commit_message", lambda **kwargs: "feat: add new feature")

        # Mock count_tokens to return predictable values
        def mock_count_tokens(content, model):
            if len(content) > 100:  # Assume it's the prompt
                return 150
            else:  # It's the commit message
                return 10

        monkeypatch.setattr("gac.main.count_tokens", mock_count_tokens)

        # Capture console output
        captured_output = []

        def mock_console_print(self, *args, **kwargs):
            captured_output.append(str(args[0]) if args else "")

        monkeypatch.setattr("rich.console.Console.print", mock_console_print)

        # Run the command
        result = runner.invoke(cli, ["--yes", "--no-verify"])

        # Check that the command succeeded
        assert result.exit_code == 0

        # Check that estimated token usage was displayed
        output_text = "\n".join(captured_output)
        # Now we count both system and user prompts, so 150 + 150 = 300 for prompts
        assert "Token usage: 300 prompt + 10 completion = 310 total" in output_text

    def test_token_usage_not_displayed_when_quiet(self, runner, mock_dependencies, monkeypatch):
        """Test that token usage is not displayed in quiet mode."""
        # Mock generate_commit_message
        monkeypatch.setattr("gac.main.generate_commit_message", lambda **kwargs: "feat: add new feature")

        # Mock count_tokens
        monkeypatch.setattr("gac.main.count_tokens", lambda content, model: 100)

        # Capture console output
        captured_output = []

        def mock_console_print(self, *args, **kwargs):
            captured_output.append(str(args[0]) if args else "")

        monkeypatch.setattr("rich.console.Console.print", mock_console_print)

        # Run the command in quiet mode
        result = runner.invoke(cli, ["--yes", "--quiet", "--no-verify"])

        # Check that the command succeeded
        assert result.exit_code == 0

        # Check that token usage was NOT displayed
        output_text = "\n".join(captured_output)
        assert "Estimated token usage:" not in output_text
