"""Tests for editor_cli module."""

import os
from unittest.mock import patch

from click.testing import CliRunner

from gac.editor_cli import configure_editor_init_workflow, editor


class TestEditorSelectionInPlace:
    """Test selecting 'In-place TUI (default)'."""

    def test_in_place_tui_unsets_env_key(self, clean_env_state, tmp_path):
        """Choosing 'In-place TUI' unsets GAC_EDITOR and clears os.environ."""
        fake_env = tmp_path / ".gac.env"
        fake_env.write_text("GAC_EDITOR=vim\n")

        os.environ["GAC_EDITOR"] = "vim"

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "In-place TUI (default)"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert result.exit_code == 0
                assert "In-place TUI" in result.output
                assert "unset" in result.output.lower()
                content = fake_env.read_text()
                assert "GAC_EDITOR" not in content

    def test_in_place_tui_no_existing_key(self, clean_env_state, tmp_path):
        """Choosing 'In-place TUI' when no GAC_EDITOR is set still works."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "In-place TUI (default)"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert result.exit_code == 0
                assert "In-place TUI" in result.output
                assert "unset" in result.output.lower()


class TestEditorSelectionVSCode:
    """Test selecting 'VS Code'."""

    def test_vscode_sets_env_key(self, clean_env_state, tmp_path):
        """Choosing 'VS Code' sets GAC_EDITOR=code --wait."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "VS Code"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert result.exit_code == 0
                assert "VS Code" in result.output
                assert "code --wait" in result.output
                content = fake_env.read_text()
                assert "GAC_EDITOR" in content
                assert "code --wait" in content


class TestEditorSelectionCustom:
    """Test the 'Custom' editor option."""

    def test_custom_editor_input(self, clean_env_state, tmp_path):
        """Choosing 'Custom' and entering 'micro' sets GAC_EDITOR=micro."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Custom"

                with patch("questionary.text") as mock_text:
                    mock_text.return_value.ask.return_value = "micro"

                    runner = CliRunner()
                    result = runner.invoke(editor)

                    assert result.exit_code == 0
                    assert "micro" in result.output
                    content = fake_env.read_text()
                    assert "GAC_EDITOR" in content
                    assert "micro" in content

    def test_custom_editor_cancelled(self, clean_env_state, tmp_path):
        """Choosing 'Custom' but entering empty string returns None / cancels."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Custom"

                with patch("questionary.text") as mock_text:
                    mock_text.return_value.ask.return_value = ""

                    runner = CliRunner()
                    result = runner.invoke(editor)

                    assert "cancelled" in result.output.lower()
                    content = fake_env.read_text()
                    assert "GAC_EDITOR" not in content

    def test_custom_editor_none_return(self, clean_env_state, tmp_path):
        """Choosing 'Custom' but questionary.text returns None cancels."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Custom"

                with patch("questionary.text") as mock_text:
                    mock_text.return_value.ask.return_value = None

                    runner = CliRunner()
                    result = runner.invoke(editor)

                    assert "cancelled" in result.output.lower()
                    content = fake_env.read_text()
                    assert "GAC_EDITOR" not in content


class TestEditorEnvFileCreation:
    """Test env file creation when missing."""

    def test_env_file_created_if_missing(self, clean_env_state, tmp_path):
        """If ~/.gac.env doesn't exist, it's created."""
        fake_env = tmp_path / ".gac.env"

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Nano"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Created" in result.output
                assert fake_env.exists()
                content = fake_env.read_text()
                assert "GAC_EDITOR" in content
                assert "nano" in content


class TestEditorCancellation:
    """Test cancellation scenarios."""

    def test_select_cancelled(self, clean_env_state, tmp_path):
        """Pressing Ctrl+C / cancelling the questionary prompt exits gracefully."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = None

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "cancelled" in result.output.lower()
                content = fake_env.read_text()
                assert "GAC_EDITOR" not in content


class TestEditorInitWorkflow:
    """Test configure_editor_init_workflow for init command."""

    def test_init_workflow_no_existing_file(self, clean_env_state, tmp_path):
        """Init workflow creates file and proceeds to selection when no file exists."""
        fake_env = tmp_path / ".gac.env"

        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "Vim"

            result = configure_editor_init_workflow(fake_env)

            assert result is True
            content = fake_env.read_text()
            assert "GAC_EDITOR" in content
            assert "vim" in content

    def test_init_workflow_with_existing_editor_kept(self, clean_env_state, tmp_path):
        """Init workflow preserves existing editor when user chooses to keep it."""
        fake_env = tmp_path / ".gac.env"
        fake_env.write_text("GAC_EDITOR=nvim\n")

        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "Keep existing editor (nvim)"

            result = configure_editor_init_workflow(fake_env)

            assert result is True
            content = fake_env.read_text()
            assert "GAC_EDITOR" in content
            assert "nvim" in content

    def test_init_workflow_with_existing_editor_cancelled(self, clean_env_state, tmp_path):
        """Init workflow returns True when user cancels the 'keep or replace' prompt."""
        fake_env = tmp_path / ".gac.env"
        fake_env.write_text("GAC_EDITOR=nvim\n")

        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = None

            result = configure_editor_init_workflow(fake_env)

            # Should return True to continue with init
            assert result is True
            # File unchanged
            content = fake_env.read_text()
            assert "GAC_EDITOR" in content
            assert "nvim" in content

    def test_init_workflow_with_existing_editor_replaced(self, clean_env_state, tmp_path):
        """Init workflow replaces editor when user picks a new one."""
        fake_env = tmp_path / ".gac.env"
        fake_env.write_text("GAC_EDITOR=vim\n")

        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.side_effect = [
                "Select new editor",
                "VS Code",
            ]

            result = configure_editor_init_workflow(fake_env)

            assert result is True
            content = fake_env.read_text()
            assert "code --wait" in content

    def test_init_workflow_no_existing_editor(self, clean_env_state, tmp_path):
        """Init workflow proceeds to selection when file exists but no GAC_EDITOR."""
        fake_env = tmp_path / ".gac.env"
        fake_env.write_text("GAC_LANGUAGE=Spanish\n")

        with patch("questionary.select") as mock_select:
            mock_select.return_value.ask.return_value = "Emacs"

            result = configure_editor_init_workflow(fake_env)

            assert result is True
            content = fake_env.read_text()
            assert "GAC_EDITOR" in content
            assert "emacs" in content

    def test_init_workflow_error_handling(self, clean_env_state, tmp_path):
        """Init workflow returns False on unexpected errors."""
        fake_env = tmp_path / ".gac.env"

        with patch("questionary.select", side_effect=RuntimeError("boom")):
            result = configure_editor_init_workflow(fake_env)
            assert result is False


class TestEditorOtherNamedChoices:
    """Test selecting other named editor choices."""

    def test_cursor_selection(self, clean_env_state, tmp_path):
        """Choosing 'Cursor' sets GAC_EDITOR=cursor --wait."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Cursor"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Cursor" in result.output
                content = fake_env.read_text()
                assert "cursor --wait" in content

    def test_zed_selection(self, clean_env_state, tmp_path):
        """Choosing 'Zed' sets GAC_EDITOR=zed --wait."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Zed"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Zed" in result.output
                content = fake_env.read_text()
                assert "zed --wait" in content

    def test_sublime_selection(self, clean_env_state, tmp_path):
        """Choosing 'Sublime Text' sets GAC_EDITOR=subl -w."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Sublime Text"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Sublime Text" in result.output
                content = fake_env.read_text()
                assert "subl -w" in content

    def test_neovim_selection(self, clean_env_state, tmp_path):
        """Choosing 'Neovim' sets GAC_EDITOR=nvim."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Neovim"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Neovim" in result.output
                content = fake_env.read_text()
                assert "nvim" in content

    def test_emacs_selection(self, clean_env_state, tmp_path):
        """Choosing 'Emacs' sets GAC_EDITOR=emacs."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Emacs"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Emacs" in result.output
                content = fake_env.read_text()
                assert "emacs" in content

    def test_vim_selection(self, clean_env_state, tmp_path):
        """Choosing 'Vim' sets GAC_EDITOR=vim."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Vim"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Vim" in result.output
                content = fake_env.read_text()
                assert "vim" in content

    def test_nano_selection(self, clean_env_state, tmp_path):
        """Choosing 'Nano' sets GAC_EDITOR=nano."""
        fake_env = tmp_path / ".gac.env"
        fake_env.touch()

        with patch("gac.editor_cli.GAC_ENV_PATH", fake_env):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "Nano"

                runner = CliRunner()
                result = runner.invoke(editor)

                assert "Nano" in result.output
                content = fake_env.read_text()
                assert "nano" in content
