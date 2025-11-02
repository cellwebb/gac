"""Test module for token usage display functionality."""

import copy

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
            if isinstance(content, list):  # Conversation prompt
                return 300
            # Commit message
            return 10

        monkeypatch.setattr("gac.main.count_tokens", mock_count_tokens)
        monkeypatch.setattr("gac.ai_utils.count_tokens", mock_count_tokens)

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

    def test_prompt_tokens_recalculated_after_reroll(self, runner, mock_dependencies, monkeypatch):
        """Ensure prompt token counts are recomputed when rerolling with feedback."""
        # Track build_prompt calls and return distinct prompts per generation
        prompt_history: list[tuple[str, str]] = []

        def fake_build_prompt(**kwargs):
            system_prompt = f"system-prompt-{len(prompt_history)}"
            user_prompt = f"user-prompt-{len(prompt_history)}"
            prompt_history.append((system_prompt, user_prompt))
            return system_prompt, user_prompt

        monkeypatch.setattr("gac.main.build_prompt", fake_build_prompt)

        # Capture count_tokens inputs to verify recomputation happens for reroll prompts
        counted_inputs: list[object] = []

        def fake_count_tokens(content, model):
            if isinstance(content, list):
                counted_inputs.append(copy.deepcopy(content))
                return 200
            counted_inputs.append(content)
            return 10

        monkeypatch.setattr("gac.main.count_tokens", fake_count_tokens)
        monkeypatch.setattr("gac.ai_utils.count_tokens", fake_count_tokens)

        # Provide two commit messages, one for the initial generation and one for the reroll
        commit_messages = iter(["feat: initial", "feat: rerolled"])

        conversation_history: list[list[dict[str, str]]] = []

        def fake_generate_commit_message(**kwargs):
            prompt_messages = kwargs["prompt"]
            conversation_history.append(copy.deepcopy(prompt_messages))
            return next(commit_messages)

        monkeypatch.setattr("gac.main.generate_commit_message", fake_generate_commit_message)

        # Simulate user providing feedback followed by acceptance
        responses = iter(["needs more detail", "y"])
        monkeypatch.setattr("click.prompt", lambda *args, **kwargs: next(responses))

        result = runner.invoke(cli, ["--no-verify"])

        assert result.exit_code == 0

        # Prompt should only be built once; rerolls reuse the conversation
        assert prompt_history == [("system-prompt-0", "user-prompt-0")]

        # count_tokens should have been called with the conversation before each generation
        assert len(counted_inputs) == 4
        assert isinstance(counted_inputs[0], list)
        assert len(counted_inputs[0]) == 2  # system + user
        assert counted_inputs[1] == "feat: initial"
        assert isinstance(counted_inputs[2], list)
        assert len(counted_inputs[2]) == 4  # includes assistant reply + feedback message
        assert counted_inputs[3] == "feat: rerolled"

        # Verify conversation history sent to generate_commit_message follows message chain pattern
        assert len(conversation_history) == 2
        assert conversation_history[0] == [
            {"role": "system", "content": "system-prompt-0"},
            {"role": "user", "content": "user-prompt-0"},
        ]
        assert conversation_history[1] == [
            {"role": "system", "content": "system-prompt-0"},
            {"role": "user", "content": "user-prompt-0"},
            {"role": "assistant", "content": "feat: initial"},
            {
                "role": "user",
                "content": "Please revise the commit message based on this feedback: needs more detail",
            },
        ]
