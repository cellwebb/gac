"""Tests for init_cli module focused on init workflow integration."""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

from gac.init_cli import _configure_language, _configure_stats, _load_existing_env, _prompt_required_text, init


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


def test_init_cli_prompt_required_text_valid_input():
    """Test _prompt_required_text with valid input."""
    with mock.patch("questionary.text") as mtext:
        mtext.return_value.ask.side_effect = ["valid input"]
        result = _prompt_required_text("Enter something:")
        assert result == "valid input"


def test_init_cli_prompt_required_text_empty_then_valid():
    """Test _prompt_required_text with empty input then valid input."""
    with mock.patch("questionary.text") as mtext, mock.patch("click.echo") as mecho:
        mtext.return_value.ask.side_effect = ["", "  ", "valid input"]
        result = _prompt_required_text("Enter something:")
        assert result == "valid input"
        # Should have echoed error message twice for empty inputs
        assert mecho.call_count == 2


def test_init_cli_prompt_required_text_cancel():
    """Test _prompt_required_text with cancellation."""
    with mock.patch("questionary.text") as mtext:
        mtext.return_value.ask.side_effect = [None]  # User cancels
        result = _prompt_required_text("Enter something:")
        assert result is None


def test_init_cli_load_existing_env_new_file(tmp_path):
    """Test _load_existing_env creates new file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path), mock.patch("click.echo") as mecho:
            result = _load_existing_env()
            assert result == {}
            assert env_path.exists()
            assert "Created $HOME/.gac.env" in str(mecho.call_args)


def test_init_cli_load_existing_env_existing_file(tmp_path):
    """Test _load_existing_env loads existing file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("EXISTING_KEY='existing_value'\nANOTHER_KEY='another_value'\n")
        with mock.patch("gac.init_cli.GAC_ENV_PATH", env_path), mock.patch("click.echo") as mecho:
            result = _load_existing_env()
            assert result == {"EXISTING_KEY": "existing_value", "ANOTHER_KEY": "another_value"}
            assert "already exists" in str(mecho.call_args)


def test_init_cli_configure_language_success(tmp_path):
    """Test _configure_language successful configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        with (
            mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
            mock.patch("gac.init_cli.configure_language_init_workflow") as mconfig,
            mock.patch("click.echo") as mecho,
        ):
            mconfig.return_value = True
            _configure_language({})
            mconfig.assert_called_once_with(env_path)
            # Check that the success message was printed
            echo_calls = [str(call) for call in mecho.call_args_list]
            assert any("Language configuration completed" in str(call) for call in echo_calls)


def test_init_cli_configure_language_failure(tmp_path):
    """Test _configure_language failed configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        with (
            mock.patch("gac.init_cli.GAC_ENV_PATH", env_path),
            mock.patch("gac.init_cli.configure_language_init_workflow") as mconfig,
            mock.patch("click.echo") as mecho,
        ):
            mconfig.return_value = False
            _configure_language({})
            mconfig.assert_called_once_with(env_path)
            # Check that the failure message was printed
            echo_calls = [str(call) for call in mecho.call_args_list]
            assert any("Language configuration cancelled or failed" in str(call) for call in echo_calls)


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
                mock.patch("questionary.confirm") as mconfirm,
            ):
                # Complete workflow: provider selection + language selection (no existing config)
                mselect.return_value.ask.side_effect = ["OpenAI", "English"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]
                mconfirm.return_value.ask.side_effect = [True]  # enable stats

                result = runner.invoke(init)
                assert result.exit_code == 0
                env_text = env_path.read_text()
                assert "GAC_MODEL='openai:gpt-4'" in env_text
                assert "OPENAI_API_KEY='openai-key'" in env_text
                assert "GAC_LANGUAGE='English'" in env_text
                assert "GAC_TRANSLATE_PREFIXES='false'" in env_text


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
                mock.patch("questionary.confirm") as mconfirm,
            ):
                # Simple workflow: provider selection + English language
                mselect.return_value.ask.side_effect = ["OpenAI", "English"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]
                mconfirm.return_value.ask.side_effect = [True]  # enable stats

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
                mock.patch("questionary.confirm") as mconfirm,
            ):
                # Provider, API key action, language action (Keep existing)
                mselect.return_value.ask.side_effect = ["OpenAI", "Keep existing key", "Keep existing language"]
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mconfirm.return_value.ask.side_effect = [True]  # enable stats

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
                mock.patch("questionary.confirm") as mconfirm,
            ):
                mselect.return_value.ask.side_effect = ["OpenAI", "Keep existing key", "English"]
                mtext.return_value.ask.side_effect = ["gpt-5"]
                mconfirm.return_value.ask.side_effect = [True]  # enable stats

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


def test_configure_stats_enable_from_default():
    """Test that confirming with no prior setting leaves env file unchanged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        with _patch_env_paths(env_path):
            with mock.patch("questionary.confirm") as mconfirm:
                mconfirm.return_value.ask.side_effect = [True]
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                # questionary.confirm called with default=True
                args, kwargs = mconfirm.call_args
                assert kwargs.get("default") is True
                # No GAC_DISABLE_STATS written
                assert "GAC_DISABLE_STATS" not in env_path.read_text()
                assert "GAC_DISABLE_STATS" not in existing_env


def test_configure_stats_disable_from_default():
    """Test that declining writes GAC_DISABLE_STATS=true to the env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        stats_file = Path(tmpdir) / ".gac_stats.json"  # non-existent
        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.confirm") as mconfirm,
            ):
                mconfirm.return_value.ask.side_effect = [False]
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                env_text = env_path.read_text()
                assert "GAC_DISABLE_STATS" in env_text
                assert existing_env.get("GAC_DISABLE_STATS") == "true"


def test_configure_stats_re_enable_removes_key():
    """Test that confirming when previously disabled removes the key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GAC_DISABLE_STATS='true'\n")
        with _patch_env_paths(env_path):
            with mock.patch("questionary.confirm") as mconfirm:
                mconfirm.return_value.ask.side_effect = [True]
                existing_env = {"GAC_DISABLE_STATS": "true"}
                _configure_stats(existing_env, env_path)
                # default should be False (currently disabled)
                args, kwargs = mconfirm.call_args
                assert kwargs.get("default") is False
                env_text = env_path.read_text()
                assert "GAC_DISABLE_STATS" not in env_text
                assert "GAC_DISABLE_STATS" not in existing_env


def test_configure_stats_keep_disabled():
    """Test that declining when previously disabled re-asserts the key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.write_text("GAC_DISABLE_STATS='true'\n")
        stats_file = Path(tmpdir) / ".gac_stats.json"  # non-existent
        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.confirm") as mconfirm,
            ):
                mconfirm.return_value.ask.side_effect = [False]
                existing_env = {"GAC_DISABLE_STATS": "true"}
                _configure_stats(existing_env, env_path)
                env_text = env_path.read_text()
                assert "GAC_DISABLE_STATS" in env_text
                assert existing_env.get("GAC_DISABLE_STATS") == "true"


def test_configure_stats_user_cancels():
    """Test that cancelling (Ctrl-C / None) leaves env unchanged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        before = env_path.read_text()
        with _patch_env_paths(env_path):
            with mock.patch("questionary.confirm") as mconfirm:
                mconfirm.return_value.ask.side_effect = [None]
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                assert env_path.read_text() == before
                assert "GAC_DISABLE_STATS" not in existing_env


def test_configure_stats_disable_offers_to_delete_existing_history():
    """When disabling, offer to delete existing stats file. User accepts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        stats_file = Path(tmpdir) / ".gac_stats.json"
        stats_file.write_text("{}")

        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.confirm") as mconfirm,
            ):
                # 1) disable stats, 2) confirm delete
                mconfirm.return_value.ask.side_effect = [False, True]
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                assert not stats_file.exists()
                assert existing_env.get("GAC_DISABLE_STATS") == "true"


def test_configure_stats_disable_keeps_existing_history_when_user_declines():
    """When disabling, user can keep the existing stats file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        stats_file = Path(tmpdir) / ".gac_stats.json"
        stats_file.write_text('{"total_gacs": 5}')

        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.confirm") as mconfirm,
            ):
                # 1) disable stats, 2) keep file
                mconfirm.return_value.ask.side_effect = [False, False]
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                assert stats_file.exists()
                assert stats_file.read_text() == '{"total_gacs": 5}'
                assert existing_env.get("GAC_DISABLE_STATS") == "true"


def test_configure_stats_disable_no_prompt_when_no_history():
    """When disabling and no stats file exists, the delete prompt is skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".gac.env"
        env_path.touch()
        stats_file = Path(tmpdir) / ".gac_stats.json"  # never created

        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.confirm") as mconfirm,
            ):
                mconfirm.return_value.ask.side_effect = [False]  # only the enable prompt
                existing_env: dict[str, str] = {}
                _configure_stats(existing_env, env_path)
                # confirm called exactly once (no delete prompt)
                assert mconfirm.call_count == 1
                assert existing_env.get("GAC_DISABLE_STATS") == "true"


def test_init_cli_language_action_cancelled(monkeypatch):
    """Test init workflow when user cancels language selection."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = _setup_env_file(tmpdir)
        stats_file = Path(tmpdir) / ".gac_stats.json"  # non-existent
        with _patch_env_paths(env_path):
            with (
                mock.patch("gac.stats.STATS_FILE", stats_file),
                mock.patch("questionary.select") as mselect,
                mock.patch("questionary.text") as mtext,
                mock.patch("questionary.password") as mpass,
                mock.patch("questionary.confirm") as mconfirm,
            ):
                mselect.return_value.ask.side_effect = ["OpenAI", None]  # Cancels at language step
                mtext.return_value.ask.side_effect = ["gpt-4"]
                mpass.return_value.ask.side_effect = ["openai-key"]
                # Stats step still runs after language; user enables stats.
                mconfirm.return_value.ask.side_effect = [True]

                result = runner.invoke(init)
                # Should complete model config but cancel language part
                assert result.exit_code == 0
