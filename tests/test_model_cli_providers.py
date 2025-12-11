"""Tests for additional provider configurations in model_cli to improve coverage."""

from unittest.mock import patch

from gac.model_cli import _configure_model


def test_configure_model_custom_openai_success(tmp_path):
    """Test successful Custom OpenAI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Custom OpenAI provider
            mselect.return_value.ask.return_value = "Custom (OpenAI)"
            mtext.return_value.ask.return_value = "https://custom-openai.example.com"
            mpass.return_value.ask.return_value = "custom-openai-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and base URL and API key
            assert mock_set_key.call_count >= 3


def test_configure_model_custom_openai_cancellation(tmp_path):
    """Test Custom OpenAI provider base URL cancellation."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("gac.model_cli._prompt_required_text") as mock_prompt,
            patch("gac.model_cli.click.echo") as mock_echo,
        ):
            # Select Custom OpenAI provider
            mselect.return_value.ask.return_value = "Custom (OpenAI)"
            # Provide model name, then cancel base URL entry
            mtext.return_value.ask.return_value = "custom-model"
            mock_prompt.return_value = None  # Cancel base URL

            result = _configure_model({})

            assert result is False
            mock_echo.assert_called_with("Custom OpenAI base URL entry cancelled. Exiting.")


def test_configure_model_zai_success(tmp_path):
    """Test successful Z.AI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Z.AI provider
            mselect.return_value.ask.return_value = "Z.AI"
            mtext.return_value.ask.return_value = "glm-4.5-air"
            mpass.return_value.ask.return_value = "zai-api-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and ZAI_API_KEY
            assert mock_set_key.call_count >= 2


def test_configure_model_zai_coding_success(tmp_path):
    """Test successful Z.AI Coding provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Z.AI Coding provider
            mselect.return_value.ask.return_value = "Z.AI Coding"
            mtext.return_value.ask.return_value = "glm-4.6"
            mpass.return_value.ask.return_value = "zai-coding-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and ZAI_API_KEY
            assert mock_set_key.call_count >= 2


def test_configure_model_fireworks_success(tmp_path):
    """Test successful Fireworks provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Fireworks provider
            mselect.return_value.ask.return_value = "Fireworks"
            mtext.return_value.ask.return_value = "accounts/fireworks/models/gpt-oss-20b"
            mpass.return_value.ask.return_value = "fireworks-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_cerebras_success(tmp_path):
    """Test successful Cerebras provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Cerebras provider
            mselect.return_value.ask.return_value = "Cerebras"
            mtext.return_value.ask.return_value = "zai-glm-4.6"
            mpass.return_value.ask.return_value = "cerebras-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_moonshot_success(tmp_path):
    """Test successful Moonshot AI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Moonshot AI provider
            mselect.return_value.ask.return_value = "Moonshot AI"
            mtext.return_value.ask.return_value = "kimi-k2-thinking-turbo"
            mpass.return_value.ask.return_value = "moonshot-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_minimax_success(tmp_path):
    """Test successful MiniMax.io provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select MiniMax.io provider
            mselect.return_value.ask.return_value = "MiniMax.io"
            mtext.return_value.ask.return_value = "MiniMax-M2"
            mpass.return_value.ask.return_value = "minimax-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_mistral_success(tmp_path):
    """Test successful Mistral provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Mistral provider
            mselect.return_value.ask.return_value = "Mistral"
            mtext.return_value.ask.return_value = "devstral-2512"
            mpass.return_value.ask.return_value = "mistral-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_openrouter_success(tmp_path):
    """Test successful OpenRouter provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select OpenRouter provider
            mselect.return_value.ask.return_value = "OpenRouter"
            mtext.return_value.ask.return_value = "openrouter/auto"
            mpass.return_value.ask.return_value = "openrouter-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configureModel_replicate_success(tmp_path):
    """Test successful Replicate provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Replicate provider
            mselect.return_value.ask.return_value = "Replicate"
            mtext.return_value.ask.return_value = "openai/gpt-oss-120b"
            mpass.return_value.ask.return_value = "replicate-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_together_success(tmp_path):
    """Test successful Together AI provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Together AI provider
            mselect.return_value.ask.return_value = "Together AI"
            mtext.return_value.ask.return_value = "openai/gpt-oss-20B"
            mpass.return_value.ask.return_value = "together-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_chutes_success(tmp_path):
    """Test successful Chutes provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Chutes provider
            mselect.return_value.ask.return_value = "Chutes"
            mtext.return_value.ask.return_value = "zai-org/GLM-4.6-FP8"
            mpass.return_value.ask.return_value = "chutes-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_synthetic_success(tmp_path):
    """Test successful Synthetic.new provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Synthetic.new provider
            mselect.return_value.ask.return_value = "Synthetic.new"
            mtext.return_value.ask.return_value = "hf:zai-org/GLM-4.6"
            mpass.return_value.ask.return_value = "synthetic-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_groq_success(tmp_path):
    """Test successful Groq provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Groq provider
            mselect.return_value.ask.return_value = "Groq"
            mtext.return_value.ask.return_value = "meta-llama/llama-4-maverick-17b-128e-instruct"
            mpass.return_value.ask.return_value = "groq-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_gemini_success(tmp_path):
    """Test successful Gemini provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Gemini provider
            mselect.return_value.ask.return_value = "Gemini"
            mtext.return_value.ask.return_value = "gemini-2.5-flash"
            mpass.return_value.ask.return_value = "gemini-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_kimi_coding_success(tmp_path):
    """Test successful Kimi for Coding provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select Kimi for Coding provider
            mselect.return_value.ask.return_value = "Kimi for Coding"
            mtext.return_value.ask.return_value = "kimi-for-coding"
            mpass.return_value.ask.return_value = "kimi-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2


def test_configure_model_deepseek_success(tmp_path):
    """Test successful DeepSeek provider configuration."""
    env_path = tmp_path / ".gac.env"
    env_path.touch()

    with patch("gac.model_cli.GAC_ENV_PATH", env_path):
        with (
            patch("questionary.select") as mselect,
            patch("questionary.text") as mtext,
            patch("questionary.password") as mpass,
            patch("gac.model_cli.set_key") as mock_set_key,
        ):
            # Select DeepSeek provider
            mselect.return_value.ask.return_value = "DeepSeek"
            mtext.return_value.ask.return_value = "deepseek-chat"
            mpass.return_value.ask.return_value = "deepseek-key"

            result = _configure_model({})

            assert result is True
            # Should have set_key calls for model and API key
            assert mock_set_key.call_count >= 2
