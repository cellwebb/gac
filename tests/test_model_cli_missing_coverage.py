"""Additional tests to improve model_cli coverage."""

from unittest.mock import patch

from gac.model_cli import _configure_model


def test_configure_model_anthropic_provider(tmp_path):
    """Test Anthropic provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Anthropic provider
            mselect.return_value.ask.return_value = "Anthropic"
            mtext.return_value.ask.return_value = "claude-sonnet-4-5"
            mpass.return_value.ask.return_value = "sk-ant-api-key"

            result = _configure_model({})

            assert result is True
            # Verify that set_key was called at least twice (GAC_MODEL and API_KEY)
            assert mock_set_key.call_count >= 2

            # Just verify that the function ran successfully and made calls
            # (the actual values are confirmed by the stdout output)


def test_configure_model_simple_provider(tmp_path):
    """Test a simple provider without special handling."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select a simple provider
            mselect.return_value.ask.return_value = "DeepSeek"
            mtext.return_value.ask.return_value = "deepseek-chat"
            mpass.return_value.ask.return_value = "deepseek-key"

            result = _configure_model({})

            assert result is True
            # Verify that set_key was called (should have model and API key)
            assert mock_set_key.call_count >= 2


def test_configure_model_provider_cancellation(tmp_path):
    """Test provider selection cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with patch("questionary.select") as mselect, patch("gac.model_cli.click.echo") as mock_echo:
            # Provider selection returns None (cancellation)
            mselect.return_value.ask.return_value = None

            result = _configure_model({})

            assert result is False
            mock_echo.assert_called_with("Provider selection cancelled. Exiting.")


def test_configure_model_streamlake_cancellation(tmp_path):
    """Test Streamlake endpoint ID cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Streamlake provider
            mselect.return_value.ask.return_value = "Streamlake"
            # Cancel endpoint ID entry
            mtext.return_value.ask.return_value = None

            result = _configure_model({})

            assert result is False
            mock_echo.assert_called_with("Streamlake configuration cancelled. Exiting.")


def test_configure_model_streamlake_success(tmp_path):
    """Test successful Streamlake provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Streamlake provider
            mselect.return_value.ask.return_value = "Streamlake"
            # Return endpoint ID
            mtext.return_value.ask.return_value = "endpoint-123"
            # Skip API key (optional for local providers)
            mpass.return_value.ask.return_value = ""

            result = _configure_model({})

            assert result is True
            # Should have called set_key for the model
            assert mock_set_key.call_count >= 1


def test_configure_model_custom_anthropic_success(tmp_path):
    """Test successful Custom Anthropic provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Custom Anthropic provider
            mselect.return_value.ask.return_value = "Custom (Anthropic)"
            mtext.return_value.ask.side_effect = ["custom-model", "https://custom-anthropic.com", "2024-01-01"]
            mpass.return_value.ask.return_value = "custom-key"

            result = _configure_model({})

            assert result is True
            # Should have multiple set_key calls (model, base URL, version, API key)
            assert mock_set_key.call_count >= 3


def test_configure_model_ollama_success(tmp_path):
    """Test successful Ollama provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Ollama provider
            mselect.return_value.ask.return_value = "Ollama"
            mtext.return_value.ask.return_value = "http://localhost:11434"
            mpass.return_value.ask.return_value = ""  # Skip API key for local provider

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API URL
            assert mock_set_key.call_count >= 2


def test_configure_model_lmstudio_success(tmp_path):
    """Test successful LM Studio provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select LM Studio provider
            mselect.return_value.ask.return_value = "LM Studio"
            mtext.return_value.ask.return_value = "http://localhost:1234"
            mpass.return_value.ask.return_value = ""  # Skip API key for local provider

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API URL
            assert mock_set_key.call_count >= 2
