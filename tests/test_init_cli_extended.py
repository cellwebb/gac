"""Extended tests for init_cli module focused on init workflow integration."""

import tempfile
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.init_cli import init


def test_init_cli_creates_new_gac_env_file(clean_env_state):
    """Test that init creates .gac.env if it doesn't exist (init workflow)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        # Don't create the file beforehand
        assert not env_path.exists()

        with (
            mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
            mock.patch("gac.model_cli.GAC_ENV_PATH", env_path),
        ):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Anthropic", "English"]
                mtext.return_value.ask.side_effect = ["claude-sonnet-4-5"]
                mpass.return_value.ask.side_effect = ["test-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert env_path.exists()
                env_text = env_path.read_text()
                assert "ANTHROPIC_API_KEY='test-key'" in env_text
                assert "GAC_MODEL='anthropic:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text


def test_init_cli_complete_workflow_with_model_and_language(clean_env_state):
    """Test complete init workflow with model and language configuration."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()

        with (
            mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
            mock.patch("gac.model_cli.GAC_ENV_PATH", env_path),
        ):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Anthropic", "English"]
                mtext.return_value.ask.side_effect = ["claude-sonnet-4-5"]
                mpass.return_value.ask.side_effect = ["test-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='anthropic:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text


def test_init_cli_init_workflow_failure_cleanup(clean_env_state):
    """Test that init workflow can handle failures gracefully."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()

        with (
            mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
            mock.patch("gac.model_cli.GAC_ENV_PATH", env_path),
        ):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as _mtext,
                mock.patch("questionary.password") as _mpass,
            ):
                # User cancels provider selection
                mselect.return_value.ask.side_effect = [None]

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Provider selection cancelled" in result.output


# Note: Model-specific tests (Custom Anthropic, Custom OpenAI, Azure OpenAI, etc.)
# have been moved to test_model_cli.py to maintain better separation of concerns.
# This file now focuses on the complete init workflow integration.
