"""Tests to close coverage gaps in language_cli.py.

Targeting uncovered lines:
- Lines 28-80: configure_language_init_workflow full flow
- Line 245: is_rtl_text with non-ARABIC/HEBREW RTL script characters
- Line 314->316: show_rtl_warning with env_path=None
- Line 362: language command with custom RTL language (previously confirmed)
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gac.language_cli import (
    configure_language_init_workflow,
    is_rtl_text,
    language,
    show_rtl_warning,
)

# ── Lines 28-80: configure_language_init_workflow ────────────────────


class TestConfigureLanguageInitWorkflow:
    """Test configure_language_init_workflow function."""

    def test_existing_language_clears_gac_env_keys(self):
        """When file exists, existing GAC_ env vars should be cleared before loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_LANGUAGE=English\n")
            with (
                patch("questionary.select") as mock_select,
                patch.dict(os.environ, {"GAC_SOME_KEY": "old_value", "GAC_LANGUAGE": "stale"}, clear=False),
            ):
                mock_select.return_value.ask.return_value = "Keep existing language (English)"
                result = configure_language_init_workflow(env_path)
                assert result is True
                # The old GAC_SOME_KEY should have been cleared
                assert "GAC_SOME_KEY" not in os.environ

    def test_no_env_file_creates_and_selects(self):
        """When no env file exists, should run language selection and return True on success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            with (
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_flow.return_value = "Spanish"
                result = configure_language_init_workflow(env_path)
                assert result is True
                mock_flow.assert_called_once_with(env_path)

    def test_no_env_file_returns_false_on_cancel(self):
        """When no env file and user cancels, should return False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            with (
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_flow.return_value = None
                result = configure_language_init_workflow(env_path)
                assert result is False

    def test_existing_language_keep(self):
        """When existing language found and user keeps it, should return True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_LANGUAGE=English\n")
            with (
                patch("questionary.select") as mock_select,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_select.return_value.ask.return_value = "Keep existing language (English)"
                result = configure_language_init_workflow(env_path)
                assert result is True

    def test_existing_language_cancel_action(self):
        """When user cancels the preserve action, should return True (continue init)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_LANGUAGE=English\n")
            with (
                patch("questionary.select") as mock_select,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_select.return_value.ask.return_value = None  # User cancelled
                result = configure_language_init_workflow(env_path)
                assert result is True

    def test_existing_language_select_new(self):
        """When user selects new language, should run selection flow and return True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_LANGUAGE=English\n")
            with (
                patch("questionary.select") as mock_select,
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_select.return_value.ask.return_value = "Select new language"
                mock_flow.return_value = "Spanish"
                result = configure_language_init_workflow(env_path)
                assert result is True
                mock_flow.assert_called_once()

    def test_existing_language_select_new_cancelled(self):
        """When user selects new but cancels in flow, should return True (continue init)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_LANGUAGE=English\n")
            with (
                patch("questionary.select") as mock_select,
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_select.return_value.ask.return_value = "Select new language"
                mock_flow.return_value = None
                result = configure_language_init_workflow(env_path)
                assert result is True

    def test_no_existing_language_in_file(self):
        """When file exists but has no GAC_LANGUAGE, should run selection flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            env_path.write_text("GAC_TRANSLATE_PREFIXES=false\n")
            with (
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_flow.return_value = "French"
                result = configure_language_init_workflow(env_path)
                assert result is True
                mock_flow.assert_called_once()

    def test_string_path_input(self):
        """When existing_env_path is a string, should convert to Path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path_str = str(Path(tmpdir) / ".gac.env")
            with (
                patch("gac.language_cli._run_language_selection_flow") as mock_flow,
                patch("gac.language_cli.os.environ", {}),
            ):
                mock_flow.return_value = "German"
                result = configure_language_init_workflow(env_path_str)
                assert result is True

    def test_exception_returns_false(self):
        """When an exception occurs, should return False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".gac.env"
            with patch("gac.language_cli._run_language_selection_flow", side_effect=RuntimeError("boom")):
                result = configure_language_init_workflow(env_path)
                assert result is False


# ── Line 245: is_rtl_text with non-ARABIC/HEBREW RTL scripts ────────


class TestIsRtlTextScriptDetection:
    """Test is_rtl_text with Unicode characters from non-ARABIC/HEBREW RTL scripts."""

    def test_syriac_characters(self):
        """Syriac script characters should be detected as RTL."""
        # Syriac letter Alaph (U+0710)
        assert is_rtl_text("ܐܒܓ") is True

    def test_thaana_characters(self):
        """Thaana script characters should be detected as RTL."""
        # Thaana letter Haa (U+0780)
        assert is_rtl_text("ހށނ") is True

    def test_latin_text_not_rtl(self):
        """Latin text should not be detected as RTL."""
        assert is_rtl_text("Hello World") is False

    def test_known_rtl_language_name_case_insensitive(self):
        """Known RTL language names should be detected case-insensitively."""
        assert is_rtl_text("ARABIC") is True
        assert is_rtl_text("Hebrew") is True
        assert is_rtl_text("PERSIAN") is True


# ── Line 314->316: show_rtl_warning with env_path=None ───────────────


class TestShowRtlWarningDefaultPath:
    """Test show_rtl_warning when env_path is None (uses GAC_ENV_PATH)."""

    def test_env_path_none_uses_default(self):
        """When env_path is None, should use GAC_ENV_PATH."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_env = Path(tmpdir) / ".gac.env"
            with (
                patch("gac.language_cli.GAC_ENV_PATH", fake_env),
                patch("questionary.confirm") as mock_confirm,
            ):
                mock_confirm.return_value.ask.return_value = True
                result = show_rtl_warning("Arabic", env_path=None)
                assert result is True
                # The file should have been written with GAC_RTL_CONFIRMED=true
                content = fake_env.read_text()
                assert "GAC_RTL_CONFIRMED" in content

    def test_user_cancels_rtl_warning(self):
        """When user declines RTL warning, should return False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_env = Path(tmpdir) / ".gac.env"
            with (
                patch("gac.language_cli.GAC_ENV_PATH", fake_env),
                patch("questionary.confirm") as mock_confirm,
            ):
                mock_confirm.return_value.ask.return_value = False
                result = show_rtl_warning("Arabic", env_path=fake_env)
                assert result is False


# ── Line 362: language command with custom RTL language ──────────────


class TestLanguageCommandCustomRtl:
    """Test language command with custom RTL language that was previously confirmed."""

    def test_custom_rtl_language_previously_confirmed(self, clean_env_state):
        """Custom RTL language with RTL warning previously confirmed should show info message."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = Path(tmpdir) / ".gac.env"
            # Pre-configure RTL confirmed
            fake_path.write_text("GAC_RTL_CONFIRMED=true\n")
            with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
                with patch("questionary.select") as mock_select:
                    # 1st: select "Custom", 2nd: prefix translation choice
                    mock_select.return_value.ask.side_effect = [
                        "Custom",
                        "Keep prefixes in English (feat:, fix:, etc.)",
                    ]
                    with patch("questionary.text") as mock_text:
                        mock_text.return_value.ask.return_value = "العربية"
                        result = runner.invoke(language)
                        assert result.exit_code == 0
                        # Must show the specific previously-confirmed RTL info message
                        assert "RTL warning previously confirmed" in result.output
