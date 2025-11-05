import tempfile
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.init_cli import init


def _setup_env_file(tmpdir: str) -> Path:
    env_path = Path(tmpdir) / ".gac.env"
    env_path.touch()
    return env_path


def test_init_cli_groq(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection (English = no prefix prompt)
                mselect.return_value.ask.side_effect = ["Groq", "English"]
                mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]
                mpass.return_value.ask.side_effect = ["main-api-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='groq:meta-llama/llama-4-scout-17b-16e-instruct'" in env_text
                assert "GROQ_API_KEY='main-api-key'" in env_text


def test_init_cli_zai_regular_provider(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection
                mselect.return_value.ask.side_effect = ["Z.AI", "English"]
                mtext.return_value.ask.side_effect = ["glm-4.6"]
                mpass.return_value.ask.side_effect = ["zai-api-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='zai:glm-4.6'" in env_text
                assert "ZAI_API_KEY='zai-api-key'" in env_text


def test_init_cli_zai_coding_provider(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection
                mselect.return_value.ask.side_effect = ["Z.AI Coding", "English"]
                mtext.return_value.ask.side_effect = ["glm-4.6"]
                mpass.return_value.ask.side_effect = ["zai-api-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='zai-coding:glm-4.6'" in env_text
                assert "ZAI_API_KEY='zai-api-key'" in env_text


def test_init_cli_streamlake_requires_endpoint(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection
                mselect.return_value.ask.side_effect = ["Streamlake", "English"]
                # First text prompt is for the endpoint ID (required)
                mtext.return_value.ask.side_effect = ["ep-custom-12345"]
                mpass.return_value.ask.side_effect = ["streamlake-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='streamlake:ep-custom-12345'" in env_text
                assert "STREAMLAKE_API_KEY='streamlake-key'" in env_text


def test_init_cli_ollama_optional_api_key_and_url(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection
                mselect.return_value.ask.side_effect = ["Ollama", "English"]
                # Text prompts: model, API URL
                mtext.return_value.ask.side_effect = ["gemma3", "http://localhost:11434"]
                mpass.return_value.ask.side_effect = [""]  # optional key skipped

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='ollama:gemma3'" in env_text
                assert "OLLAMA_API_URL='http://localhost:11434'" in env_text
                assert "OLLAMA_API_KEY" not in env_text


def test_init_cli_lmstudio_optional_api_key_and_url(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, then language selection
                mselect.return_value.ask.side_effect = ["LM Studio", "English"]
                # Text prompts: model, API URL
                mtext.return_value.ask.side_effect = ["deepseek-r1-distill-qwen-7b", "http://localhost:1234"]
                mpass.return_value.ask.side_effect = [""]  # optional key skipped

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='lm-studio:deepseek-r1-distill-qwen-7b'" in env_text
                assert "LMSTUDIO_API_URL='http://localhost:1234'" in env_text
                assert "LMSTUDIO_API_KEY" not in env_text


def test_init_cli_claude_code_keep_existing_token(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: "existing-token")

            def forbid_authenticate(quiet: bool) -> bool:
                raise AssertionError("authenticate_and_save should not be called")

            monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", forbid_authenticate)

            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Claude Code", "Keep existing token", "English"]
                mtext.return_value.ask.side_effect = [""]
                mpass.return_value.ask.side_effect = []

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='claude-code:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text


def test_init_cli_claude_code_reauthenticate_success(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: "existing-token")
            auth_mock = mock.Mock(return_value=True)
            monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", auth_mock)

            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = [
                    "Claude Code",
                    "Re-authenticate (get new token)",
                    "English",
                ]
                mtext.return_value.ask.side_effect = [""]
                mpass.return_value.ask.side_effect = []

                result = runner.invoke(init)
                assert result.exit_code == 0
                auth_mock.assert_called_once_with(quiet=False)
                env_text = env_path.read_text()
                assert "GAC_MODEL='claude-code:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text


def test_init_cli_claude_code_reauthenticate_failure(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: "existing-token")
            auth_mock = mock.Mock(return_value=False)
            monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", auth_mock)

            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = [
                    "Claude Code",
                    "Re-authenticate (get new token)",
                ]
                mtext.return_value.ask.side_effect = [""]
                mpass.return_value.ask.side_effect = []

                result = runner.invoke(init)
                assert result.exit_code == 0
                auth_mock.assert_called_once_with(quiet=False)
                assert "Claude Code authentication failed. Keeping existing token." in result.output
                env_text = env_path.read_text()
                assert "GAC_MODEL='claude-code:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE" not in env_text


def test_init_cli_claude_code_first_time_success(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: None)
            auth_mock = mock.Mock(return_value=True)
            monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", auth_mock)

            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Claude Code", "English"]
                mtext.return_value.ask.side_effect = [""]
                mpass.return_value.ask.side_effect = []

                result = runner.invoke(init)
                assert result.exit_code == 0
                auth_mock.assert_called_once_with(quiet=False)
                env_text = env_path.read_text()
                assert "GAC_MODEL='claude-code:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text


def test_init_cli_claude_code_first_time_failure(monkeypatch):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            monkeypatch.setattr("gac.oauth.claude_code.load_stored_token", lambda: None)
            auth_mock = mock.Mock(return_value=False)
            monkeypatch.setattr("gac.oauth.claude_code.authenticate_and_save", auth_mock)

            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                mselect.return_value.ask.side_effect = ["Claude Code"]
                mtext.return_value.ask.side_effect = [""]
                mpass.return_value.ask.side_effect = []

                result = runner.invoke(init)
                assert result.exit_code == 0
                auth_mock.assert_called_once_with(quiet=False)
                assert "Claude Code authentication failed. Exiting." in result.output
                env_text = env_path.read_text()
                assert "GAC_MODEL='claude-code:claude-sonnet-4-5'" in env_text
                assert "GAC_LANGUAGE" not in env_text


def test_init_cli_provider_selection_cancelled():
    """Test behavior when user cancels provider selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with mock.patch("questionary.select") as mselect:
                mselect.return_value.ask.return_value = None

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Provider selection cancelled" in result.output


def test_init_cli_streamlake_endpoint_cancelled():
    """Test behavior when user cancels Streamlake endpoint entry."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                mselect.return_value.ask.return_value = "Streamlake"
                mtext.return_value.ask.return_value = None

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Streamlake configuration cancelled" in result.output


def test_init_cli_model_entry_cancelled():
    """Test behavior when user cancels model entry."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                mselect.return_value.ask.return_value = "OpenAI"
                mtext.return_value.ask.return_value = None

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Model entry cancelled" in result.output


def test_init_cli_ollama_url_cancelled():
    """Test behavior when user cancels Ollama URL entry."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                mselect.return_value.ask.return_value = "Ollama"
                mtext.return_value.ask.side_effect = ["gemma3", None]

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "Ollama URL entry cancelled" in result.output


def test_init_cli_lmstudio_url_cancelled():
    """Test behavior when user cancels LM Studio URL entry."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                mselect.return_value.ask.return_value = "LM Studio"
                mtext.return_value.ask.side_effect = ["gemma3", None]

                result = runner.invoke(init)
                assert result.exit_code == 0
                assert "LM Studio URL entry cancelled" in result.output


def test_prompt_required_text_retry_on_empty():
    """Test _prompt_required_text retries on empty input and handles cancellation."""
    from gac.init_cli import _prompt_required_text

    with mock.patch("questionary.text") as mtext:
        # Simulate: empty string, whitespace, then valid value
        mtext.return_value.ask.side_effect = ["", "  ", "valid-value"]
        with mock.patch("click.echo"):
            result = _prompt_required_text("Enter value:")
            assert result == "valid-value"


def test_prompt_required_text_cancelled():
    """Test _prompt_required_text returns None when user cancels."""
    from gac.init_cli import _prompt_required_text

    with mock.patch("questionary.text") as mtext:
        mtext.return_value.ask.return_value = None
        result = _prompt_required_text("Enter value:")
        assert result is None


def test_init_cli_existing_api_key_leave_as_is(monkeypatch):
    """Test behavior when user chooses to leave existing API key as-is."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider selection, API key action (Keep existing), language selection
                mselect.return_value.ask.side_effect = [
                    "Groq",
                    "Keep existing key",
                    "English",
                ]
                mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GROQ_API_KEY='existing-key'" in env_text
                assert "Keeping existing GROQ_API_KEY" in result.output


def test_init_cli_existing_api_key_edit_replace(monkeypatch):
    """Test behavior when user chooses to edit/replace existing API key."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='old-key'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, API key action (Enter new), language selection
                mselect.return_value.ask.side_effect = [
                    "Groq",
                    "Enter new key",
                    "English",
                ]
                mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]
                mpass.return_value.ask.side_effect = ["new-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GROQ_API_KEY='new-key'" in env_text
                assert "old-key" not in env_text
                assert "Updated GROQ_API_KEY" in result.output


def test_init_cli_existing_api_key_action_cancelled(monkeypatch):
    """Test behavior when user cancels action selection for existing API key."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider selection, API key action (cancelled), language selection
                mselect.return_value.ask.side_effect = ["Groq", None, "English"]
                mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GROQ_API_KEY='existing-key'" in env_text
                assert "Keeping existing key" in result.output


def test_init_cli_existing_api_key_edit_with_empty_input(monkeypatch):
    """Test behavior when user chooses edit but provides empty input."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider selection, API key action (Enter new), language selection
                mselect.return_value.ask.side_effect = [
                    "Groq",
                    "Enter new key",
                    "English",
                ]
                mtext.return_value.ask.side_effect = ["meta-llama/llama-4-scout-17b-16e-instruct"]
                mpass.return_value.ask.side_effect = [""]  # empty input

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GROQ_API_KEY='existing-key'" in env_text
                assert "Keeping existing GROQ_API_KEY" in result.output


def test_init_cli_existing_api_key_zai_provider(monkeypatch):
    """Test existing API key handling for Z.AI provider (uses ZAI_API_KEY)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("ZAI_API_KEY='existing-zai-key'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider selection, API key action (Keep existing), language selection
                mselect.return_value.ask.side_effect = [
                    "Z.AI",
                    "Keep existing key",
                    "English",
                ]
                mtext.return_value.ask.side_effect = ["glm-4.6"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "ZAI_API_KEY='existing-zai-key'" in env_text
                assert "Keeping existing ZAI_API_KEY" in result.output


def test_init_cli_existing_language_keep(monkeypatch):
    """Test behavior when user chooses to keep existing language."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\nGAC_LANGUAGE='Spanish'\nGAC_TRANSLATE_PREFIXES='true'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider, API key action, language action (Keep existing)
                mselect.return_value.ask.side_effect = ["Groq", "Keep existing key", "Keep existing language"]
                mtext.return_value.ask.side_effect = ["llama-4-scout"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='Spanish'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='true'" in env_text
                assert "Keeping existing language: Spanish" in result.output


def test_init_cli_existing_language_select_new(monkeypatch):
    """Test behavior when user chooses to select new language."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\nGAC_LANGUAGE='Spanish'\nGAC_TRANSLATE_PREFIXES='true'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider, API key action, language action, new language, prefix choice
                mselect.return_value.ask.side_effect = [
                    "Groq",
                    "Keep existing key",
                    "Select new language",
                    "Français",
                    "Keep prefixes in English (feat:, fix:, etc.)",
                ]
                mtext.return_value.ask.side_effect = ["llama-4-scout"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='French'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text


def test_init_cli_existing_language_action_cancelled(monkeypatch):
    """Test behavior when user cancels language action selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\nGAC_LANGUAGE='Spanish'\nGAC_TRANSLATE_PREFIXES='false'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider, API key action, language action (cancelled)
                mselect.return_value.ask.side_effect = ["Groq", "Keep existing key", None]
                mtext.return_value.ask.side_effect = ["llama-4-scout"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='Spanish'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text
                assert "Keeping existing language" in result.output


def test_init_cli_existing_language_select_new_then_cancel(monkeypatch):
    """Test when user selects new language but then cancels the language selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GROQ_API_KEY='existing-key'\nGAC_LANGUAGE='Spanish'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
            ):
                # Provider, API key action, language action (Select new), language cancelled
                mselect.return_value.ask.side_effect = ["Groq", "Keep existing key", "Select new language", None]
                mtext.return_value.ask.side_effect = ["llama-4-scout"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='Spanish'" in env_text
                assert "Keeping existing language" in result.output


def test_init_cli_english_selection_sets_language(monkeypatch):
    """Test that selecting English explicitly sets GAC_LANGUAGE=English."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path):
            with (
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
            ):
                # Provider, language selection (English)
                mselect.return_value.ask.side_effect = ["Groq", "English"]
                mtext.return_value.ask.side_effect = ["llama-4-scout"]
                mpass.return_value.ask.side_effect = ["api-key"]

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text
