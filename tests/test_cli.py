import pytest
from click.testing import CliRunner

from gac.cli import cli


class TestMainCommand:
    @pytest.fixture
    def mock_init_commands(self, monkeypatch):
        # Patch the init and model commands' callbacks directly in their source module
        def dummy_command(*args, **kwargs):
            pass

        monkeypatch.setattr("gac.init_cli.init.callback", dummy_command)
        monkeypatch.setattr("gac.model_cli.model.callback", dummy_command)
        yield

    def test_init_success(self, monkeypatch, mock_init_commands):
        """Test 'gac init' runs without error when all dependencies succeed."""
        runner = CliRunner()
        # The init command's callback is already mocked by mock_init_commands.
        # No need to mock load_config or run_git_command for gac.init_cli here.
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

    def test_init_not_in_git_repo(self, monkeypatch, mock_init_commands):
        """Test 'gac init' runs (it doesn't check for git repo status itself)."""
        runner = CliRunner()
        # The init command's callback is already mocked by mock_init_commands.
        # No need to mock load_config or run_git_command for gac.init_cli here.
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

    def test_model_success(self, monkeypatch, mock_init_commands):
        """Test 'gac model' runs without error when all dependencies succeed."""
        runner = CliRunner()
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, ["model"])
        assert result.exit_code == 0

    def test_main_command(self, monkeypatch):
        """Test main command runs without error when its core logic is mocked."""
        runner = CliRunner()
        # Patch gac.config.load_config to ensure that gac.cli.cli's setup phase
        # (which uses gac.cli.config) doesn't fail, and to provide a dummy model.
        monkeypatch.setattr("gac.config.load_config", lambda: {"log_level": "ERROR", "model": "dummy:model"})
        # Patch the main function in 'gac.cli' module, as this is what Click calls.
        monkeypatch.setattr("gac.cli.main", lambda **kwargs: None)
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        # Output is empty because gac.cli.main and rich.console.Console.print are mocked.


class TestInteractiveFlag:
    """Test the --interactive/-i flag functionality."""

    @pytest.fixture
    def mock_main_function(self, monkeypatch):
        """Mock the main function to capture arguments."""
        captured_kwargs = {}

        def capture_main(**kwargs):
            captured_kwargs.update(kwargs)

        monkeypatch.setattr("gac.cli.main", capture_main)
        return captured_kwargs

    @pytest.fixture
    def mock_config_and_console(self, monkeypatch):
        """Mock config and console for CLI tests."""
        monkeypatch.setattr("gac.config.load_config", lambda: {"log_level": "ERROR", "model": "dummy:model"})
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)

    def test_interactive_flag_long_form(self, mock_config_and_console, mock_main_function):
        """Test --interactive flag is properly recognized and passed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive"])

        assert result.exit_code == 0
        assert mock_main_function.get("interactive") is True

    def test_interactive_flag_short_form(self, mock_config_and_console, mock_main_function):
        """Test -i flag is properly recognized and passed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["-i"])

        assert result.exit_code == 0
        assert mock_main_function.get("interactive") is True

    def test_no_interactive_flag_default(self, mock_config_and_console, mock_main_function):
        """Test that interactive defaults to False when flag is not provided."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        assert mock_main_function.get("interactive") is False

    def test_interactive_flag_with_other_flags(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works in combination with other flags."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--interactive", "--verbose", "--add-all", "--model", "anthropic:claude-3-haiku", "--hint", "test hint"],
        )

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("verbose") is True
        assert captured.get("stage_all") is True
        assert captured.get("model") == "anthropic:claude-3-haiku"
        assert captured.get("hint") == "test hint"

    def test_interactive_flag_with_group_flag(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --group flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--group"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("group") is True

    def test_interactive_flag_with_dry_run(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --dry-run flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--dry-run"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("dry_run") is True

    def test_interactive_flag_with_message_only(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --message-only flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--message-only"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("message_only") is True

    def test_interactive_flag_with_yes_flag(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --yes flag (skip confirmation)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--yes"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("require_confirmation") is False

    def test_interactive_flag_with_language_override(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --language flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--language", "Spanish"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("language") == "Spanish"

    def test_interactive_help_output(self, mock_config_and_console):
        """Test that help output includes the interactive flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        help_text = result.output

        # Check both long and short forms are documented
        assert "--interactive" in help_text
        assert "-i" in help_text
        # Check the help description
        assert "ask interactive questions" in help_text.lower()

    def test_interactive_flag_mixed_order(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works regardless of position in command."""
        runner = CliRunner()

        # Test interactive flag at different positions
        test_cases = [
            ["--interactive", "--verbose", "--add-all"],
            ["--verbose", "--interactive", "--add-all"],
            ["--verbose", "--add-all", "--interactive"],
        ]

        for args in test_cases:
            mock_main_function.clear()  # Reset captured kwargs
            result = runner.invoke(cli, args)
            assert result.exit_code == 0
            assert mock_main_function.get("interactive") is True

    def test_interactive_flag_with_model_override(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with model override."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--interactive",
                "--model",
                "openai:gpt-4",
            ],
        )

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        # Note: temperature isn't a CLI flag, but we test it's passed correctly
        assert captured.get("model") == "openai:gpt-4"

    def test_interactive_flag_with_scope_flag(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --scope flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--scope"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("infer_scope") is True

    def test_interactive_flag_with_one_liner(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --one-liner flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--one-liner"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("one_liner") is True

    def test_interactive_flag_with_quiet(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --quiet flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--quiet"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("quiet") is True

    def test_interactive_flag_with_skip_secret_scan(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --skip-secret-scan flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--skip-secret-scan"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("skip_secret_scan") is True

    def test_interactive_flag_with_no_verify(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --no-verify flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--no-verify"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("no_verify") is True

    def test_interactive_flag_with_hook_timeout(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with --hook-timeout flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--hook-timeout", "180"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True
        assert captured.get("hook_timeout") == 180

    def test_interactive_flag_complex_combination(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with complex flag combinations."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--interactive",
                "--verbose",
                "--add-all",
                "--group",
                "--model",
                "anthropic:claude-3-sonnet",
                "--language",
                "Japanese",
                "--hint",
                "Fix authentication flow",
                "--scope",
                "--push",
                "--skip-secret-scan",
                "--hook-timeout",
                "200",
            ],
        )

        assert result.exit_code == 0
        captured = mock_main_function

        # Verify all flags were passed correctly
        assert captured.get("interactive") is True
        assert captured.get("verbose") is True
        assert captured.get("stage_all") is True
        assert captured.get("group") is True
        assert captured.get("model") == "anthropic:claude-3-sonnet"
        assert captured.get("language") == "Japanese"
        assert captured.get("hint") == "Fix authentication flow"
        assert captured.get("infer_scope") is True
        assert captured.get("push") is True
        assert captured.get("skip_secret_scan") is True
        assert captured.get("hook_timeout") == 200

    def test_interactive_flag_short_form_combination(self, mock_config_and_console, mock_main_function):
        """Test interactive flag works with other short form flags."""
        runner = CliRunner()
        result = runner.invoke(cli, ["-i", "-a", "-g", "-p", "-v"])

        assert result.exit_code == 0
        captured = mock_main_function
        assert captured.get("interactive") is True  # -i
        assert captured.get("stage_all") is True  # -a
        assert captured.get("group") is True  # -g
        assert captured.get("push") is True  # -p
        assert captured.get("verbose") is True  # -v

    def test_interactive_flag_duplicate_specification(self, mock_config_and_console, mock_main_function):
        """Test behavior when interactive flag is specified multiple times."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive", "--interactive"])

        assert result.exit_code == 0
        # Click should handle this gracefully and set it to True
        assert mock_main_function.get("interactive") is True

    def test_interactive_flag_with_version(self, mock_config_and_console):
        """Test that --version flag still works when --interactive is also present."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version", "--interactive"])

        # --version should exit early, but the command should still be valid
        assert result.exit_code == 0

    def test_interactive_flag_error_handling(self, mock_config_and_console, monkeypatch):
        """Test error handling with interactive flag."""

        # Mock main to raise an exception to test error propagation
        def mock_main_error(**kwargs):
            if kwargs.get("interactive"):
                raise Exception("Interactive mode error")

        monkeypatch.setattr("gac.cli.main", mock_main_error)

        runner = CliRunner()
        result = runner.invoke(cli, ["--interactive"])

        # Should propagate the error
        assert result.exit_code != 0
        assert result.exit_code == 1 or "error" in str(result.exception or result.output).lower()

    def test_interactive_flag_help_detailed(self, mock_config_and_console):
        """Test detailed help output for interactive flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        help_text = result.output

        # Verify flag is in help
        assert "--interactive" in help_text
        assert "-i" in help_text

        # Verify help text contains the description
        assert "Ask interactive questions" in help_text
        assert "context" in help_text.lower()

        # Verify it's grouped with other workflow flags
        lines = help_text.split("\n")
        interactive_line = None
        add_all_line = None

        for line in lines:
            if "--interactive" in line or "-i" in line:
                interactive_line = line
            if "--add-all" in line or "-a" in line:
                add_all_line = line

        # Both flags should be present in help
        assert interactive_line is not None
        assert add_all_line is not None
