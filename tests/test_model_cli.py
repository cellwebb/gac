"""Tests for model_cli module."""

from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.model_cli import (
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
