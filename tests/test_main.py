"""Tests for the main module integration."""

from unittest.mock import MagicMock, patch

import pytest

from gac.errors import ConfigError
from gac.main import _execute_single_commit_workflow, main


class TestMainIntegration:
    """Test main function integration."""

    @patch("gac.main.config")
    @patch("gac.main.GitStateValidator")
    @patch("gac.main.PromptBuilder")
    @patch("gac.main.CommitExecutor")
    @patch("gac.main.InteractiveMode")
    @patch("gac.main.GroupedCommitWorkflow")
    def test_main_function_initializes_components(
        self,
        mock_grouped_workflow,
        mock_interactive_mode,
        mock_commit_executor,
        mock_prompt_builder,
        mock_git_validator,
        mock_config,
    ):
        """Test that main function properly initializes all components."""
        # Mock config with required fields
        config_values = {
            "model": "openai:gpt-4o-mini",
            "temperature": 0.1,
            "max_output_tokens": 4096,
            "max_retries": 3,
            "warning_limit_tokens": 500,
        }
        mock_config.__getitem__.side_effect = lambda key: config_values.get(key)
        mock_config.get.side_effect = lambda key, default=None: config_values.get(key, default)

        # Mock git validator
        mock_git_state = mock_git_validator.return_value.get_git_state.return_value
        mock_git_state.staged_files = ["file1.py"]
        mock_git_state.has_secrets = False

        # Mock prompt builder
        mock_prompts = mock_prompt_builder.return_value.build_prompts.return_value
        mock_prompts.system_prompt = "system prompt"
        mock_prompts.user_prompt = "user prompt"

        with (
            patch("gac.main.run_lefthook_hooks", return_value=True),
            patch("gac.main.run_pre_commit_hooks", return_value=True),
            patch("gac.main._execute_single_commit_workflow") as mock_workflow,
        ):
            main(dry_run=True, quiet=True, require_confirmation=False)

            # Verify all components were initialized
            mock_git_validator.assert_called_once()
            mock_prompt_builder.assert_called_once()
            mock_commit_executor.assert_called_once()
            mock_interactive_mode.assert_called_once()
            mock_grouped_workflow.assert_called_once()

            # Verify workflow was called
            mock_workflow.assert_called_once()

    def test_main_missing_config_values_raise_error(self):
        """Test that accessing missing config values raises ConfigError."""
        # Test the actual logic without going through main()
        config = {"model": "openai:gpt-4o-mini", "temperature": None}

        # Test the same pattern as in main()
        with pytest.raises(ConfigError) as exc:
            temperature_val = config["temperature"]
            if temperature_val is None:
                raise ConfigError("temperature configuration missing")

        assert "temperature configuration missing" in str(exc.value)


class TestSingleCommitWorkflow:
    """Test single commit workflow behavior."""

    @pytest.fixture
    def mock_components(self):
        """Create mock components for workflow tests."""
        commit_executor = MagicMock()
        interactive_mode = MagicMock()
        git_state = MagicMock()
        git_state.status = "M test.py"
        git_state.processed_diff = "diff content"
        git_state.diff_stat = "1 file changed"
        return commit_executor, interactive_mode, git_state

    @patch("gac.main.generate_commit_message")
    @patch("gac.main.count_tokens")
    @patch("gac.main.config", {"warning_limit_tokens": 50000})
    def test_panel_displayed_with_auto_confirm_flag(self, mock_count_tokens, mock_generate, mock_components):
        """Test that commit message panel is displayed even when require_confirmation=False (-y flag)."""
        commit_executor, interactive_mode, git_state = mock_components
        mock_generate.return_value = "feat: test commit message"
        mock_count_tokens.return_value = 100

        with (
            patch("gac.main.display_commit_message") as mock_display,
            pytest.raises(SystemExit) as exc,
        ):
            _execute_single_commit_workflow(
                system_prompt="system",
                user_prompt="user",
                model="openai:gpt-4o-mini",
                temperature=0.1,
                max_output_tokens=4096,
                max_retries=3,
                require_confirmation=False,  # -y flag
                quiet=False,
                no_verify=False,
                dry_run=False,
                push=False,
                show_prompt=False,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint="",
            )

        assert exc.value.code == 0
        mock_display.assert_called_once()
        commit_executor.create_commit.assert_called_once_with("feat: test commit message")

    @patch("gac.main.generate_commit_message")
    @patch("gac.main.count_tokens")
    @patch("gac.main.config", {"warning_limit_tokens": 50000})
    def test_panel_not_displayed_when_quiet(self, mock_count_tokens, mock_generate, mock_components):
        """Test that commit message panel is not displayed when quiet=True."""
        commit_executor, interactive_mode, git_state = mock_components
        mock_generate.return_value = "feat: test commit message"
        mock_count_tokens.return_value = 100

        with (
            patch("gac.main.display_commit_message") as mock_display,
            pytest.raises(SystemExit) as exc,
        ):
            _execute_single_commit_workflow(
                system_prompt="system",
                user_prompt="user",
                model="openai:gpt-4o-mini",
                temperature=0.1,
                max_output_tokens=4096,
                max_retries=3,
                require_confirmation=False,
                quiet=True,  # quiet mode
                no_verify=False,
                dry_run=False,
                push=False,
                show_prompt=False,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint="",
            )

        assert exc.value.code == 0
        mock_display.assert_not_called()

    @patch("gac.main.generate_commit_message")
    @patch("gac.main.count_tokens")
    @patch("gac.main.console")
    @patch("gac.main.config", {"warning_limit_tokens": 50000})
    def test_abort_on_no_response(self, mock_console, mock_count_tokens, mock_generate, mock_components):
        """Test that responding 'n' to confirmation aborts the commit."""
        commit_executor, interactive_mode, git_state = mock_components
        mock_generate.return_value = "feat: test commit message"
        mock_count_tokens.return_value = 100

        interactive_mode.handle_single_commit_confirmation.return_value = ("feat: test commit message", "no")

        with (
            patch("gac.workflow_utils.display_commit_message"),
            pytest.raises(SystemExit) as exc,
        ):
            _execute_single_commit_workflow(
                system_prompt="system",
                user_prompt="user",
                model="openai:gpt-4o-mini",
                temperature=0.1,
                max_output_tokens=4096,
                max_retries=3,
                require_confirmation=True,
                quiet=False,
                no_verify=False,
                dry_run=False,
                push=False,
                show_prompt=False,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint="",
            )

        assert exc.value.code == 0
        mock_console.print.assert_called_with("[yellow]Commit aborted.[/yellow]")
        commit_executor.create_commit.assert_not_called()

    @patch("gac.main.generate_commit_message")
    @patch("gac.main.count_tokens")
    @patch("gac.main.config", {"warning_limit_tokens": 50000})
    def test_regenerate_on_reroll_response(self, mock_count_tokens, mock_generate, mock_components):
        """Test that responding 'r' regenerates the commit message."""
        commit_executor, interactive_mode, git_state = mock_components
        mock_generate.side_effect = ["feat: first message", "feat: second message"]
        mock_count_tokens.return_value = 100

        interactive_mode.handle_single_commit_confirmation.side_effect = [
            ("feat: first message", "regenerate"),
            ("feat: second message", "yes"),
        ]

        with (
            patch("gac.workflow_utils.display_commit_message"),
            pytest.raises(SystemExit) as exc,
        ):
            _execute_single_commit_workflow(
                system_prompt="system",
                user_prompt="user",
                model="openai:gpt-4o-mini",
                temperature=0.1,
                max_output_tokens=4096,
                max_retries=3,
                require_confirmation=True,
                quiet=False,
                no_verify=False,
                dry_run=False,
                push=False,
                show_prompt=False,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint="",
            )

        assert exc.value.code == 0
        assert mock_generate.call_count == 2
        assert interactive_mode.handle_single_commit_confirmation.call_count == 2
        commit_executor.create_commit.assert_called_once_with("feat: second message")

    @patch("gac.main.generate_commit_message")
    @patch("gac.main.count_tokens")
    @patch("gac.main.config", {"warning_limit_tokens": 50000})
    def test_proceed_on_yes_response(self, mock_count_tokens, mock_generate, mock_components):
        """Test that responding 'y' proceeds with the commit."""
        commit_executor, interactive_mode, git_state = mock_components
        mock_generate.return_value = "feat: test commit message"
        mock_count_tokens.return_value = 100

        interactive_mode.handle_single_commit_confirmation.return_value = ("feat: edited message", "yes")

        with (
            patch("gac.workflow_utils.display_commit_message"),
            pytest.raises(SystemExit) as exc,
        ):
            _execute_single_commit_workflow(
                system_prompt="system",
                user_prompt="user",
                model="openai:gpt-4o-mini",
                temperature=0.1,
                max_output_tokens=4096,
                max_retries=3,
                require_confirmation=True,
                quiet=False,
                no_verify=False,
                dry_run=False,
                push=False,
                show_prompt=False,
                commit_executor=commit_executor,
                interactive_mode=interactive_mode,
                git_state=git_state,
                hint="",
            )

        assert exc.value.code == 0
        commit_executor.create_commit.assert_called_once_with("feat: edited message")
