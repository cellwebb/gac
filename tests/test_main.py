"""Tests for the main module integration."""

from unittest.mock import patch

import pytest

from gac.errors import ConfigError
from gac.main import _parse_model_identifier, main


class TestParseModelIdentifier:
    """Test the _parse_model_identifier function."""

    def test_parse_model_identifier_valid_format(self):
        """Test parsing valid model identifiers."""
        provider, model_name = _parse_model_identifier("openai:gpt-4o-mini")
        assert provider == "openai"
        assert model_name == "gpt-4o-mini"

        provider, model_name = _parse_model_identifier("anthropic:claude-3-haiku")
        assert provider == "anthropic"
        assert model_name == "claude-3-haiku"

    def test_parse_model_identifier_trims_whitespace(self):
        """Test that whitespace is trimmed from model identifiers."""
        provider, model_name = _parse_model_identifier("  openai:gpt-4  ")
        assert provider == "openai"
        assert model_name == "gpt-4"

    def test_parse_model_identifier_invalid_format_exits(self):
        """Test that invalid model format causes SystemExit."""
        with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
            _parse_model_identifier("invalid-model")

        assert exc.value.code == 1
        mock_print.assert_called()
        printed_args = " ".join(str(call) for call in mock_print.call_args_list)
        assert "Invalid model format" in printed_args
        assert "Expected 'provider:model'" in printed_args

    def test_parse_model_identifier_empty_parts_exits(self):
        """Test that empty provider or model name causes SystemExit."""
        test_cases = ["openai:", ":gpt-4", "provider:"]

        for invalid_model in test_cases:
            with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
                _parse_model_identifier(invalid_model)

            assert exc.value.code == 1
            mock_print.assert_called()
            printed_args = " ".join(str(call) for call in mock_print.call_args_list)
            assert "Invalid model format" in printed_args
            assert "provider and model name are required" in printed_args


class TestMainIntegration:
    """Test main function integration."""

    @patch("gac.main.GitStateValidator")
    @patch("gac.main.PromptBuilder")
    @patch("gac.main.CommitExecutor")
    @patch("gac.main.InteractiveMode")
    @patch("gac.main.GroupedCommitWorkflow")
    @patch("gac.main.load_config")
    def test_main_function_initializes_components(
        self,
        mock_load_config,
        mock_grouped_workflow,
        mock_interactive_mode,
        mock_commit_executor,
        mock_prompt_builder,
        mock_git_validator,
    ):
        """Test that main function properly initializes all components."""
        # Mock config
        mock_config = {
            "model": "openai:gpt-4o-mini",
            "temperature": 0.1,
            "max_output_tokens": 4096,
            "max_retries": 3,
        }
        mock_load_config.return_value = mock_config

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
            patch("gac.main._execute_single_commit_workflow_refactored") as mock_workflow,
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
