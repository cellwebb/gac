"""Test module for the --message-only flag functionality."""

import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestMessageOnlyFlag:
    """Test suite for the --message-only flag functionality."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture(autouse=True)
    def auto_mock_dependencies(self, monkeypatch):
        """Mocks common dependencies for all tests in this class."""
        mocked_config = {
            "model": "mocked:mocked-model-name",
            "temperature": 0.7,
            "max_output_tokens": 150,
            "max_retries": 2,
            "log_level": "ERROR",
            "warning_limit_tokens": 10000,
        }
        monkeypatch.setattr(
            "gac.main.load_config",
            lambda: mocked_config,
        )
        # Also patch the already-loaded config instance in gac.main
        monkeypatch.setattr("gac.main.config", mocked_config)

        def mock_run_git_command(args, **kwargs):
            if args == ["rev-parse", "--show-toplevel"]:
                return "/mock/repo/path"
            if args == ["add", "--all"]:
                return ""
            if args == ["diff", "--cached"]:
                return "diff --git a/test.py b/test.py\n@@ -1 +1 @@\n-old\n+new"
            if args == ["diff", "--stat", "--cached"]:
                return "test.py | 1 +"
            if args == ["commit", "-m", "test"]:
                return ""
            if args == ["status"]:
                return "On branch main\nChanges to be committed:\n  modified:   test.py"
            return "mock git output"

        monkeypatch.setattr("gac.git.run_git_command", mock_run_git_command)
        monkeypatch.setattr("gac.git_state_validator.run_git_command", mock_run_git_command)
        monkeypatch.setattr(
            "gac.git.get_staged_status", lambda: "On branch main\nChanges to be committed:\n  modified:   test.py"
        )

        # Mock generate_commit_message to return a predictable message
        def mock_generate_commit_message(**kwargs):
            return "feat: add new feature"

        monkeypatch.setattr("gac.main.generate_commit_message", mock_generate_commit_message)

        # Mock clean_commit_message
        monkeypatch.setattr("gac.main.clean_commit_message", lambda x: x)

        # Mock check_token_warning
        monkeypatch.setattr("gac.workflow_utils.check_token_warning", lambda *args, **kwargs: True)

        # Mock scan_staged_diff
        monkeypatch.setattr("gac.security.scan_staged_diff", lambda x: [])

        # Mock run_lefthook_hooks and run_pre_commit_hooks
        monkeypatch.setattr("gac.main.run_lefthook_hooks", lambda *args, **kwargs: True)
        monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda *args, **kwargs: True)

        # Mock preprocess_diff
        monkeypatch.setattr("gac.preprocess.preprocess_diff", lambda *args, **kwargs: "diff content")

        # Mock build_prompt
        monkeypatch.setattr("gac.prompt.build_prompt", lambda *args, **kwargs: ("system", "user"))

        def mock_count_tokens(*args, **kwargs):
            return 100

        monkeypatch.setattr("gac.main.count_tokens", mock_count_tokens)

    def test_message_only_flag_works(self, runner, monkeypatch):
        """Test that --message-only flag outputs only the commit message."""
        result = runner.invoke(cli, ["--message-only", "--yes"])

        assert result.exit_code == 0
        assert "feat: add new feature" in result.output
        # Should not contain any formatting or additional text
        assert "\u2713" not in result.output  # No checkmarks
        assert "\u25cf" not in result.output  # No bullets
        assert "Token usage" not in result.output
        assert "Generating" not in result.output

    def test_message_only_with_one_liner(self, runner, monkeypatch):
        """Test --message-only works with --one-liner flag."""
        result = runner.invoke(cli, ["--message-only", "--one-liner", "--yes"])

        assert result.exit_code == 0
        assert "feat: add new feature" in result.output
        # Should be a single line without extra formatting
        lines = [line.strip() for line in result.output.strip().split("\n") if line.strip()]
        assert len(lines) <= 2  # Allow for empty lines

    def test_message_only_quiet_propagation(self, runner, monkeypatch):
        """Test that --message-only properly suppresses spinner output."""
        # This test ensures that quiet=True is passed to generate_commit_message when message_only=True
        captured_quiet_values = []

        def mock_generate_commit_message_with_quiet_check(**kwargs):
            captured_quiet_values.append(kwargs.get("quiet", False))
            return "feat: test quiet propagation"

        monkeypatch.setattr("gac.main.generate_commit_message", mock_generate_commit_message_with_quiet_check)

        result = runner.invoke(cli, ["--message-only", "--yes"])

        assert result.exit_code == 0
        # Verify that quiet was True when generating the message
        assert True in captured_quiet_values

    def test_message_only_bypasses_confirmation(self, runner, monkeypatch):
        """Test that --message-only bypasses confirmation prompts."""
        result = runner.invoke(cli, ["--message-only"])  # Without --yes

        assert result.exit_code == 0
        assert "feat: add new feature" in result.output
        # Should not ask for confirmation
        assert "Proceed" not in result.output
        assert "[y/n" not in result.output

    def test_message_only_mutually_exclusive_with_group(self, runner):
        """Test that --message-only and --group cannot be used together."""
        result = runner.invoke(cli, ["--message-only", "--group", "--yes"])

        assert result.exit_code == 1
        assert "Error: --message-only and --group options are mutually exclusive" in result.output
        assert "--message-only is for generating a single commit message for external use" in result.output
        assert "--group is for organizing multiple commits within the current workflow" in result.output

    def test_message_only_order_independence(self, runner):
        """Test that mutual exclusion works regardless of flag order."""
        # Test different flag orders
        result1 = runner.invoke(cli, ["--message-only", "--group", "--yes"])
        result2 = runner.invoke(cli, ["--group", "--message-only", "--yes"])

        assert result1.exit_code == 1
        assert result2.exit_code == 1
        assert "mutually exclusive" in result1.output
        assert "mutually exclusive" in result2.output

    def test_message_only_without_staged_files(self, runner, monkeypatch):
        """Test --message-only behavior when no files are staged."""

        def mock_run_git_command_empty(args, **kwargs):
            if args == ["rev-parse", "--show-toplevel"]:
                return "/mock/repo/path"
            if args == ["add", "--all"]:
                return ""
            if args == ["diff", "--cached"]:
                return ""
            return ""

        monkeypatch.setattr("gac.git.run_git_command", mock_run_git_command_empty)
        monkeypatch.setattr("gac.git_state_validator.run_git_command", mock_run_git_command_empty)

        def mock_get_staged_files(**kwargs):
            return []

        monkeypatch.setattr("gac.git.get_staged_files", mock_get_staged_files)

        result = runner.invoke(cli, ["--message-only", "--yes"])

        # Should exit with 0 but show the no staged files message
        assert result.exit_code == 0
        assert "No staged changes found" in result.output

    def test_message_only_with_various_combinations(self, runner, monkeypatch):
        """Test --message-only works correctly with other non-conflicting flags."""
        # Test with --add-all
        result1 = runner.invoke(cli, ["--add-all", "--message-only", "--yes"])
        assert result1.exit_code == 0
        assert "feat: add new feature" in result1.output

        # Test with --scope
        result2 = runner.invoke(cli, ["--message-only", "--scope", "--yes"])
        assert result2.exit_code == 0
        assert "feat: add new feature" in result2.output

        # Test with --hint
        result3 = runner.invoke(cli, ["--message-only", "--hint", "test hint", "--yes"])
        assert result3.exit_code == 0
        assert "feat: add new feature" in result3.output

    def test_message_only_help_text(self, runner):
        """Test that --message-only appears in help text."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "--message-only" in result.output
        assert "Output only the generated commit message" in result.output
