from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gac.prompt_cli import (
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
