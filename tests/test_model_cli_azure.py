"""Tests for Azure OpenAI specific model_cli flows to improve coverage."""

from unittest.mock import patch

from gac.model_cli import _configure_model


def test_configure_model_azure_openai_new_endpoint_and_version(tmp_path):
    """Test Azure OpenAI provider configuration with new endpoint and version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.return_value = "Azure OpenAI"
            # First call: model, then endpoint (no existing), then version (no existing)
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                "https://test.openai.azure.com",  # endpoint
                "2025-01-01-preview",  # API version
            ]
            mpass.return_value.ask.return_value = "azure-test-key"

            result = _configure_model({})  # Empty existing env

            assert result is True
            # Should have set_key calls for model, endpoint, version, and API key
            assert mock_set_key.call_count >= 4


def test_configure_model_azure_openai_keep_existing_endpoint_new_version(tmp_path):
    """Test Azure OpenAI provider keeping existing endpoint but setting new version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"AZURE_OPENAI_ENDPOINT": "https://existing.openai.azure.com"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Enter new version",  # Version action (since no existing version)
            ]
            # Model, then new version
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                "2025-02-01-preview",  # new API version
            ]
            mpass.return_value.ask.return_value = "azure-test-key"

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model, version, and API key (endpoint kept)
            assert mock_set_key.call_count >= 3


def test_configure_model_azure_openai_keep_existing_endpoint_and_version(tmp_path):
    """Test Azure OpenAI provider keeping both existing endpoint and version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {
        "AZURE_OPENAI_ENDPOINT": "https://existing.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-12-01-preview",
    }

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Keep existing endpoint",  # Endpoint action
                "Keep existing version",  # Version action
            ]
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model only
            mpass.return_value.ask.return_value = "azure-test-key"

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model and API key only (endpoint and version kept)
            assert mock_set_key.call_count >= 2


def test_configure_model_azure_openai_endpoint_cancellation(tmp_path):
    """Test Azure OpenAI provider endpoint entry cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"AZURE_OPENAI_ENDPOINT": "https://existing.openai.azure.com"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Enter new endpoint",  # Endpoint action
            ]
            # Model, then cancel endpoint
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                None,  # cancel endpoint
            ]

            result = _configure_model(existing_env)

            assert result is False
            mock_echo.assert_called_with("Azure OpenAI endpoint entry cancelled. Exiting.")


def test_configure_model_azure_openai_version_cancellation(tmp_path):
    """Test Azure OpenAI provider API version entry cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli._prompt_required_text") as mock_prompt,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Enter new version",  # Version action (no existing version)
            ]
            # Model, then cancel endpoint (required first), then cancel version
            mtext.return_value.ask.return_value = "gpt-5-mini"  # model
            mock_prompt.side_effect = [None, None]  # cancel endpoint, then cancel version

            result = _configure_model({})  # No existing env

            assert result is False
            mock_echo.assert_called_with("Azure OpenAI endpoint entry cancelled. Exiting.")


def test_configure_model_azure_openai_empty_version_cancellation(tmp_path):
    """Test Azure OpenAI provider empty API version entry cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli._prompt_required_text") as mock_prompt,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Enter new version",  # Version action (no existing version)
            ]
            # Mock model entry and endpoint entry
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                "",  # empty API version
                None,  # cancel confirm
            ]
            # Provide valid endpoint first, then cancel version
            mock_prompt.return_value = "https://test.openai.azure.com"  # valid endpoint

            result = _configure_model({})  # No existing env

            assert result is False
            mock_echo.assert_called_with("Azure OpenAI API version entry cancelled. Exiting.")


def test_configure_model_azure_openai_keep_endpoint_new_version(tmp_path):
    """Test Azure OpenAI provider keeping existing endpoint but entering new version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"AZURE_OPENAI_ENDPOINT": "https://existing.openai.azure.com"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Keep existing endpoint",  # Endpoint action
                "Enter new version",  # Version action (no existing version)
            ]
            # Model, then new API version
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                "2025-03-01-preview",  # new API version
            ]
            mpass.return_value.ask.return_value = "azure-test-key"

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model, version, and API key
            assert mock_set_key.call_count >= 3


def test_configure_model_azure_openai_new_endpoint_keep_version(tmp_path):
    """Test Azure OpenAI provider entering new endpoint but keeping existing version."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    existing_env = {"AZURE_OPENAI_API_VERSION": "2024-12-01-preview"}

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Azure OpenAI provider
            mselect.return_value.ask.side_effect = [
                "Azure OpenAI",  # Provider selection
                "Enter new endpoint",  # Endpoint action (no existing endpoint)
                "Keep existing version",  # Version action (existing version exists)
            ]
            # Model, then new endpoint
            mtext.return_value.ask.side_effect = [
                "gpt-5-mini",  # model
                "https://new.openai.azure.com",  # new endpoint
            ]
            mpass.return_value.ask.return_value = "azure-test-key"

            result = _configure_model(existing_env)

            assert result is True
            # Should have set_key calls for model, endpoint, and API key
            assert mock_set_key.call_count >= 3
