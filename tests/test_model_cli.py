"""Tests for model_cli module."""

from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.model_cli import (
    _configure_model,
    _load_existing_env,
    _prompt_required_text,
    _should_show_rtl_warning_for_init,
    _show_rtl_warning_for_init,
    model,
)


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


def test_should_show_rtl_warning_for_init_no_config() -> None:
    """Test RTL warning check when no config exists (lines 20-24)."""
    with mock.patch("gac.model_cli.GAC_ENV_PATH") as mock_path:
        mock_path.exists.return_value = False

        result = _should_show_rtl_warning_for_init()
        assert result is True  # Should show warning when no config exists


def test_should_show_rtl_warning_for_init_not_confirmed() -> None:
    """Test RTL warning check when config exists but RTL not confirmed."""
    with (
        mock.patch("gac.model_cli.GAC_ENV_PATH") as mock_path,
        mock.patch("gac.model_cli.load_dotenv"),
        mock.patch("gac.model_cli.os.getenv", return_value="false"),
    ):
        mock_path.exists.return_value = True

        result = _should_show_rtl_warning_for_init()
        assert result is True  # Should show warning when RTL not confirmed


def test_should_show_rtl_warning_for_init_already_confirmed() -> None:
    """Test RTL warning check when user already confirmed RTL."""
    with (
        mock.patch("gac.model_cli.GAC_ENV_PATH") as mock_path,
        mock.patch("gac.model_cli.load_dotenv"),
        mock.patch("gac.model_cli.os.getenv", return_value="true"),
    ):
        mock_path.exists.return_value = True

        result = _should_show_rtl_warning_for_init()
        assert result is False  # Should not show warning when already confirmed


def test_show_rtl_warning_for_init_proceeds() -> None:
    """Test RTL warning flow when user proceeds (lines 37-54)."""
    with (
        mock.patch("gac.model_cli.click.echo") as mock_echo,
        mock.patch("gac.model_cli.click.style") as mock_style,
        mock.patch("gac.model_cli.questionary.confirm") as mock_confirm,
        mock.patch("gac.model_cli.set_key") as mock_set_key,
    ):
        mock_confirm.return_value.ask.return_value = True
        mock_style.return_value = "Styled title"

        result = _show_rtl_warning_for_init("Hebrew")

        assert result is True
        mock_set_key.assert_called_once()
        mock_echo.assert_called()


def test_show_rtl_warning_for_init_cancels() -> None:
    """Test RTL warning flow when user cancels."""
    with (
        mock.patch("gac.model_cli.click.echo") as mock_echo,
        mock.patch("gac.model_cli.click.style") as mock_style,
        mock.patch("gac.model_cli.questionary.confirm") as mock_confirm,
        mock.patch("gac.model_cli.set_key") as mock_set_key,
    ):
        mock_confirm.return_value.ask.return_value = False
        mock_style.return_value = "Styled title"

        result = _show_rtl_warning_for_init("Hebrew")

        assert result is False
        mock_set_key.assert_not_called()
        mock_echo.assert_called()


def test_prompt_required_text_success() -> None:
    """Test _prompt_required_text when user provides valid input (line 66)."""
    with mock.patch("gac.model_cli.questionary.text") as mock_text:
        mock_text.return_value.ask.return_value = "valid input"

        result = _prompt_required_text("Enter value:")

        assert result == "valid input"


def test_prompt_required_text_cancels() -> None:
    """Test _prompt_required_text when user cancels."""
    with mock.patch("gac.model_cli.questionary.text") as mock_text:
        mock_text.return_value.ask.return_value = None

        result = _prompt_required_text("Enter value:")

        assert result is None


def test_prompt_required_text_empty_then_valid() -> None:
    """Test _prompt_required_text when user enters empty then valid input."""
    with mock.patch("gac.model_cli.questionary.text") as mock_text, mock.patch("gac.model_cli.click.echo") as mock_echo:
        # First call returns empty, second returns valid
        mock_text.return_value.ask.side_effect = ["   ", "valid input"]

        result = _prompt_required_text("Enter value:")

        assert result == "valid input"
        mock_echo.assert_called_with("A value is required. Please try again.")


def test_load_existing_env_file_exists() -> None:
    """Test _load_existing_env when env file already exists (lines 76-77)."""
    mock_path = mock.Mock()
    mock_path.exists.return_value = True

    with (
        mock.patch("gac.model_cli.GAC_ENV_PATH", mock_path),
        mock.patch("gac.model_cli.click.echo") as mock_echo,
        mock.patch("gac.model_cli.dotenv_values", return_value={"EXISTING": "value", "EMPTY": None}),
    ):
        result = _load_existing_env()

        assert result == {"EXISTING": "value"}
        mock_echo.assert_called()


def test_load_existing_env_file_new() -> None:
    """Test _load_existing_env when creating new env file."""
    mock_path = mock.Mock()
    mock_path.exists.return_value = False

    with (
        mock.patch("gac.model_cli.GAC_ENV_PATH", mock_path),
        mock.patch("gac.model_cli.click.echo") as mock_echo,
        mock.patch("gac.model_cli.dotenv_values", return_value={}),
    ):
        result = _load_existing_env()

        assert result == {}
        mock_path.touch.assert_called_once()
        mock_echo.assert_called()


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


def test_configure_model_azure_new_endpoint_cancelled(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli._prompt_required_text") as mprompt,
        ):
            mselect.return_value.ask.side_effect = ["Azure OpenAI"]
            mtext.return_value.ask.side_effect = ["gpt-5-mini"]
            mprompt.return_value = None

            result = _configure_model({})
            assert result is False


def test_configure_model_azure_api_version_enter_new(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("questionary.password") as mpass,
            mock.patch("gac.model_cli.set_key"),
        ):
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",
                "Keep existing endpoint",
                "Enter new version",
                "Keep existing key",
            ]
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",
                "2025-03-01-preview",
            ]
            mpass.return_value.ask.return_value = None

            result = _configure_model(
                {
                    "AZURE_OPENAI_ENDPOINT": "https://myendpoint.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                    "AZURE_OPENAI_API_KEY": "existing-key",
                }
            )
            assert result is True


def test_configure_model_azure_api_version_enter_new_cancelled(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
        ):
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",
                "Keep existing endpoint",
                "Enter new version",
            ]
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",
                None,
            ]

            result = _configure_model(
                {
                    "AZURE_OPENAI_ENDPOINT": "https://myendpoint.openai.azure.com",
                    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
                }
            )
            assert result is False


def test_configure_model_ollama_url_cancelled(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
        ):
            mselect.return_value.ask.side_effect = ["Ollama"]
            mtext.return_value.ask.side_effect = ["gemma3", None]

            result = _configure_model({})
            assert result is False


def test_configure_model_lmstudio_url_cancelled(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
        ):
            mselect.return_value.ask.side_effect = ["LM Studio"]
            mtext.return_value.ask.side_effect = ["gemma3", None]

            result = _configure_model({})
            assert result is False


def test_configure_model_claude_code_oauth_keep_existing(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value={"access_token": "existing"}),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)", "Keep existing token"]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is True


def test_configure_model_claude_code_oauth_reauth_success(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value={"access_token": "existing"}),
            mock.patch("gac.oauth.claude_code.authenticate_and_save", return_value=True),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)", "Re-authenticate (get new token)"]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is True


def test_configure_model_claude_code_oauth_reauth_fail(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value={"access_token": "existing"}),
            mock.patch("gac.oauth.claude_code.authenticate_and_save", return_value=False),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)", "Re-authenticate (get new token)"]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is False


def test_configure_model_claude_code_oauth_no_existing_success(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value=None),
            mock.patch("gac.oauth.claude_code.authenticate_and_save", return_value=True),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)"]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is True


def test_configure_model_claude_code_oauth_no_existing_fail(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value=None),
            mock.patch("gac.oauth.claude_code.authenticate_and_save", return_value=False),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)"]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is False


def test_model_command_configure_returns_false(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with mock.patch("gac.model_cli._configure_model", return_value=False):
            runner = CliRunner()
            result = runner.invoke(model)
            assert result.exit_code == 0
            assert "Model configuration complete" not in result.output


def test_configure_model_claude_code_oauth_cancel_action(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            mock.patch("questionary.select") as mselect,
            mock.patch("questionary.text") as mtext,
            mock.patch("gac.model_cli.set_key"),
            mock.patch("gac.oauth.token_store.TokenStore.get_token", return_value={"access_token": "existing"}),
        ):
            mselect.return_value.ask.side_effect = ["Claude Code (OAuth)", None]
            mtext.return_value.ask.side_effect = ["claude-sonnet-4-6"]

            result = _configure_model({})
            assert result is True


def test_configure_model_provider_key_aliases(tmp_path):
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    alias_providers = [
        ("Kimi for Coding", "kimi-coding"),
        ("MiniMax.io", "minimax"),
        ("Moonshot AI", "moonshot"),
        ("Synthetic.new", "synthetic"),
    ]

    for provider_name, expected_key in alias_providers:
        with mock.patch("gac.model_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
                mock.patch("gac.model_cli.set_key") as mset,
            ):
                mselect.return_value.ask.side_effect = [provider_name]
                mtext.return_value.ask.side_effect = ["test-model"]
                mpass.return_value.ask.side_effect = ["test-key"]

                result = _configure_model({})
                assert result is True
                model_call = mset.call_args_list[0]
                assert f"{expected_key}:test-model" in model_call[0][2]
