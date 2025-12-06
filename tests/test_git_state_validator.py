#!/usr/bin/env python3
"""Tests for GitStateValidator class."""

import subprocess
from unittest.mock import patch

import pytest

from gac.git_state_validator import GitStateValidator


class TestGitStateValidator:
    """Test GitStateValidator class."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return {
            "model": "openai:gpt-4o-mini",
            "temperature": 0.7,
            "max_output_tokens": 2048,
            "max_retries": 3,
        }

    @pytest.fixture
    def validator(self, mock_config):
        """Create a GitStateValidator instance with mock config."""
        return GitStateValidator(mock_config)

    def test_init(self, validator, mock_config):
        """Test GitStateValidator initialization."""
        assert validator.config == mock_config

    @patch("gac.git_state_validator.run_git_command")
    def test_validate_repository_success(self, mock_run_command, validator):
        """Test successful repository validation."""
        mock_run_command.return_value = "/path/to/repo"

        result = validator.validate_repository()

        assert result == "/path/to/repo"
        mock_run_command.assert_called_once_with(["rev-parse", "--show-toplevel"])

    @patch("gac.git_state_validator.run_git_command")
    @patch("gac.git_state_validator.handle_error")
    def test_validate_repository_failure(self, mock_handle_error, mock_run_command, validator):
        """Test repository validation failure."""
        mock_run_command.side_effect = subprocess.SubprocessError("Not a git repository")

        validator.validate_repository()

        mock_handle_error.assert_called_once()

    @patch("gac.git_state_validator.run_git_command")
    def test_stage_all_if_requested(self, mock_run_command, validator):
        """Test staging all files when requested."""
        validator.stage_all_if_requested(True, False)

        mock_run_command.assert_called_once_with(["add", "--all"])

    @patch("gac.git_state_validator.run_git_command")
    def test_stage_all_if_requested_dry_run(self, mock_run_command, validator):
        """Test that staging is skipped in dry run mode."""
        validator.stage_all_if_requested(True, True)

        mock_run_command.assert_not_called()

    @patch("gac.git_state_validator.get_staged_files")
    def test_get_git_state_no_staged_files(self, mock_get_staged, validator):
        """Test get_git_state when no files are staged."""
        mock_get_staged.return_value = []

        with patch("gac.git_state_validator.sys.exit") as mock_exit:
            validator.get_git_state(model="openai:gpt-4o-mini")

            mock_exit.assert_called_once_with(0)

    @patch("gac.git_state_validator.scan_staged_diff")
    def test_get_git_state_with_secrets(self, mock_scan, validator):
        """Test get_git_state when secrets are detected."""
        mock_scan.return_value = ["secret1", "secret2"]

        with (
            patch.object(validator, "validate_repository", return_value="/repo"),
            patch.object(validator, "stage_all_if_requested"),
            patch("gac.git_state_validator.get_staged_files", return_value=["file.py"]),
            patch("gac.git_state_validator.get_staged_status", return_value="M file.py"),
            patch("gac.git_state_validator.run_git_command"),
            patch("gac.git_state_validator.preprocess_diff", return_value="processed"),
        ):
            git_state = validator.get_git_state(model="openai:gpt-4o-mini")

            assert git_state.has_secrets is True
            assert git_state.secrets == ["secret1", "secret2"]

    def test_handle_secret_detection_no_secrets(self, validator):
        """Test handle_secret_detection when no secrets are found."""
        result = validator.handle_secret_detection([])

        assert result is True

    @patch("gac.git_state_validator.console.print")
    @patch("click.prompt")
    def test_handle_secret_detection_abort(self, mock_prompt, mock_print, validator):
        """Test handle_secret_detection when user chooses to abort."""
        from gac.security import DetectedSecret

        mock_secret = DetectedSecret(
            file_path="file.py", line_number=10, secret_type="api_key", matched_text="sk_test_123"
        )
        mock_prompt.return_value = "a"

        with patch("gac.git_state_validator.sys.exit") as mock_exit:
            validator.handle_secret_detection([mock_secret])

            mock_exit.assert_called_once_with(0)

    @patch("gac.git_state_validator.console.print")
    @patch("click.prompt")
    def test_handle_secret_detection_continue(self, mock_prompt, mock_print, validator):
        """Test handle_secret_detection when user chooses to continue."""
        from gac.security import DetectedSecret

        mock_secret = DetectedSecret(
            file_path="file.py", line_number=10, secret_type="api_key", matched_text="sk_test_123"
        )
        mock_prompt.return_value = "c"

        result = validator.handle_secret_detection([mock_secret])

        assert result is True
