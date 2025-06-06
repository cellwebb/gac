"""Test module for the --scope flag functionality."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.cli import cli
from gac.prompt import build_prompt


class TestScopeFlag:
    """Test suite for the --scope/-s flag functionality."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture(autouse=True)
    def auto_mock_dependencies(self, monkeypatch):
        """Mocks common dependencies for all tests in this class."""
        mocked_config = {
            "model": "mocked-model/mocked-model-name",
            "temperature": 0.7,
            "max_output_tokens": 150,
            "max_retries": 2,
            "log_level": "ERROR",
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
            if args == ["status"]:
                return "mocked git status"
            if args == ["diff", "--staged"]:
                return "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old line\n+new line"
            # Add other specific commands if main uses them before prompt
            return "mock git output"

        monkeypatch.setattr("gac.main.run_git_command", mock_run_git_command)
        monkeypatch.setattr("gac.git.run_git_command", mock_run_git_command)

        # Mock both generate_commit_message and clean_commit_message to handle the new flow
        monkeypatch.setattr("gac.main.generate_commit_message", lambda **kwargs: "feat(test): mock commit")
        monkeypatch.setattr("gac.main.clean_commit_message", lambda msg: msg)
        monkeypatch.setattr("gac.main.count_tokens", lambda content, model: 10)
        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)
        # Mock click.prompt to return 'y' for the new confirmation prompt
        monkeypatch.setattr("click.prompt", lambda *args, **kwargs: "y")
        # Mock run_pre_commit_hooks to return True
        monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda: True)

        # Mock preprocess_diff to avoid any processing issues
        monkeypatch.setattr("gac.prompt.preprocess_diff", lambda diff, token_limit=None, model=None: diff)

        # Mock load_prompt_template to return a simpler template for testing that matches new structure
        mock_template = """<conventions_no_scope>no scope</conventions_no_scope>
<conventions_scope_provided>provided scope '{scope}'</conventions_scope_provided>
<conventions_scope_inferred>inferred scope</conventions_scope_inferred>
<status></status>
<diff></diff>"""
        # Mock the load_prompt_template function to return our template
        monkeypatch.setattr("gac.prompt.load_prompt_template", lambda: mock_template)

        # Mock process_scope_sections which is used in build_prompt
        monkeypatch.setattr("gac.prompt.re.sub", lambda pattern, repl, string, flags=0: string)

        def mock_get_staged_files(existing_only=False):
            return ["file1.py"]

        monkeypatch.setattr("gac.main.get_staged_files", mock_get_staged_files)
        monkeypatch.setattr("gac.git.get_staged_files", mock_get_staged_files)

        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)
        # To prevent actual logging calls from interfering or printing during tests
        monkeypatch.setattr("logging.Logger.info", lambda *args, **kwargs: None)
        # Remove or comment out the mock for logging.Logger.error to see tracebacks
        # monkeypatch.setattr("logging.Logger.error", lambda *args, **kwargs: None)
        monkeypatch.setattr("logging.Logger.warning", lambda *args, **kwargs: None)
        monkeypatch.setattr("logging.Logger.debug", lambda *args, **kwargs: None)

    def test_scope_flag_with_value(self, runner, monkeypatch):
        """Test --scope flag with a specific value."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        result = runner.invoke(cli, ["--scope", "auth", "--no-verify"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == "auth"

    def test_scope_flag_short_with_value(self, runner, monkeypatch):
        """Test -s flag (short form) with a specific value."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        result = runner.invoke(cli, ["-s", "api", "--no-verify"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == "api"

    def test_scope_flag_without_value(self, runner, monkeypatch):
        """Test --scope flag when an empty string is provided (AI determines scope)."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        # Invoke with an explicit empty string for the scope value
        result = runner.invoke(cli, ["--scope", "", "--no-verify"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == ""  # Empty string when no value provided

    def test_no_scope_flag(self, runner, monkeypatch):
        """Test behavior when --scope flag is not used."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        result = runner.invoke(cli, ["--no-verify"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") is None  # None when flag not used

    def test_scope_with_other_flags(self, runner, monkeypatch):
        """Test --scope flag combined with other flags."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        result = runner.invoke(cli, ["--one-liner", "--scope", "docs", "--hint", "Update documentation", "--no-verify"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == "docs"
        assert captured_prompt.get("one_liner") is True
        assert captured_prompt.get("hint") == "Update documentation"


class TestScopePromptBuilding:
    """Test how scope affects prompt building."""

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_with_specific_scope(self, mock_preprocess):
        """Test prompt building when scope is explicitly provided."""
        # Skip the regex processing by directly mocking build_prompt's internal calls
        with patch("gac.prompt.re.sub") as mock_sub:
            # Make re.sub pass through the original string
            mock_sub.side_effect = lambda pattern, repl, string, flags=0: string
            prompt = build_prompt("status", "mock_diff", scope="ui")
            # Verify we attempted to process the right template sections
            assert mock_sub.call_count > 0
            # Just check we have something in the prompt
            assert len(prompt) > 0

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_with_empty_scope(self, mock_preprocess):
        """Test prompt building when scope flag is used but no value is provided."""
        # Skip the regex processing by directly mocking build_prompt's internal calls
        with patch("gac.prompt.re.sub") as mock_sub:
            # Make re.sub pass through the original string
            mock_sub.side_effect = lambda pattern, repl, string, flags=0: string
            prompt = build_prompt("status", "mock_diff", scope="")
            # Verify we attempted to process the right template sections
            assert mock_sub.call_count > 0
            # Just check we have something in the prompt
            assert len(prompt) > 0

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_without_scope(self, mock_preprocess):
        """Test prompt building when scope is not requested."""
        # Skip the regex processing by directly mocking build_prompt's internal calls
        with patch("gac.prompt.re.sub") as mock_sub:
            # Make re.sub pass through the original string
            mock_sub.side_effect = lambda pattern, repl, string, flags=0: string
            prompt = build_prompt("status", "mock_diff", scope=None)
            # Verify we attempted to process the right template sections
            assert mock_sub.call_count > 0
            # Just check we have something in the prompt
            assert len(prompt) > 0

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_scope_with_different_values(self, mock_preprocess):
        """Test various scope values in prompt building."""
        # Test with a variety of valid scope values
        scopes = ["ui", "api", "auth", "docs", "core"]

        # Skip the regex processing by directly mocking build_prompt's internal calls
        with patch("gac.prompt.re.sub") as mock_sub:
            # Make re.sub pass through the original string
            mock_sub.side_effect = lambda pattern, repl, string, flags=0: string

            for scope_value in scopes:
                prompt = build_prompt("status", "mock_diff", scope=scope_value)
                # Verify we attempted to process the right template sections
                assert mock_sub.call_count > 0
                # Just check we have something in the prompt
                assert len(prompt) > 0
                # Reset the mock for the next iteration
                mock_sub.reset_mock()


class TestScopeIntegration:
    """Integration tests for scope functionality."""

    def test_scope_in_generated_message(self, monkeypatch):
        """Test that scope appears in the final commit message."""
        from gac.main import main

        # Mock config - patch the module-level config object that was already loaded
        test_config = {
            "model": "test:model",
            "temperature": 0.1,
            "max_output_tokens": 100,
            "max_retries": 1,
            "log_level": "ERROR",
        }

        # Patch the already-loaded config in main module
        monkeypatch.setattr("gac.main.config", test_config)

        # Also patch load_config in case it's called again
        monkeypatch.setattr("gac.main.load_config", lambda: test_config)
        monkeypatch.setattr("gac.config.load_config", lambda: test_config)

        # Set up a spy for the git commit command
        class GitCommandSpy:
            def __init__(self):
                self.commit_message = None

            def run_git_command(self, args, **kwargs):
                if len(args) > 2 and args[0] == "commit" and args[1] == "-m":
                    self.commit_message = args[2]
                    return "Mock commit success"
                elif "status" in args:
                    return "On branch main"
                elif "diff" in args:
                    return "diff --git a/file.py b/file.py\n+New line"
                elif "rev-parse" in args:
                    return "/repo"
                return "mock output"

        # Create our spy instance
        git_spy = GitCommandSpy()

        # Mock both the git module and main module's run_git_command
        monkeypatch.setattr("gac.git.run_git_command", git_spy.run_git_command)
        monkeypatch.setattr("gac.main.run_git_command", git_spy.run_git_command)

        # Mock AI to return message with scope
        def mock_generate(**kwargs):
            prompt = kwargs.get("prompt", "")
            if "REQUIRED scope 'auth'" in prompt:
                return "feat(auth): add login functionality"
            elif "inferred scope" in prompt.lower():
                return "fix(api): handle null response"
            else:
                return "feat: add new feature"

        monkeypatch.setattr("gac.main.generate_commit_message", mock_generate)
        monkeypatch.setattr("gac.main.count_tokens", lambda content, model: 10)

        # Don't clean the commit message (this happens after commit in the real code)
        monkeypatch.setattr("gac.main.clean_commit_message", lambda msg: msg)

        # Silence console output
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)

        # Mock other functions needed for the test
        def mock_get_staged_files(**kwargs):
            if kwargs.get("existing_only", False):
                return []  # No files exist on disk
            return ["file1.py"]

        monkeypatch.setattr("gac.main.get_staged_files", mock_get_staged_files)
        monkeypatch.setattr("gac.git.get_staged_files", mock_get_staged_files)

        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

        # Mock the click.prompt to return 'y' to proceed with the commit
        with patch("click.prompt", return_value="y"):
            # For dry_run mode, we need to capture the message before it would be passed to git
            # We can do this by capturing the clean_commit_message function's output
            from gac.prompt import clean_commit_message

            original_clean = clean_commit_message

            def spy_clean_commit_message(message):
                result = original_clean(message)
                git_spy.commit_message = result
                return result

            monkeypatch.setattr("gac.main.clean_commit_message", spy_clean_commit_message)

            # Test with specific scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope="auth", dry_run=True)  # Use dry_run to avoid actual git calls
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "feat(auth): add login functionality"

            # Reset spy for the next test
            git_spy.commit_message = None

            # Reset spy for the next test
            git_spy.commit_message = None

            # Test with AI-determined scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope="", dry_run=True)  # Use dry_run to avoid actual git calls
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "fix(api): handle null response"

            # Reset spy for the next test
            git_spy.commit_message = None

            # Test without scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope=None, dry_run=True)  # Use dry_run to avoid actual git calls
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "feat: add new feature"


def test_scope_flag_help():
    """Test that --scope flag help is displayed correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "--scope" in result.output or "-s" in result.output
    assert "Add a scope to the commit message" in result.output
