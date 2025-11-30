"""Tests for model_cli module."""

from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.model_cli import model


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


def test_model_cli_basic(tmp_path):
    """Test basic model CLI functionality."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    # Mock both GAC_ENV_PATH locations since init_cli imports from model_cli
    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):  # For init_cli's _load_existing_env
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection
                mselect.return_value.ask.side_effect = ["OpenAI"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["sk-test-key"]

                runner = CliRunner()
                result = runner.invoke(model)

                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='openai:gpt-4'" in env_text
                assert "OPENAI_API_KEY='sk-test-key'" in env_text
                assert "Model configuration complete" in result.output


def test_model_cli_cancelled(tmp_path):
    """Test model CLI when user cancels provider selection."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with mock.patch("questionary.select") as mselect:
                mselect.return_value.ask.side_effect = [None]  # User cancels

                runner = CliRunner()
                result = runner.invoke(model)

                assert result.exit_code == 0
                assert "Provider selection cancelled" in result.output


def test_model_cli_custom_openai(tmp_path):
    """Test custom OpenAI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Custom (OpenAI)"]
                mtext.return_value.ask.side_effect = ["my-custom-model", "https://custom.example.com/v1"]
                mpass.return_value.ask.side_effect = ["custom-key"]

                runner = CliRunner()
                result = runner.invoke(model)

                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='custom-openai:my-custom-model'" in env_text
                assert "CUSTOM_OPENAI_BASE_URL='https://custom.example.com/v1'" in env_text
                assert "CUSTOM_OPENAI_API_KEY='custom-key'" in env_text


def test_model_cli_groq_provider(tmp_path):
    """Test Groq provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Groq"]
            mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]
            mpass.return_value.ask.side_effect = ["main-api-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='groq:meta-llama/llama-4-scout-17b-16e-instruct'" in env_text
            assert "GROQ_API_KEY='main-api-key'" in env_text


def test_model_cli_zai_regular_provider(tmp_path):
    """Test Z.AI regular provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Z.AI"]
            mtext.return_value.ask.side_effect = ["glm-4.6"]
            mpass.return_value.ask.side_effect = ["zai-api-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='zai:glm-4.6'" in env_text
            assert "ZAI_API_KEY='zai-api-key'" in env_text


def test_model_cli_zai_coding_provider(tmp_path):
    """Test Z.AI Coding provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Z.AI Coding"]
            mtext.return_value.ask.side_effect = ["glm-4.6"]
            mpass.return_value.ask.side_effect = ["zai-api-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='zai-coding:glm-4.6'" in env_text
            assert "ZAI_API_KEY='zai-api-key'" in env_text


def test_model_cli_streamlake_requires_endpoint(tmp_path):
    """Test Streamlake requires endpoint ID configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Streamlake"]
            # First text prompt is for the endpoint ID (required)
            mtext.return_value.ask.side_effect = ["ep-custom-12345"]
            mpass.return_value.ask.side_effect = ["streamlake-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='streamlake:ep-custom-12345'" in env_text
            assert "STREAMLAKE_API_KEY='streamlake-key'" in env_text


def test_model_cli_ollama_optional_api_key_and_url(tmp_path):
    """Test Ollama provider with optional API key and custom URL."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Ollama"]
            mtext.return_value.ask.side_effect = ["gemma3", "http://localhost:11434"]
            mpass.return_value.ask.side_effect = [None]  # Skip API key

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='ollama:gemma3'" in env_text
            assert "OLLAMA_API_URL='http://localhost:11434'" in env_text
            # No API key should be set
            assert "OLLAMA_API_KEY" not in env_text


def test_model_cli_lmstudio_optional_api_key_and_url(tmp_path):
    """Test LM Studio provider with optional API key and custom URL."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["LM Studio"]
            mtext.return_value.ask.side_effect = ["gemma3", "http://localhost:1234"]
            mpass.return_value.ask.side_effect = [None]  # Skip API key

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='lm-studio:gemma3'" in env_text
            assert "LMSTUDIO_API_URL='http://localhost:1234'" in env_text
            # No API key should be set
            assert "LMSTUDIO_API_KEY" not in env_text


def test_model_cli_provider_selection_cancelled(tmp_path):
    """Test model CLI when user cancels provider selection."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with mock.patch("questionary.select") as mselect:
            mselect.return_value.ask.side_effect = [None]  # User cancels

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            assert "Provider selection cancelled" in result.output


def test_model_cli_streamlake_endpoint_cancelled(tmp_path):
    """Test Streamlake endpoint cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
        ):
            mselect.return_value.ask.side_effect = ["Streamlake"]
            mtext.return_value.ask.side_effect = [None]  # User cancels endpoint entry

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            assert "Streamlake configuration cancelled" in result.output


def test_model_cli_model_entry_cancelled(tmp_path):
    """Test model entry cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
        ):
            mselect.return_value.ask.side_effect = ["OpenAI"]
            mtext.return_value.ask.side_effect = [None]  # User cancels model entry

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            assert "Model entry cancelled" in result.output


def test_model_cli_existing_api_key_leave_as_is(tmp_path):
    """Test leaving existing API key unchanged."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()
    # Pre-populate with existing API key
    env_path.write_text("OPENAI_API_KEY='existing-key'\nGAC_MODEL='openai:gpt-4'\n")

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as _mpass,
        ):
            mselect.return_value.ask.side_effect = ["OpenAI", "Keep existing key"]
            mtext.return_value.ask.side_effect = ["gpt-5"]
            # mpass.return_value.ask.side_effect = None  # Not used when keeping existing key

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='openai:gpt-5'" in env_text
            assert "OPENAI_API_KEY='existing-key'" in env_text
            assert "Keeping existing OPENAI_API_KEY" in result.output


def test_model_cli_existing_api_key_edit_replace(tmp_path):
    """Test replacing existing API key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()
    # Pre-populate with existing API key
    env_path.write_text("OPENAI_API_KEY='existing-key'\nGAC_MODEL='openai:gpt-4'\n")

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = [
                "OpenAI",  # Provider
                "Enter new key",  # Action
            ]
            mtext.return_value.ask.side_effect = ["gpt-5"]
            mpass.return_value.ask.side_effect = ["new-api-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='openai:gpt-5'" in env_text
            assert "OPENAI_API_KEY='new-api-key'" in env_text
            assert "Updated OPENAI_API_KEY" in result.output


# Note: Claude Code OAuth tests are complex and require special mocking
# They can be added later if needed. The core provider functionality is tested above.


# Custom provider tests
def test_model_cli_custom_anthropic_with_default_version(tmp_path):
    """Test Custom Anthropic provider with default API version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Custom (Anthropic)"]
            mtext.return_value.ask.side_effect = [
                "claude-3-5-sonnet",
                "https://custom-anthropic.example.com",
                "2023-06-01",
            ]
            mpass.return_value.ask.side_effect = ["custom-anthropic-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='custom-anthropic:claude-3-5-sonnet'" in env_text
            assert "CUSTOM_ANTHROPIC_BASE_URL='https://custom-anthropic.example.com'" in env_text
            assert "CUSTOM_ANTHROPIC_API_KEY='custom-anthropic-key'" in env_text
            # No custom version should be set when using default
            assert "CUSTOM_ANTHROPIC_VERSION" not in env_text


def test_model_cli_custom_anthropic_with_custom_version(tmp_path):
    """Test Custom Anthropic provider with custom API version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Custom (Anthropic)"]
            mtext.return_value.ask.side_effect = [
                "claude-3-5-sonnet",
                "https://custom-anthropic.example.com",
                "2023-01-01",
            ]
            mpass.return_value.ask.side_effect = ["custom-anthropic-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='custom-anthropic:claude-3-5-sonnet'" in env_text
            assert "CUSTOM_ANTHROPIC_BASE_URL='https://custom-anthropic.example.com'" in env_text
            assert "CUSTOM_ANTHROPIC_API_KEY='custom-anthropic-key'" in env_text
            assert "CUSTOM_ANTHROPIC_VERSION='2023-01-01'" in env_text


# Azure OpenAI tests
def test_model_cli_azure_openai_configuration(tmp_path):
    """Test Azure OpenAI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            mselect.return_value.ask.side_effect = ["Azure OpenAI"]
            mtext.return_value.ask.side_effect = [
                "gpt-4o",
                "https://test-resource.openai.azure.com",
                "2025-01-01-preview",
            ]
            mpass.return_value.ask.side_effect = ["azure-openai-key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='azure-openai:gpt-4o'" in env_text
            assert "AZURE_OPENAI_ENDPOINT='https://test-resource.openai.azure.com'" in env_text
            assert "AZURE_OPENAI_API_VERSION='2025-01-01-preview'" in env_text
            assert "AZURE_OPENAI_API_KEY='azure-openai-key'" in env_text


def test_model_cli_empty_model_suggestion(tmp_path):
    """Test providers with empty model suggestions (require explicit model entry)."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with _patch_env_paths(env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
        ):
            # Custom providers have empty model suggestions
            mselect.return_value.ask.side_effect = ["Custom (OpenAI)"]
            mtext.return_value.ask.side_effect = ["my-custom-model", "https://example.com/v1"]
            mpass.return_value.ask.side_effect = ["key"]

            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            env_text = env_path.read_text()
            assert "GAC_MODEL='custom-openai:my-custom-model'" in env_text
            assert "CUSTOM_OPENAI_BASE_URL='https://example.com/v1'" in env_text
            assert "CUSTOM_OPENAI_API_KEY='key'" in env_text
