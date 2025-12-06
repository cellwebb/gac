#!/usr/bin/env python3
"""Tests for PromptBuilder class."""

from unittest.mock import Mock, patch

import pytest

from gac.prompt_builder import PromptBuilder, PromptBundle


class TestPromptBuilder:
    """Test PromptBuilder class."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "language": "en",
            "translate_prefixes": True,
            "system_prompt_path": None,
        }

    @pytest.fixture
    def builder(self, mock_config):
        """Create a PromptBuilder instance with mock config."""
        return PromptBuilder(mock_config)

    @pytest.fixture
    def mock_git_state(self):
        """Mock git state."""
        from gac.git_state_validator import GitState

        return GitState(
            repo_root="/repo",
            staged_files=["file.py"],
            status="M file.py",
            diff="diff content",
            diff_stat=" file.py | 1 +",
            processed_diff="processed diff",
            has_secrets=False,
            secrets=[],
        )

    def test_init(self, builder, mock_config):
        """Test PromptBuilder initialization."""
        assert builder.config == mock_config

    @patch("gac.prompt.build_prompt")
    def test_build_prompts_single_commit(self, mock_build_prompt, builder, mock_git_state):
        """Test building prompts for single commit."""
        mock_build_prompt.return_value = ("system", "user")

        result = builder.build_prompts(mock_git_state, group=False)

        assert isinstance(result, PromptBundle)
        assert result.system_prompt == "system"
        assert result.user_prompt == "user"
        mock_build_prompt.assert_called_once()

    @patch("gac.prompt.build_group_prompt")
    def test_build_prompts_grouped_commit(self, mock_build_group_prompt, builder, mock_git_state):
        """Test building prompts for grouped commit."""
        mock_build_group_prompt.return_value = ("system", "user")

        result = builder.build_prompts(mock_git_state, group=True)

        assert isinstance(result, PromptBundle)
        assert result.system_prompt == "system"
        assert result.user_prompt == "user"
        mock_build_group_prompt.assert_called_once()

    @patch("gac.prompt_builder.Panel")
    @patch("rich.console.Console")
    def test_display_prompts(self, mock_console, mock_panel, builder):
        """Test displaying prompts."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        builder.display_prompts("system", "user")

        mock_console.assert_called_once()
        mock_panel.assert_called_once()

    def test_build_prompts_with_language_override(self, builder, mock_git_state):
        """Test building prompts with language override."""
        with patch("gac.prompt.build_prompt") as mock_build_prompt:
            mock_build_prompt.return_value = ("system", "user")

            builder.build_prompts(mock_git_state, language="es")

            # Should not affect config.get() calls, just pass through
            mock_build_prompt.assert_called_once()

    def test_build_prompts_with_config_options(self, builder, mock_git_state):
        """Test building prompts respects config options."""
        with patch("gac.prompt.build_prompt") as mock_build_prompt:
            mock_build_prompt.return_value = ("system", "user")

            builder.build_prompts(
                mock_git_state,
                one_liner=True,
                hint="test hint",
                infer_scope=True,
                verbose=True,
            )

            call_args = mock_build_prompt.call_args[1]
            assert call_args["one_liner"] is True
            assert call_args["hint"] == "test hint"
            assert call_args["infer_scope"] is True
            assert call_args["verbose"] is True
