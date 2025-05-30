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

        monkeypatch.setattr("gac.main.generate_commit_message", lambda **kwargs: "feat(test): mock commit")
        monkeypatch.setattr("gac.main.count_tokens", lambda content, model: 10)
        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

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

        result = runner.invoke(cli, ["--scope", "auth"])

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

        result = runner.invoke(cli, ["-s", "api"])

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
        result = runner.invoke(cli, ["--scope", ""])

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

        result = runner.invoke(cli, [])

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

        result = runner.invoke(cli, ["--one-liner", "--scope", "docs", "--hint", "Update documentation"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == "docs"
        assert captured_prompt.get("one_liner") is True
        assert captured_prompt.get("hint") == "Update documentation"


class TestScopePromptBuilding:
    """Test how scope affects prompt building."""

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_with_specific_scope(self, mock_preprocess):
        """Test prompt building with a specific scope value."""
        prompt = build_prompt("status", "diff", scope="auth")
        # Check that the scope instruction is customized
        assert "The user specified the scope to be 'auth'" in prompt
        assert "Please include this exact scope in parentheses after the type" in prompt
        assert "fix(auth):" in prompt  # Example format should be shown

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_with_empty_scope(self, mock_preprocess):
        """Test prompt building when user wants AI to determine scope."""
        prompt = build_prompt("status", "diff", scope="")
        # Check that the scope instruction asks AI to determine scope
        assert "The user requested to include a scope in the commit message" in prompt
        assert "Please determine and include the most appropriate scope" in prompt

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_build_prompt_without_scope(self, mock_preprocess):
        """Test prompt building when scope is not requested."""
        prompt = build_prompt("status", "diff", scope=None)
        # Check that scope instructions are removed
        assert "The user specified the scope to be" not in prompt
        assert "The user requested to include a scope" not in prompt
        # When scope is None, the entire scope_instructions section is removed
        assert "feat(auth): add login functionality" not in prompt
        assert "fix(api): handle null response" not in prompt
        # But the conventions section still mentions scope usage

    @patch("gac.prompt.preprocess_diff", return_value="mock_diff")
    def test_scope_with_different_values(self, mock_preprocess):
        """Test various scope values in prompt building."""
        # Test with a specific scope
        scopes = ["api", "auth", "ui", "backend", "database", "config"]

        for scope_value in scopes:
            prompt = build_prompt("status", "diff", scope=scope_value)
            assert f"The user specified the scope to be '{scope_value}'" in prompt
            assert f"fix({scope_value}):" in prompt


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
            if "The user specified the scope to be 'auth'" in prompt:
                return "feat(auth): add login functionality"
            elif "The user requested to include a scope" in prompt:
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
        with patch('click.prompt', return_value='y'):
            # Test with specific scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope="auth")
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "feat(auth): add login functionality"

            # Reset spy for the next test
            git_spy.commit_message = None

            # Test with AI-determined scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope="")
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "fix(api): handle null response"

            # Reset spy for the next test
            git_spy.commit_message = None

            # Test without scope
            with pytest.raises(SystemExit) as exc_info:
                main(scope=None)
            assert exc_info.value.code == 0
            assert git_spy.commit_message == "feat: add new feature"


def test_scope_flag_help():
    """Test that --scope flag help is displayed correctly."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "--scope" in result.output or "-s" in result.output
    assert "Add a scope to the commit message" in result.output
