"""Tests for API key handling scenarios in model_cli to improve coverage."""

from unittest.mock import patch

from gac.model_cli import _configure_model


def test_configure_model_api_key_existing_keep(tmp_path):
    """Test provider with existing API key - keep existing key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"OPENAI_API_KEY": "existing-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password"),
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.side_effect = [
                "OpenAI",  # Provider selection
                "Keep existing key",  # API key action
            ]
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key call for model only
            assert mock_set_key.call_count >= 1


def test_configure_model_api_key_existing_enter_new(tmp_path):
    """Test provider with existing API key - enter new key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"OPENAI_API_KEY": "existing-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.side_effect = [
                "OpenAI",  # Provider selection
                "Enter new key",  # API key action
            ]
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model
            mpass.return_value.ask.return_value = "new-openai-key"  # new API key

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_api_key_existing_enter_empty(tmp_path):
    """Test provider with existing API key - enter empty key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"OPENAI_API_KEY": "existing-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.side_effect = [
                "OpenAI",  # Provider selection
                "Enter new key",  # API key action
            ]
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model
            mpass.return_value.ask.return_value = ""  # empty API key

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key call for model only
            assert mock_set_key.call_count >= 1
            mock_echo.assert_called_with("No key entered. Keeping existing OPENAI_API_KEY")


def test_configure_model_api_key_existing_cancel_action(tmp_path):
    """Test provider with existing API key - cancel action."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"OPENAI_API_KEY": "existing-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password"),
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.side_effect = [
                "OpenAI",  # Provider selection
                None,  # Cancel API key action
            ]
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key call for model only
            assert mock_set_key.call_count >= 1
            mock_echo.assert_called_with("API key configuration cancelled. Keeping existing key.")


def test_configure_model_api_key_new_enter(tmp_path):
    """Test provider with no existing API key - enter new key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.return_value = "OpenAI"
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model
            mpass.return_value.ask.return_value = "new-openai-key"  # API key

            result = _configure_model({})  # No existing env

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_api_key_new_skip(tmp_path):
    """Test provider with no existing API key - skip key entry."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select OpenAI provider
            mselect.return_value.ask.return_value = "OpenAI"
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model
            mpass.return_value.ask.return_value = ""  # Skip API key

            result = _configure_model({})  # No existing env

            assert result is True
            # Should have set_key call for model only
            assert mock_set_key.call_count >= 1
            mock_echo.assert_called_with("No API key entered. You can add one later by editing ~/.gac.env")


def test_configure_model_api_key_ollama_skip(tmp_path):
    """Test Ollama provider with optional API key - skip key entry."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Ollama provider
            mselect.return_value.ask.return_value = "Ollama"
            mtext.return_value.ask.return_value = "http://localhost:11434"  # URL
            mpass.return_value.ask.return_value = ""  # Skip API key

            result = _configure_model({})  # No existing env

            assert result is True
            # Should have set_key calls for model and URL
            assert mock_set_key.call_count >= 2
            mock_echo.assert_called_with("Skipping API key. You can add one later if needed.")


def test_configure_model_api_key_ollama_enter(tmp_path):
    """Test Ollama provider with optional API key - enter key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo"),
        ):
            # Select Ollama provider
            mselect.return_value.ask.return_value = "Ollama"
            mtext.return_value.ask.return_value = "http://localhost:11434"  # URL
            mpass.return_value.ask.return_value = "ollama-key"  # API key

            result = _configure_model({})  # No existing env

            assert result is True
            # Should have set_key calls for model, URL, and API key
            assert mock_set_key.call_count >= 3


def test_configure_model_api_key_lmstudio_skip(tmp_path):
    """Test LM Studio provider with optional API key - skip key entry."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select LM Studio provider
            mselect.return_value.ask.return_value = "LM Studio"
            mtext.return_value.ask.return_value = "http://localhost:1234"  # URL
            mpass.return_value.ask.return_value = ""  # Skip API key

            result = _configure_model({})  # No existing env

            assert result is True
            # Should have set_key calls for model and URL
            assert mock_set_key.call_count >= 2
            mock_echo.assert_called_with("Skipping API key. You can add one later if needed.")


def test_configure_model_api_key_lmstudio_existing_skip(tmp_path):
    """Test LM Studio provider with existing API key - skip (keep existing)."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"LMSTUDIO_API_KEY": "existing-lmstudio-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password"),
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select LM Studio provider
            mselect.return_value.ask.side_effect = [
                "LM Studio",  # Provider selection
                "Keep existing key",  # API key action
            ]
            mtext.return_value.ask.return_value = "http://localhost:1234"  # URL

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model and URL only
            assert mock_set_key.call_count >= 2


def test_configure_model_model_cancellation(tmp_path):
    """Test model entry cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Anthropic provider
            mselect.return_value.ask.return_value = "Anthropic"
            # Cancel model entry
            mtext.return_value.ask.return_value = None

            result = _configure_model({})

            assert result is False
            mock_echo.assert_called_with("Model entry cancelled. Exiting.")


def test_configure_model_custom_anthropic_cancellation(tmp_path):
    """Test Custom Anthropic provider base URL cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli._prompt_required_text") as mock_prompt,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Custom Anthropic provider
            mselect.return_value.ask.return_value = "Custom (Anthropic)"
            # Provide model name, then cancel base URL entry
            mtext.return_value.ask.return_value = "custom-model"
            mock_prompt.return_value = None  # Cancel base URL

            result = _configure_model({})

            assert result is False
            mock_echo.assert_called_with("Custom Anthropic base URL entry cancelled. Exiting.")


def test_configure_model_zai_api_key_existing_keep(tmp_path):
    """Test Z.AI provider with existing API key - keep existing key."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"ZAI_API_KEY": "existing-zai-key"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password"),
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Z.AI provider
            mselect.return_value.ask.side_effect = [
                "Z.AI",  # Provider selection
                "Keep existing key",  # API key action
            ]
            mtext.return_value.ask.return_value = "glm-4.5-air"  # model

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key call for model only
            assert mock_set_key.call_count >= 1
