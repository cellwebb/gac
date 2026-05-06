from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gac.prompt_cli import (
    _edit_text_interactive,
    get_active_custom_prompt,
    prompt,
)


@pytest.fixture
def mock_paths(tmp_path, monkeypatch):
    """Override config directory and custom prompt file paths."""
    config_dir = tmp_path / "config" / "gac"
    custom_prompt = config_dir / "custom_system_prompt.txt"

    monkeypatch.setattr("gac.prompt_cli.GAC_CONFIG_DIR", config_dir)
    monkeypatch.setattr("gac.prompt_cli.CUSTOM_PROMPT_FILE", custom_prompt)

    return {"config_dir": config_dir, "custom_prompt": custom_prompt}


@pytest.fixture
def runner():
    return CliRunner()


class TestPromptShow:
    def test_prompt_show_no_custom_prompt(self, runner, mock_paths, monkeypatch):
        """No env var, no file, shows default system prompt."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        result = runner.invoke(prompt, ["show"])
        assert result.exit_code == 0
        assert "No custom prompt configured" in result.output
        assert "Default System Prompt" in result.output
        # Should contain actual default prompt content
        assert "git commit message" in result.output.lower()

    def test_prompt_show_from_env_var(self, runner, tmp_path, monkeypatch):
        """GAC_SYSTEM_PROMPT_PATH set, shows content with env var source."""
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("Env var custom prompt content", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        result = runner.invoke(prompt, ["show"])
        assert result.exit_code == 0
        assert "Env var custom prompt content" in result.output
        # Rich may wrap long paths, so check for key parts
        output_normalized = result.output.replace("\n", "")
        assert "GAC_SYSTEM_PROMPT_PATH=" in output_normalized

    def test_prompt_show_from_stored_file(self, runner, mock_paths, monkeypatch):
        """File exists at CUSTOM_PROMPT_FILE, shows content with file path source."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Stored custom prompt content", encoding="utf-8")

        result = runner.invoke(prompt, ["show"])
        assert result.exit_code == 0
        assert "Stored custom prompt content" in result.output
        # Panel shows title with source info
        assert "Custom System Prompt" in result.output

    def test_prompt_show_env_var_precedence(self, runner, mock_paths, tmp_path, monkeypatch):
        """Both env var and stored file exist, env var wins."""
        # Create stored file
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Stored prompt", encoding="utf-8")

        # Create env var file
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("Env var prompt", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        result = runner.invoke(prompt, ["show"])
        assert result.exit_code == 0
        assert "Env var prompt" in result.output
        assert "Stored prompt" not in result.output
        # Rich may wrap long paths, so check for key parts
        output_normalized = result.output.replace("\n", "")
        assert "GAC_SYSTEM_PROMPT_PATH=" in output_normalized


class TestPromptSetFile:
    def test_prompt_set_file_success(self, runner, mock_paths, tmp_path, monkeypatch):
        """Copies file content to CUSTOM_PROMPT_FILE."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        source_file = tmp_path / "source.txt"
        source_file.write_text("Test prompt content", encoding="utf-8")

        result = runner.invoke(prompt, ["set", "--file", str(source_file)])
        assert result.exit_code == 0
        assert mock_paths["custom_prompt"].exists()
        assert mock_paths["custom_prompt"].read_text(encoding="utf-8") == "Test prompt content"
        assert "Custom prompt copied" in result.output

    def test_prompt_set_file_not_found(self, runner, mock_paths, monkeypatch):
        """Error when file doesn't exist."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        nonexistent = "/path/that/does/not/exist.txt"
        result = runner.invoke(prompt, ["set", "--file", nonexistent])
        assert result.exit_code != 0
        assert "does not exist" in result.output or "not found" in result.output.lower()

    def test_prompt_set_file_creates_directory(self, runner, mock_paths, tmp_path, monkeypatch):
        """Creates ~/.config/gac if needed."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        source_file = tmp_path / "source.txt"
        source_file.write_text("Test content", encoding="utf-8")

        # Ensure config_dir doesn't exist
        assert not mock_paths["config_dir"].exists()

        result = runner.invoke(prompt, ["set", "--file", str(source_file)])
        assert result.exit_code == 0
        assert mock_paths["config_dir"].exists()
        assert mock_paths["custom_prompt"].exists()


class TestPromptSetEdit:
    def test_prompt_set_edit_new(self, runner, mock_paths, monkeypatch):
        """Mock _edit_text_interactive(), verify content saved (no existing prompt)."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)

        with patch("gac.prompt_cli._edit_text_interactive") as mock_edit:
            mock_edit.return_value = "New prompt from editor"
            result = runner.invoke(prompt, ["set", "--edit"])

        assert result.exit_code == 0
        assert mock_paths["custom_prompt"].exists()
        assert mock_paths["custom_prompt"].read_text(encoding="utf-8") == "New prompt from editor"
        assert "Custom prompt saved" in result.output
        # Verify editor was called with empty string
        mock_edit.assert_called_once_with("")

    def test_prompt_set_edit_existing(self, runner, mock_paths, monkeypatch):
        """Mock _edit_text_interactive(), verify pre-populated with existing content."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Existing prompt", encoding="utf-8")

        with patch("gac.prompt_cli._edit_text_interactive") as mock_edit:
            mock_edit.return_value = "Updated prompt from editor"
            result = runner.invoke(prompt, ["set", "--edit"])

        assert result.exit_code == 0
        assert mock_paths["custom_prompt"].read_text(encoding="utf-8") == "Updated prompt from editor"
        # Verify editor was called with existing content
        mock_edit.assert_called_once_with("Existing prompt")

    def test_prompt_set_edit_abort(self, runner, mock_paths, monkeypatch):
        """Mock _edit_text_interactive() returning None, verify no changes."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Original content", encoding="utf-8")

        with patch("gac.prompt_cli._edit_text_interactive") as mock_edit:
            mock_edit.return_value = None  # User cancelled
            result = runner.invoke(prompt, ["set", "--edit"])

        assert result.exit_code == 0
        # File should remain unchanged
        assert mock_paths["custom_prompt"].read_text(encoding="utf-8") == "Original content"
        assert "cancelled" in result.output.lower()

    def test_prompt_set_requires_option(self, runner, mock_paths, monkeypatch):
        """Error if neither --edit nor --file provided."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        result = runner.invoke(prompt, ["set"])
        assert result.exit_code != 0
        assert "--edit" in result.output or "--file" in result.output

    def test_prompt_set_edit_env_var_file(self, runner, mock_paths, tmp_path, monkeypatch):
        """When GAC_SYSTEM_PROMPT_PATH is set, --edit edits that file."""
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("Original env content", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        with patch("gac.prompt_cli._edit_text_interactive") as mock_edit:
            mock_edit.return_value = "Updated env content"
            result = runner.invoke(prompt, ["set", "--edit"])

        assert result.exit_code == 0
        # Editor should be called with env file content
        mock_edit.assert_called_once_with("Original env content")
        # Env file should be updated, not the default stored file
        assert env_prompt_file.read_text(encoding="utf-8") == "Updated env content"
        assert not mock_paths["custom_prompt"].exists()


class TestPromptClear:
    def test_prompt_clear_existing(self, runner, mock_paths, monkeypatch):
        """Deletes file, shows confirmation."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Prompt to delete", encoding="utf-8")

        result = runner.invoke(prompt, ["clear"])
        assert result.exit_code == 0
        assert not mock_paths["custom_prompt"].exists()
        assert "deleted" in result.output.lower()

    def test_prompt_clear_nonexistent(self, runner, mock_paths, monkeypatch):
        """No error when file doesn't exist (idempotent)."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        assert not mock_paths["custom_prompt"].exists()

        result = runner.invoke(prompt, ["clear"])
        assert result.exit_code == 0
        # Should succeed silently or with friendly message
        assert "error" not in result.output.lower()


class TestGetActiveCustomPrompt:
    def test_get_active_custom_prompt_none(self, mock_paths, monkeypatch):
        """Returns (None, None) when no custom prompt."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        content, source = get_active_custom_prompt()
        assert content is None
        assert source is None

    def test_get_active_custom_prompt_env_var(self, tmp_path, monkeypatch):
        """Returns content and source from env var."""
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("Env var content", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        content, source = get_active_custom_prompt()
        assert content == "Env var content"
        assert source == f"GAC_SYSTEM_PROMPT_PATH={env_prompt_file}"

    def test_get_active_custom_prompt_stored_file(self, mock_paths, monkeypatch):
        """Returns content and source from stored file."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Stored content", encoding="utf-8")

        content, source = get_active_custom_prompt()
        assert content == "Stored content"
        assert source == str(mock_paths["custom_prompt"])

    def test_get_active_custom_prompt_env_var_precedence(self, mock_paths, tmp_path, monkeypatch):
        """Env var takes precedence over stored file."""
        # Create stored file
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("Stored content", encoding="utf-8")

        # Create env var file
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("Env var content", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        content, source = get_active_custom_prompt()
        assert content == "Env var content"
        assert source == f"GAC_SYSTEM_PROMPT_PATH={env_prompt_file}"

    def test_get_active_custom_prompt_env_var_missing_file(self, mock_paths, monkeypatch):
        """Returns (None, None) when env var points to nonexistent file."""
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", "/nonexistent/file.txt")

        content, source = get_active_custom_prompt()
        # Should gracefully handle missing file
        assert content is None
        assert source is None

    def test_get_active_custom_prompt_env_var_oserror(self, tmp_path, monkeypatch):
        """Handles OSError when reading env var file."""
        env_prompt_file = tmp_path / "env_prompt.txt"
        env_prompt_file.write_text("content", encoding="utf-8")
        monkeypatch.setenv("GAC_SYSTEM_PROMPT_PATH", str(env_prompt_file))

        with patch("pathlib.Path.read_text", side_effect=OSError("Permission denied")):
            content, source = get_active_custom_prompt()
        # Should gracefully handle OSError
        assert content is None
        assert source is None

    def test_get_active_custom_prompt_stored_file_oserror(self, mock_paths, monkeypatch):
        """Handles OSError when reading stored file."""
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        mock_paths["config_dir"].mkdir(parents=True, exist_ok=True)
        mock_paths["custom_prompt"].write_text("content", encoding="utf-8")

        with patch("pathlib.Path.read_text", side_effect=OSError("Permission denied")):
            content, source = get_active_custom_prompt()
        # Should gracefully handle OSError
        assert content is None
        assert source is None


class TestEditTextInteractive:
    @pytest.fixture(autouse=True)
    def _patch_prompt_toolkit(self):
        self.mock_buffer = MagicMock()
        self.mock_document = MagicMock()
        self.mock_editing_mode = MagicMock()
        self.mock_key_bindings_cls = MagicMock()
        self.mock_key_press_event = MagicMock()
        self.mock_hsplit = MagicMock()
        self.mock_layout_cls = MagicMock()
        self.mock_window = MagicMock()
        self.mock_buffer_control = MagicMock()
        self.mock_formatted_text_control = MagicMock()
        self.mock_scrollbar_margin = MagicMock()
        self.mock_style = MagicMock()
        self.mock_app_cls = MagicMock()
        self.mock_app_instance = MagicMock()
        self.mock_app_cls.return_value = self.mock_app_instance

        self.patches = [
            patch("prompt_toolkit.Application", self.mock_app_cls),
            patch("prompt_toolkit.buffer.Buffer", self.mock_buffer),
            patch("prompt_toolkit.document.Document", self.mock_document),
            patch("prompt_toolkit.enums.EditingMode", self.mock_editing_mode),
            patch("prompt_toolkit.key_binding.KeyBindings", self.mock_key_bindings_cls),
            patch("prompt_toolkit.key_binding.KeyPressEvent", self.mock_key_press_event),
            patch("prompt_toolkit.layout.HSplit", self.mock_hsplit),
            patch("prompt_toolkit.layout.Layout", self.mock_layout_cls),
            patch("prompt_toolkit.layout.Window", self.mock_window),
            patch("prompt_toolkit.layout.controls.BufferControl", self.mock_buffer_control),
            patch("prompt_toolkit.layout.controls.FormattedTextControl", self.mock_formatted_text_control),
            patch("prompt_toolkit.layout.margins.ScrollbarMargin", self.mock_scrollbar_margin),
            patch("prompt_toolkit.styles.Style", self.mock_style),
        ]
        for p in self.patches:
            p.start()
        yield
        for p in self.patches:
            p.stop()

    def test_returns_none_when_neither_submitted_nor_cancelled(self):
        self.mock_app_instance.run.return_value = None
        result = _edit_text_interactive("test text")
        assert result is None

    def test_returns_none_on_eof_error(self):
        self.mock_app_instance.run.side_effect = EOFError()
        result = _edit_text_interactive("test text")
        assert result is None

    def test_returns_none_on_keyboard_interrupt(self):
        self.mock_app_instance.run.side_effect = KeyboardInterrupt()
        result = _edit_text_interactive("test text")
        assert result is None

    def test_returns_none_on_generic_exception(self):
        self.mock_app_instance.run.side_effect = RuntimeError("something broke")
        result = _edit_text_interactive("test text")
        assert result is None

    def test_cancelled_returns_none(self):
        kb_instance = MagicMock()
        handlers = {}

        def capture_add(*keys):
            def decorator(func):
                handlers[keys] = func
                return func

            return decorator

        kb_instance.add = capture_add
        self.mock_key_bindings_cls.return_value = kb_instance

        def simulate_cancel():
            if ("c-c",) in handlers:
                mock_event = MagicMock()
                handlers[("c-c",)](mock_event)

        self.mock_app_instance.run.side_effect = simulate_cancel
        result = _edit_text_interactive("test text")
        assert result is None

    def test_submitted_returns_stripped_text(self):
        kb_instance = MagicMock()
        handlers = {}

        def capture_add(*keys):
            def decorator(func):
                handlers[keys] = func
                return func

            return decorator

        kb_instance.add = capture_add
        self.mock_key_bindings_cls.return_value = kb_instance

        mock_buffer_instance = MagicMock()
        mock_buffer_instance.text = "  edited text  "
        self.mock_buffer.return_value = mock_buffer_instance

        def simulate_submit():
            if ("c-s",) in handlers:
                mock_event = MagicMock()
                handlers[("c-s",)](mock_event)

        self.mock_app_instance.run.side_effect = simulate_submit
        result = _edit_text_interactive("initial text")
        assert result == "edited text"

    def test_escape_enter_submits(self):
        kb_instance = MagicMock()
        handlers = {}

        def capture_add(*keys):
            def decorator(func):
                handlers[keys] = func
                return func

            return decorator

        kb_instance.add = capture_add
        self.mock_key_bindings_cls.return_value = kb_instance

        mock_buffer_instance = MagicMock()
        mock_buffer_instance.text = "submitted via escape"
        self.mock_buffer.return_value = mock_buffer_instance

        def simulate_escape_enter():
            if ("escape", "enter") in handlers:
                mock_event = MagicMock()
                handlers[("escape", "enter")](mock_event)

        self.mock_app_instance.run.side_effect = simulate_escape_enter
        result = _edit_text_interactive("initial text")
        assert result == "submitted via escape"


class TestPromptSetEdgeCases:
    def test_prompt_set_both_edit_and_file(self, runner, mock_paths, tmp_path, monkeypatch):
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        source_file = tmp_path / "source.txt"
        source_file.write_text("content", encoding="utf-8")

        result = runner.invoke(prompt, ["set", "--edit", "--file", str(source_file)])
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()

    def test_prompt_set_edit_empty_result(self, runner, mock_paths, monkeypatch):
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)

        with patch("gac.prompt_cli._edit_text_interactive") as mock_edit:
            mock_edit.return_value = ""
            result = runner.invoke(prompt, ["set", "--edit"])

        assert result.exit_code == 0
        assert "empty prompt not saved" in result.output.lower()
        assert not mock_paths["custom_prompt"].exists()

    def test_prompt_set_file_oserror(self, runner, mock_paths, tmp_path, monkeypatch):
        monkeypatch.delenv("GAC_SYSTEM_PROMPT_PATH", raising=False)
        source_file = tmp_path / "source.txt"
        source_file.write_text("content", encoding="utf-8")

        with patch("pathlib.Path.read_text", side_effect=OSError("Permission denied")):
            result = runner.invoke(prompt, ["set", "--file", str(source_file)])

        assert result.exit_code != 0
        assert "error reading file" in result.output.lower()
