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

    @pytest.fixture
    def mock_dependencies(self, monkeypatch):
        """Mock all external dependencies for CLI testing."""
        # Mock config - patch the module-level config object that was already loaded
        test_config = {
            "model": "test:model",
            "backup_model": "test:backup",
            "temperature": 0.1,
            "max_output_tokens": 100,
            "max_retries": 1,
            "format_files": True,
            "log_level": "ERROR",
        }

        # Patch the already-loaded config in main module
        monkeypatch.setattr("gac.main.config", test_config)

        # Also patch load_config in case it's called again
        monkeypatch.setattr("gac.main.load_config", lambda: test_config)
        monkeypatch.setattr("gac.config.load_config", lambda: test_config)

        # Mock git commands
        def mock_git_command(args, **kwargs):
            if "status" in args:
                return "On branch main"
            elif "diff" in args:
                return "diff --git a/file.py b/file.py\n+New line"
            elif "rev-parse" in args:
                return "/repo"
            else:
                return ""

        monkeypatch.setattr("gac.main.run_git_command", mock_git_command)
        monkeypatch.setattr("gac.git.run_git_command", mock_git_command)

        # Mock AI generation
        monkeypatch.setattr("gac.main.generate_with_fallback", lambda **kwargs: "feat: test commit message")
        monkeypatch.setattr("gac.main.clean_commit_message", lambda msg: msg)

        # Mock git commit (using run_git_command)
        def mock_commit(args, **kwargs):
            if args[0] == "commit":
                return None
            return mock_git_command(args)

        monkeypatch.setattr("gac.main.run_git_command", mock_commit)

        # Mock get_staged_files to return some files
        def mock_get_staged_files(**kwargs):
            if kwargs.get("existing_only", False):
                return []  # No files exist on disk
            return ["file.py"]

        monkeypatch.setattr("gac.main.get_staged_files", mock_get_staged_files)
        monkeypatch.setattr("gac.git.get_staged_files", mock_get_staged_files)

        # Mock format_files to avoid file system access
        monkeypatch.setattr("gac.main.format_files", lambda files, dry_run=False: [])
        monkeypatch.setattr("gac.format.format_files", lambda files, dry_run=False: [])

        # Mock Console output
        monkeypatch.setattr("rich.console.Console.print", lambda self, *a, **kw: None)

    def test_scope_flag_with_value(self, runner, mock_dependencies, monkeypatch):
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

    def test_scope_flag_short_with_value(self, runner, mock_dependencies, monkeypatch):
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

    def test_scope_flag_without_value(self, runner, mock_dependencies, monkeypatch):
        """Test --scope flag without a value (AI determines scope)."""
        captured_prompt = None

        def capture_prompt(**kwargs):
            nonlocal captured_prompt
            captured_prompt = kwargs
            return "prompt"

        monkeypatch.setattr("gac.main.build_prompt", capture_prompt)

        result = runner.invoke(cli, ["--scope"])

        assert result.exit_code == 0
        assert captured_prompt is not None
        assert captured_prompt.get("scope") == ""  # Empty string when no value provided

    def test_no_scope_flag(self, runner, mock_dependencies, monkeypatch):
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

    def test_scope_with_other_flags(self, runner, mock_dependencies, monkeypatch):
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

    @patch("gac.prompt.extract_repository_context", return_value="")
    @patch("gac.prompt.preprocess_diff", return_value="processed diff")
    def test_build_prompt_with_specific_scope(self, mock_preprocess, mock_extract):
        """Test prompt building with a specific scope value."""
        status = "On branch main"
        diff = "diff --git a/file.py b/file.py\n+New line"

        prompt = build_prompt(status, diff, scope="auth")

        # Check that the scope instruction is customized
        assert "The user specified the scope to be 'auth'" in prompt
        assert "Please include this exact scope in parentheses after the type" in prompt
        assert "fix(auth):" in prompt  # Example format should be shown

    @patch("gac.prompt.extract_repository_context", return_value="")
    @patch("gac.prompt.preprocess_diff", return_value="processed diff")
    def test_build_prompt_with_empty_scope(self, mock_preprocess, mock_extract):
        """Test prompt building when user wants AI to determine scope."""
        status = "On branch main"
        diff = "diff --git a/file.py b/file.py\n+New line"

        prompt = build_prompt(status, diff, scope="")

        # Check that the scope instruction asks AI to determine scope
        assert "The user requested to include a scope in the commit message" in prompt
        assert "Please determine and include the most appropriate scope" in prompt

    @patch("gac.prompt.extract_repository_context", return_value="")
    @patch("gac.prompt.preprocess_diff", return_value="processed diff")
    def test_build_prompt_without_scope(self, mock_preprocess, mock_extract):
        """Test prompt building when scope is not requested."""
        status = "On branch main"
        diff = "diff --git a/file.py b/file.py\n+New line"

        prompt = build_prompt(status, diff, scope=None)

        # Check that scope instructions are removed
        assert "The user specified the scope to be" not in prompt
        assert "The user requested to include a scope" not in prompt
        # When scope is None, the entire scope_instructions section is removed
        assert "feat(auth): add login functionality" not in prompt
        assert "fix(api): handle null response" not in prompt
        # But the conventions section still mentions scope usage
        assert "If a scope is provided, include it in parentheses" in prompt

    @patch("gac.prompt.extract_repository_context", return_value="")
    @patch("gac.prompt.preprocess_diff", return_value="processed diff")
    def test_scope_with_different_values(self, mock_preprocess, mock_extract):
        """Test various scope values in prompt building."""
        status = "On branch main"
        diff = "diff"

        # Test different scope values
        scopes = ["api", "auth", "ui", "backend", "database", "config"]

        for scope_value in scopes:
            prompt = build_prompt(status, diff, scope=scope_value)
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
            "backup_model": "test:backup",
            "temperature": 0.1,
            "max_output_tokens": 100,
            "max_retries": 1,
            "format_files": True,
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

        monkeypatch.setattr("gac.main.generate_with_fallback", mock_generate)

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

        # Mock format_files to avoid file system access
        monkeypatch.setattr("gac.main.format_files", lambda files, dry_run=False: [])
        monkeypatch.setattr("gac.format.format_files", lambda files, dry_run=False: [])

        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

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
