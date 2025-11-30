"""Tests for init_cli module focused on init workflow integration."""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.init_cli import init


def _setup_env_file(tmpdir: str) -> Path:
    env_path = Path(tmpdir) / ".gac.env"
    env_path.touch()
    return env_path


@contextmanager
def _patch_env_paths(env_path: Path):
    """Patch all GAC_ENV_PATH locations since init_cli imports from model_cli and language_cli."""
    with (
        mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
        mock.patch("gac.model_cli.GAC_ENV_PATH", env_path),
        mock.patch("gac.language_cli.GAC_ENV_PATH", env_path),
    ):
        yield


def test_init_cli_complete_workflow_with_english_language(monkeypatch):
    """Test complete init workflow with model + language configuration."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with _patch_env_paths(env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Complete workflow: provider selection + language selection (no existing config)
                mselect.return_value.ask.side_effect = ["OpenAI", "English"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='openai:gpt-4'" in env_text
                assert "OPENAI_API_KEY='openai-key'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text
                assert "gac environment setup complete" in result.output


def test_init_cli_complete_workflow_simple(monkeypatch):
    """Test complete init workflow (simple version)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with _patch_env_paths(env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Simple workflow: provider selection + English language
                mselect.return_value.ask.side_effect = ["OpenAI", "English"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='openai:gpt-4'" in env_text
                assert "OPENAI_API_KEY='openai-key'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text


# Language configuration tests (these test the init workflow language part)
def test_init_cli_existing_language_keep(monkeypatch):
    """Test keeping existing language during init workflow."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("OPENAI_API_KEY='existing-key'\nGAC_LANGUAGE='Spanish'\nGAC_TRANSLATE_PREFIXES='true'\n")
        with _patch_env_paths(env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider, API key action, language action (Keep existing)
                mselect.return_value.ask.side_effect = ["OpenAI", "Keep existing key", "Keep existing language"]
                mtext.return_value.ask.side_effect = ["gpt-4"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='Spanish'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='true'" in env_text


def test_init_cli_existing_configuration_workflow(monkeypatch):
    """Test init workflow with existing model configuration."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        # Pre-populate with existing model config
        env_path.write_text("OPENAI_API_KEY=existing-key\nGAC_MODEL=openai:gpt-4\n")
        with _patch_env_paths(env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as _mpass,
            ):
                mselect.return_value.ask.side_effect = ["OpenAI", "Keep existing key", "English"]
                mtext.return_value.ask.side_effect = ["gpt-5"]
                # mpass not used when keeping existing key

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                # Should update model but keep existing API key
                assert "GAC_MODEL='openai:gpt-5'" in env_text
                assert "OPENAI_API_KEY=existing-key" in env_text
                assert "GAC_LANGUAGE='English'" in env_text


# Cancellation tests for init workflow
def test_init_cli_provider_selection_cancelled():
    """Test init workflow when user cancels provider selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with _patch_env_paths(env_path):
            with mock.patch("questionary.select") as mselect:
                mselect.return_value.ask.side_effect = [None]  # User cancels

                runner = CliRunner()
                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Provider selection cancelled" in result.output


def test_init_cli_language_action_cancelled(monkeypatch):
    """Test init workflow when user cancels language selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with _patch_env_paths(env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["OpenAI", None]  # Cancels at language step
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]

                result = runner.invoke(init)
                # Should complete model config but cancel language part
                assert result.exit_code == 0
