"""Additional targeted tests for init_cli to reach higher coverage."""

import tempfile
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
from click.testing import CliRunner

from gac.init_cli import (
    _configure_language,
    _configure_model,
    _should_show_rtl_warning_for_init,
    _show_rtl_warning_for_init,
    init,
    model,
)


@pytest.fixture(autouse=True)
def patch_gac_env_path(tmp_path, monkeypatch):
    env_path = tmp_path / ".gac.env"
    monkeypatch.setattr("gac.init_cli.GAC_ENV_PATH", env_path)
    yield env_path


def test_should_show_rtl_warning_returns_true_when_no_env(monkeypatch, patch_gac_env_path):
    monkeypatch.delenv("GAC_RTL_CONFIRMED", raising=False)

    result = _should_show_rtl_warning_for_init()

    assert result is True


def test_should_show_rtl_warning_respects_stored_confirmation(monkeypatch, patch_gac_env_path):
    monkeypatch.delenv("GAC_RTL_CONFIRMED", raising=False)
    patch_gac_env_path.write_text("GAC_RTL_CONFIRMED=true\n")

    result = _should_show_rtl_warning_for_init()

    assert result is False
    monkeypatch.delenv("GAC_RTL_CONFIRMED", raising=False)


def test_show_rtl_warning_accepts_and_persists(monkeypatch, patch_gac_env_path):
    confirm_prompt = MagicMock()
    confirm_prompt.ask.return_value = True

    with (
        patch("questionary.confirm", return_value=confirm_prompt),
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("click.echo"),
    ):
        result = _show_rtl_warning_for_init("Arabic")

    assert result is True
    mock_set_key.assert_any_call(str(patch_gac_env_path), "GAC_RTL_CONFIRMED", "true")


def test_show_rtl_warning_handles_cancelled_prompt():
    confirm_prompt = MagicMock()
    confirm_prompt.ask.return_value = None

    with (
        patch("questionary.confirm", return_value=confirm_prompt),
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("click.echo"),
    ):
        result = _show_rtl_warning_for_init("Arabic")

    assert result is False
    mock_set_key.assert_not_called()


def test_configure_model_custom_anthropic_provider():
    """Test _configure_model with Custom (Anthropic) provider."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("gac.init_cli._prompt_required_text") as mock_prompt_required,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
    ):
        mock_select.return_value.ask.return_value = "Custom (Anthropic)"
        mock_prompt_required.return_value = "https://api.anthropic-custom.com"
        mock_text.return_value.ask.return_value = "custom-version"  # Custom version
        mock_password.return_value.ask.return_value = "sk-custom-key"

        with patch("click.echo"):
            with patch("gac.init_cli.set_key") as mock_set_key:
                result = _configure_model(existing_env)

        assert result is True
        # Should have set various config keys
        mock_set_key.assert_any_call(ANY, "GAC_MODEL", ANY)
        mock_set_key.assert_any_call(ANY, "CUSTOM_ANTHROPIC_BASE_URL", "https://api.anthropic-custom.com")
        mock_set_key.assert_any_call(ANY, "CUSTOM_ANTHROPIC_VERSION", "custom-version")


def test_configure_model_custom_anthropic_provider_cancel_base_url():
    """Test _configure_model with Custom (Anthropic) provider but user cancels base URL entry."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("gac.init_cli._prompt_required_text") as mock_prompt_required,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
    ):
        mock_select.return_value.ask.return_value = "Custom (Anthropic)"
        mock_prompt_required.return_value = None  # User cancels
        mock_text.return_value.ask.return_value = "gpt-4"  # Model
        mock_password.return_value.ask.return_value = "sk-key"  # Password

        with patch("click.echo"):
            result = _configure_model(existing_env)

        assert result is False


def test_configure_model_custom_openai_provider():
    """Test _configure_model with Custom (OpenAI) provider."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("gac.init_cli._prompt_required_text") as mock_prompt_required,
        patch("questionary.password") as mock_password,
        patch("questionary.text") as mock_text,
    ):
        mock_select.return_value.ask.return_value = "Custom (OpenAI)"
        mock_prompt_required.return_value = "https://api.openai-custom.com"
        mock_text.return_value.ask.return_value = "gpt-4"  # Model
        mock_password.return_value.ask.return_value = "sk-custom-openai-key"

        with patch("click.echo"):
            with patch("gac.init_cli.set_key") as mock_set_key:
                result = _configure_model(existing_env)

        assert result is True
        # Should have set various config keys
        mock_set_key.assert_any_call(ANY, "GAC_MODEL", ANY)
        mock_set_key.assert_any_call(ANY, "CUSTOM_OPENAI_BASE_URL", "https://api.openai-custom.com")


def test_configure_model_custom_openai_provider_cancel_base_url():
    """Test _configure_model with Custom (OpenAI) provider but user cancels base URL entry."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("gac.init_cli._prompt_required_text") as mock_prompt_required,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
    ):
        mock_select.return_value.ask.return_value = "Custom (OpenAI)"
        mock_prompt_required.return_value = None  # User cancels
        mock_text.return_value.ask.return_value = "gpt-4"  # Model
        mock_password.return_value.ask.return_value = "sk-key"  # Password

        with patch("click.echo"):
            result = _configure_model(existing_env)

        assert result is False


def test_configure_model_ollama_provider_default_url():
    """Test _configure_model with Ollama provider using default URL."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
    ):
        mock_select.return_value.ask.return_value = "Ollama"
        mock_text.return_value.ask.return_value = ""  # Empty string should use default
        mock_password.return_value.ask.return_value = ""

        with patch("click.echo"):
            with patch("gac.init_cli.set_key") as mock_set_key:
                result = _configure_model(existing_env)

        assert result is True
        # Should have set default URL
        mock_set_key.assert_any_call(ANY, "OLLAMA_API_URL", "http://localhost:11434")


def test_configure_model_ollama_provider_cancel_url():
    """Test _configure_model with Ollama provider but user cancels URL entry."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
    ):
        mock_select.return_value.ask.return_value = "Ollama"
        mock_text.return_value.ask.return_value = None  # User cancels

        result = _configure_model(existing_env)

        assert result is False


def test_configure_model_lmstudio_provider_default_url():
    """Test _configure_model with LM Studio provider using default URL."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
    ):
        mock_select.return_value.ask.return_value = "LM Studio"
        mock_text.return_value.ask.return_value = ""  # Empty string should use default
        mock_password.return_value.ask.return_value = ""

        with patch("click.echo"):
            with patch("gac.init_cli.set_key") as mock_set_key:
                result = _configure_model(existing_env)

        assert result is True
        # Should have set default URL
        mock_set_key.assert_any_call(ANY, "LMSTUDIO_API_URL", "http://localhost:1234")


def test_configure_model_lmstudio_provider_cancel_url():
    """Test _configure_model with LM Studio provider but user cancels URL entry."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
    ):
        mock_select.return_value.ask.return_value = "LM Studio"
        mock_text.return_value.ask.return_value = None  # User cancels

        result = _configure_model(existing_env)

        assert result is False


def test_configure_model_zai_provider_existing_key():
    """Test _configure_model with Z.AI provider when existing key is present."""
    existing_env = {"ZAI_API_KEY": "existing-key"}

    with (
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key"),
    ):
        # Mock the first select (provider selection)
        mock_provider_select = MagicMock()
        mock_provider_select.ask.return_value = "Z.AI"

        # Mock the second select (key action selection)
        mock_key_action = MagicMock()
        mock_key_action.ask.return_value = "Keep existing key"

        with (
            patch("click.echo") as mock_echo,
            patch("questionary.select") as mock_select,
        ):
            # configure_provider and key action calls
            mock_select.side_effect = [mock_provider_select, mock_key_action]
            mock_text.return_value.ask.return_value = "glm-4.5-air"
            mock_password.return_value.ask.return_value = "sk-key"

            result = _configure_model(existing_env)

        assert result is True
        # Should have shown message about existing key
        mock_echo.assert_any_call("\nZAI_API_KEY is already configured.")
        mock_echo.assert_any_call("Keeping existing ZAI_API_KEY")


def test_configure_model_zai_provider_existing_key_action_none():
    """Test _configure_model when user cancels the key action selection."""
    existing_env = {"ZAI_API_KEY": "existing-key"}

    with (
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key"),
    ):
        # Mock the first select (provider selection)
        mock_provider_select = MagicMock()
        mock_provider_select.ask.return_value = "Z.AI"

        # Mock the second select (key action selection) - returns None (cancel)
        mock_key_action = MagicMock()
        mock_key_action.ask.return_value = None

        with (
            patch("click.echo") as mock_echo,
            patch("questionary.select") as mock_select,
        ):
            mock_select.side_effect = [mock_provider_select, mock_key_action]
            mock_text.return_value.ask.return_value = "glm-4.5-air"
            mock_password.return_value.ask.return_value = "sk-key"

            result = _configure_model(existing_env)

        assert result is True
        # Should have shown cancel message
        mock_echo.assert_any_call("API key configuration cancelled. Keeping existing key.")


def test_configure_model_with_empty_existing_key_enter_new():
    """Test _configure_model when existing key is present and user enters new empty key."""
    existing_env = {"OPENAI_API_KEY": "existing-key"}

    with (
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key"),
    ):
        # Mock the first select (provider selection)
        mock_provider_select = MagicMock()
        mock_provider_select.ask.return_value = "OpenAI"

        # Mock for key action - enter new key
        mock_key_action = MagicMock()
        mock_key_action.ask.return_value = "Enter new key"

        with (
            patch("click.echo") as mock_echo,
            patch("questionary.select") as mock_select,
        ):
            mock_select.side_effect = [mock_provider_select, mock_key_action]
            mock_text.return_value.ask.return_value = "gpt-4"
            mock_password.return_value.ask.return_value = ""  # Empty key

            result = _configure_model(existing_env)

        assert result is True
        # Should have shown message about no key entered
        mock_echo.assert_any_call("No key entered. Keeping existing OPENAI_API_KEY")


def test_configure_model_local_provider_skip_key():
    """Test _configure_model with local provider (Ollama) and skip API key."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key"),
    ):
        mock_select.return_value.ask.return_value = "Ollama"
        mock_text.return_value.ask.return_value = "http://localhost:11434"
        mock_password.return_value.ask.return_value = ""  # Skip key entry

        with patch("click.echo") as mock_echo:
            result = _configure_model(existing_env)

        assert result is True
        # Should show skipping message for local providers
        mock_echo.assert_any_call("Skipping API key. You can add one later if needed.")


def test_configure_model_minimax_normalizes_provider_and_warns_missing_key():
    """Ensure MiniMax.io provider key is normalized and warning is shown for blank API key."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("click.echo") as mock_echo,
    ):
        mock_select.return_value.ask.return_value = "MiniMax.io"
        mock_text.return_value.ask.return_value = ""  # Use default suggestion
        mock_password.return_value.ask.return_value = ""  # Missing API key triggers warning

        result = _configure_model(existing_env)

    assert result is True
    mock_set_key.assert_any_call(ANY, "GAC_MODEL", "minimax:MiniMax-M2")
    mock_echo.assert_any_call("No API key entered. You can add one later by editing ~/.gac.env")


def test_configure_model_synthetic_normalizes_provider_key():
    """Ensure Synthetic.new provider key is normalized and API key stored."""
    existing_env = {}

    with (
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("click.echo"),
    ):
        mock_select.return_value.ask.return_value = "Synthetic.new"
        mock_text.return_value.ask.return_value = "hf:zai-org/GLM-4.6"
        mock_password.return_value.ask.return_value = "sk-synthetic"

        result = _configure_model(existing_env)

    assert result is True
    mock_set_key.assert_any_call(ANY, "GAC_MODEL", "synthetic:hf:zai-org/GLM-4.6")
    mock_set_key.assert_any_call(ANY, "SYNTHETIC_API_KEY", "sk-synthetic")


def test_configure_model_claude_code_action_cancelled(monkeypatch):
    """Ensure cancelling Claude Code action shows message and skips re-auth."""
    existing_env = {}
    monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: "existing-token")
    forbid_auth = MagicMock()
    monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", forbid_auth)

    provider_select = MagicMock()
    provider_select.ask.return_value = "Claude Code"
    action_select = MagicMock()
    action_select.ask.return_value = None  # User cancelled secondary prompt

    with (
        patch("questionary.text") as mock_text,
        patch("questionary.password") as mock_password,
        patch("questionary.select") as mock_select,
        patch("click.echo") as mock_echo,
    ):
        mock_text.return_value.ask.return_value = "claude-sonnet-4-5"
        mock_password.return_value.ask.return_value = "sk-token"
        mock_select.side_effect = [provider_select, action_select]

        result = _configure_model(existing_env)

    assert result is True
    forbid_auth.assert_not_called()
    mock_echo.assert_any_call("Claude Code configuration cancelled. Keeping existing token.")


def test_configure_language_cancel_existing_language():
    """Test _configure_language when user cancels existing language action."""
    existing_env = {"GAC_LANGUAGE": "Spanish", "GAC_TRANSLATE_PREFIXES": "false"}

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
    ):
        mock_select.return_value.ask.return_value = None  # User cancels

        _configure_language(existing_env)

        # Should show cancel message
        mock_echo.assert_any_call("Language configuration cancelled. Keeping existing language.")


def test_configure_language_select_new_english():
    """Test _configure_language when selecting new English language."""
    existing_env = {"GAC_LANGUAGE": "Spanish"}

    with (
        patch("click.echo"),
        patch("questionary.select") as mock_select,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("gac.init_cli._should_show_rtl_warning_for_init", return_value=True),
    ):
        # First select: "Select new language", then "English", then prefix choice
        mock_select.return_value.ask.side_effect = [
            "Select new language",
            "English",
            "Keep prefixes in English (feat:, fix:, etc.)",
        ]

        _configure_language(existing_env)

        # Should have set English language settings
        mock_set_key.assert_any_call(ANY, "GAC_LANGUAGE", "English")
        mock_set_key.assert_any_call(ANY, "GAC_TRANSLATE_PREFIXES", "false")


def test_configure_language_select_new_custom_cancel():
    """Test _configure_language when selecting custom but user cancels language entry."""
    existing_env = {"GAC_LANGUAGE": "Spanish"}

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
    ):
        # First select: "Select new language", then "Custom"
        mock_select.return_value.ask.side_effect = ["Select new language", "Custom"]
        mock_text.return_value.ask.return_value = ""  # User cancels/enters empty

        _configure_language(existing_env)

        # Should show cancel message
        mock_echo.assert_any_call("No language entered. Keeping existing language.")


def test_configure_language_no_existing_cancel_selection():
    """Test _configure_language when no existing language and user cancels selection."""
    existing_env = {}  # No existing language

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
    ):
        mock_select.return_value.ask.return_value = None  # User cancels

        _configure_language(existing_env)

        # Should show cancel message for new language flow
        mock_echo.assert_any_call("Language selection cancelled. Using English (default).")


def test_configure_language_no_existing_custom_cancel():
    """Test _configure_language when no existing language, custom selected, user cancels."""
    existing_env = {}  # No existing language

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
    ):
        mock_select.return_value.ask.return_value = "Custom"
        mock_text.return_value.ask.return_value = ""  # User cancels/enters empty

        _configure_language(existing_env)

        # Should show cancel message for new language flow
        mock_echo.assert_any_call("No language entered. Using English (default).")


def test_configure_language_existing_custom_rtl_warning_preconfirmed():
    """Custom RTL language with existing config should skip warning prompt when already confirmed."""
    existing_env = {"GAC_LANGUAGE": "English", "GAC_TRANSLATE_PREFIXES": "false"}

    with (
        patch("click.echo"),
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("gac.language_cli.is_rtl_text", return_value=True),
        patch("gac.init_cli._should_show_rtl_warning_for_init", return_value=False),
        patch("gac.init_cli._show_rtl_warning_for_init") as mock_show_warning,
    ):
        mock_select.return_value.ask.side_effect = [
            "Select new language",
            "Custom",
            "Translate prefixes into עברית",
        ]
        mock_text.return_value.ask.return_value = " עברית "

        _configure_language(existing_env)

    mock_show_warning.assert_not_called()
    mock_set_key.assert_any_call(ANY, "GAC_LANGUAGE", "עברית")
    mock_set_key.assert_any_call(ANY, "GAC_TRANSLATE_PREFIXES", "true")


def test_configure_language_existing_predefined_rtl_user_cancels():
    """Existing config, predefined RTL language, user cancels after warning."""
    existing_env = {"GAC_LANGUAGE": "English"}

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
        patch("gac.language_cli.is_rtl_text", side_effect=lambda value: value == "Arabic"),
        patch("gac.init_cli._should_show_rtl_warning_for_init", return_value=True),
        patch("gac.init_cli._show_rtl_warning_for_init", return_value=False) as mock_warning,
    ):
        mock_select.return_value.ask.side_effect = [
            "Select new language",
            "العربية",
        ]

        _configure_language(existing_env)

    mock_warning.assert_called_once_with("Arabic")
    mock_echo.assert_any_call("Language selection cancelled. Keeping existing language.")


def test_configure_language_no_existing_custom_prefix_cancel():
    """No existing language, RTL custom selection proceeds but prefix prompt cancelled."""
    existing_env = {}

    with (
        patch("click.echo") as mock_echo,
        patch("questionary.select") as mock_select,
        patch("questionary.text") as mock_text,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("gac.language_cli.is_rtl_text", return_value=True),
        patch("gac.init_cli._should_show_rtl_warning_for_init", return_value=True),
        patch("gac.init_cli._show_rtl_warning_for_init", return_value=True) as mock_warning,
    ):
        mock_select.return_value.ask.side_effect = [
            "Custom",
            None,
        ]
        mock_text.return_value.ask.return_value = "עברית"

        _configure_language(existing_env)

    mock_warning.assert_called_once_with("עברית")
    mock_echo.assert_any_call("Prefix translation selection cancelled. Using English prefixes.")
    mock_set_key.assert_any_call(ANY, "GAC_LANGUAGE", "עברית")
    mock_set_key.assert_any_call(ANY, "GAC_TRANSLATE_PREFIXES", "false")


def test_configure_language_no_existing_predefined_translate_prefixes():
    """No existing language, predefined selection should set translation flag when chosen."""
    existing_env = {}

    with (
        patch("click.echo"),
        patch("questionary.select") as mock_select,
        patch("gac.init_cli.set_key") as mock_set_key,
        patch("gac.language_cli.is_rtl_text", return_value=False),
    ):
        mock_select.return_value.ask.side_effect = [
            "Français",
            "Translate prefixes into French",
        ]

        _configure_language(existing_env)

    mock_set_key.assert_any_call(ANY, "GAC_LANGUAGE", "French")
    mock_set_key.assert_any_call(ANY, "GAC_TRANSLATE_PREFIXES", "true")


def test_init_command_configure_model_fails():
    """Test init command when _configure_model returns False."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.init_cli.GAC_ENV_PATH", fake_path),
            patch("gac.init_cli._configure_model") as mock_configure,
            patch("click.echo"),
        ):
            mock_configure.return_value = False  # Configuration fails

            result = runner.invoke(init)

            assert result.exit_code == 0
            # Should not call _configure_language when _configure_model fails


def test_init_command_configure_model_succeeds():
    """Test init command when _configure_model succeeds and calls language config."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.init_cli.GAC_ENV_PATH", fake_path),
            patch("gac.init_cli._configure_model") as mock_configure,
            patch("gac.init_cli._configure_language") as mock_configure_lang,
            patch("gac.init_cli._load_existing_env") as mock_load,
            patch("click.echo"),
        ):
            mock_configure.return_value = True  # Configuration succeeds
            mock_load.return_value = {}

            result = runner.invoke(init)

            assert result.exit_code == 0
            # Should call language configuration when model config succeeds
            mock_configure_lang.assert_called_once_with({})


def test_model_command_configure_model_fails():
    """Test model command when _configure_model returns False."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.init_cli.GAC_ENV_PATH", fake_path),
            patch("gac.init_cli._configure_model") as mock_configure,
            patch("click.echo"),
        ):
            mock_configure.return_value = False  # Configuration fails

            result = runner.invoke(model)

            assert result.exit_code == 0
            # Should print failure message and return early when _configure_model fails


def test_model_command_success_message():
    """Test model command completes and prints final reminder."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.init_cli.GAC_ENV_PATH", fake_path),
            patch("gac.init_cli._configure_model", return_value=True),
            patch("gac.init_cli._load_existing_env", return_value={}),
            patch("click.echo") as mock_echo,
        ):
            result = runner.invoke(model)

    assert result.exit_code == 0
    mock_echo.assert_any_call(f"\nModel configuration complete. You can edit {fake_path} to update values later.")
