"""Tests for language_cli module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from gac.language_cli import language


def test_language_select_predefined_with_prefix_translation(clean_env_state):
    """Test selecting a predefined language with prefix translation enabled."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Mock questionary to select Spanish and translate prefixes
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Español",  # Language selection
                    "Translate prefixes into Spanish",  # Prefix choice
                ]
                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to Español" in result.output
                assert "GAC_LANGUAGE=Spanish" in result.output
                assert "GAC_TRANSLATE_PREFIXES=true" in result.output
                assert "Prefixes will be translated" in result.output
                assert fake_path.exists()

                # Verify the file contents
                content = fake_path.read_text()
                assert "GAC_LANGUAGE=" in content and "Spanish" in content
                assert "GAC_TRANSLATE_PREFIXES=" in content and "true" in content


def test_language_select_predefined_without_prefix_translation(clean_env_state):
    """Test selecting a predefined language without prefix translation."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "日本語",  # Japanese
                    "Keep prefixes in English (feat:, fix:, etc.)",  # Keep English prefixes
                ]
                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to 日本語" in result.output
                assert "GAC_LANGUAGE=Japanese" in result.output
                assert "GAC_TRANSLATE_PREFIXES=false" in result.output
                assert "Prefixes will remain in English" in result.output
                assert fake_path.exists()

                content = fake_path.read_text()
                assert "GAC_LANGUAGE=" in content and "Japanese" in content
                assert "GAC_TRANSLATE_PREFIXES=" in content and "false" in content


def test_language_select_english_sets_explicitly(clean_env_state):
    """Test selecting English sets the language explicitly."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        # Pre-populate .gac.env with a language setting
        fake_path.write_text("GAC_LANGUAGE=Spanish\nGAC_TRANSLATE_PREFIXES=true\n")

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "English"

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to English" in result.output
                assert "GAC_LANGUAGE=English" in result.output
                assert "GAC_TRANSLATE_PREFIXES=false" in result.output

                # Verify GAC_LANGUAGE was set to English
                content = fake_path.read_text()
                assert "GAC_LANGUAGE='English'" in content
                assert "GAC_TRANSLATE_PREFIXES='false'" in content


def test_language_select_english_file_not_exists(clean_env_state):
    """Test selecting English when .gac.env doesn't exist yet."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "English"

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to English" in result.output
                assert "GAC_LANGUAGE=English" in result.output
                assert "GAC_TRANSLATE_PREFIXES=false" in result.output
                # File should be created and contain English setting
                assert fake_path.exists()
                content = fake_path.read_text()
                assert "GAC_LANGUAGE='English'" in content
                assert "GAC_TRANSLATE_PREFIXES='false'" in content


def test_language_select_custom_language(clean_env_state):
    """Test selecting a custom language."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
                mock_select.return_value.ask.side_effect = [
                    "Custom",  # Language selection
                    "Keep prefixes in English (feat:, fix:, etc.)",  # Prefix choice
                ]
                mock_text.return_value.ask.return_value = "Esperanto"

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to Esperanto" in result.output
                assert "GAC_LANGUAGE=Esperanto" in result.output
                assert fake_path.exists()

                content = fake_path.read_text()
                assert "GAC_LANGUAGE=" in content and "Esperanto" in content


def test_language_select_custom_with_whitespace(clean_env_state):
    """Test selecting a custom language with leading/trailing whitespace."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
                mock_select.return_value.ask.side_effect = [
                    "Custom",
                    "Keep prefixes in English (feat:, fix:, etc.)",
                ]
                mock_text.return_value.ask.return_value = "  Klingon  "

                result = runner.invoke(language)

                assert result.exit_code == 0
                # Should be trimmed
                assert "GAC_LANGUAGE=Klingon" in result.output


def test_language_custom_cancelled_empty_input(clean_env_state):
    """Test cancelling custom language with empty input."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
                mock_select.return_value.ask.return_value = "Custom"
                mock_text.return_value.ask.return_value = ""

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "Language selection cancelled." in result.output
                # File might be created but shouldn't have language set
                if fake_path.exists():
                    content = fake_path.read_text()
                    assert "GAC_LANGUAGE" not in content


def test_language_custom_cancelled_whitespace_only(clean_env_state):
    """Test cancelling custom language with whitespace-only input."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
                mock_select.return_value.ask.return_value = "Custom"
                mock_text.return_value.ask.return_value = "   "

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "Language selection cancelled." in result.output


def test_language_custom_cancelled_none(clean_env_state):
    """Test cancelling custom language with None (Ctrl+C)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
                mock_select.return_value.ask.return_value = "Custom"
                mock_text.return_value.ask.return_value = None

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "Language selection cancelled." in result.output


def test_language_selection_cancelled(clean_env_state):
    """Test cancelling at the language selection step."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = None  # User pressed Ctrl+C

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "Language selection cancelled." in result.output


def test_language_prefix_selection_cancelled(clean_env_state):
    """Test cancelling at the prefix translation selection step."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Français",  # Language selection
                    None,  # Cancel prefix selection
                ]

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "Language selection cancelled." in result.output
                # File might be created but language should not be saved if prefix selection was cancelled


def test_language_creates_file_if_not_exists(clean_env_state):
    """Test that .gac.env is created if it doesn't exist."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        # Ensure file doesn't exist
        assert not fake_path.exists()

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Português",
                    "Keep prefixes in English (feat:, fix:, etc.)",
                ]

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert f"Created {fake_path}" in result.output
                assert fake_path.exists()


def test_language_all_predefined_languages(clean_env_state):
    """Test that all predefined languages can be selected and stored correctly."""
    runner = CliRunner()

    test_languages = [
        ("简体中文", "Simplified Chinese"),
        ("繁體中文", "Traditional Chinese"),
        ("한국어", "Korean"),
        ("Deutsch", "German"),
        ("Русский", "Russian"),
        ("हिन्दी", "Hindi"),
    ]

    for display_name, english_name in test_languages:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = Path(tmpdir) / ".gac.env"
            with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
                with patch("questionary.select") as mock_select:
                    mock_select.return_value.ask.side_effect = [
                        display_name,
                        "Keep prefixes in English (feat:, fix:, etc.)",
                    ]

                    result = runner.invoke(language)

                    assert result.exit_code == 0
                    assert f"✓ Set language to {display_name}" in result.output
                    assert f"GAC_LANGUAGE={english_name}" in result.output

                    content = fake_path.read_text()
                    assert "GAC_LANGUAGE=" in content and english_name in content


def test_language_display_shows_instructions(clean_env_state):
    """Test that the command displays initial instructions."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = None  # Cancel immediately

                result = runner.invoke(language)

                assert "Select a language for your commit messages:" in result.output


def test_language_existing_file_is_updated(clean_env_state):
    """Test that selecting a new language updates existing .gac.env file."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        # Pre-populate with existing config
        fake_path.write_text("GAC_MODEL=anthropic:claude-3-haiku\nGAC_LANGUAGE=Spanish\n")

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Français",
                    "Translate prefixes into French",
                ]

                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to Français" in result.output

                content = fake_path.read_text()
                # Should update language but preserve other settings
                assert "GAC_MODEL=anthropic:claude-3-haiku" in content
                assert "GAC_LANGUAGE=" in content and "French" in content
                assert "Spanish" not in content
                assert "GAC_TRANSLATE_PREFIXES=" in content and "true" in content


def test_language_prefix_translation_message_shows_language_name(clean_env_state):
    """Test that prefix translation message shows the selected language name."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Italiano",
                    "Translate prefixes into Italian",
                ]

                result = runner.invoke(language)

                assert result.exit_code == 0
                # The prefix choice message should mention "Italian"
                assert (
                    "Translate prefixes into Italian" in result.output or "GAC_TRANSLATE_PREFIXES=true" in result.output
                )


def test_rtl_detection_function(clean_env_state):
    """Test the RTL text detection function."""
    from gac.language_cli import is_rtl_text

    # Test RTL languages
    assert is_rtl_text("Arabic")
    assert is_rtl_text("arabic")
    assert is_rtl_text("ar")
    assert is_rtl_text("Hebrew")
    assert is_rtl_text("hebrew")
    assert is_rtl_text("he")
    assert is_rtl_text("العربية")
    assert is_rtl_text("עברית")

    # Test non-RTL languages
    assert not is_rtl_text("Spanish")
    assert not is_rtl_text("French")
    assert not is_rtl_text("English")
    assert not is_rtl_text("日本語")
    assert not is_rtl_text("中文")


def test_language_select_rtl_predefined_arabic(clean_env_state):
    """Test selecting Arabic (RTL) shows warning and allows proceeding."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with (
                patch("gac.language_cli.show_rtl_warning") as mock_rtl_warning,
                patch("questionary.select") as mock_select,
                patch("gac.language_cli.should_show_rtl_warning", return_value=True),  # Force warning to show
            ):
                # Mock RTL warning to return True (user wants to proceed)
                mock_rtl_warning.return_value = True
                mock_select.return_value.ask.side_effect = [
                    "العربية",  # Select Arabic
                    "Keep prefixes in English (feat:, fix:, etc.)",  # Prefix choice
                ]

                result = runner.invoke(language)

                assert result.exit_code == 0
                # Check that RTL warning was called with language and path
                mock_rtl_warning.assert_called_once()
                args, kwargs = mock_rtl_warning.call_args
                assert args[0] == "Arabic"
                assert isinstance(args[1], Path)
                assert "✓ Set language to العربية" in result.output
                assert "GAC_LANGUAGE=Arabic" in result.output


def test_language_select_rtl_predefined_hebrew(clean_env_state):
    """Test selecting Hebrew (RTL) shows warning and allows cancelling."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with (
                patch("gac.language_cli.show_rtl_warning") as mock_rtl_warning,
                patch("questionary.select") as mock_select,
                patch("gac.language_cli.should_show_rtl_warning", return_value=True),  # Force warning to show
            ):
                # Mock RTL warning to return False (user cancels)
                mock_rtl_warning.return_value = False
                mock_select.return_value.ask.return_value = "עברית"  # Select Hebrew

                result = runner.invoke(language)

                assert result.exit_code == 0
                # Check that RTL warning was called with language and path
                mock_rtl_warning.assert_called_once()
                args, kwargs = mock_rtl_warning.call_args
                assert args[0] == "Hebrew"
                assert isinstance(args[1], Path)
                assert "Language selection cancelled." in result.output
                # File should not be modified when RTL is cancelled
                assert not fake_path.exists() or "GAC_LANGUAGE" not in fake_path.read_text()


def test_language_select_custom_rtl_proceed(clean_env_state):
    """Test selecting a custom RTL language shows warning and allows proceeding."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with (
                patch("gac.language_cli.show_rtl_warning") as mock_rtl_warning,
                patch("questionary.select") as mock_select,
                patch("questionary.text") as mock_text,
                patch("gac.language_cli.should_show_rtl_warning", return_value=True),  # Force warning to show
            ):
                # Mock RTL warning to return True (user wants to proceed)
                mock_rtl_warning.return_value = True
                mock_select.return_value.ask.side_effect = [
                    "Custom",  # Select Custom
                    "Keep prefixes in English (feat:, fix:, etc.)",  # Prefix choice
                ]
                mock_text.return_value.ask.return_value = "Persian"  # Custom RTL-like name

                result = runner.invoke(language)

                assert result.exit_code == 0
                # Check that RTL warning was called with language and path
                mock_rtl_warning.assert_called_once()
                args, kwargs = mock_rtl_warning.call_args
                assert args[0] == "Persian"
                assert isinstance(args[1], Path)
                assert "✓ Set language to Persian" in result.output
                assert "GAC_LANGUAGE=Persian" in result.output


def test_language_select_custom_rtl_cancel(clean_env_state):
    """Test selecting a custom RTL language shows warning and allows cancelling."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            with (
                patch("gac.language_cli.show_rtl_warning") as mock_rtl_warning,
                patch("questionary.select") as mock_select,
                patch("questionary.text") as mock_text,
                patch("gac.language_cli.should_show_rtl_warning", return_value=True),  # Force warning to show
            ):
                # Mock RTL warning to return False (user cancels)
                mock_rtl_warning.return_value = False
                mock_select.return_value.ask.return_value = "Custom"  # Select Custom
                mock_text.return_value.ask.return_value = "Urdu"  # Custom RTL-like name

                result = runner.invoke(language)

                assert result.exit_code == 0
                # Check that RTL warning was called with language and path
                mock_rtl_warning.assert_called_once()
                args, kwargs = mock_rtl_warning.call_args
                assert args[0] == "Urdu"
                assert isinstance(args[1], Path)
                assert "Language selection cancelled." in result.output


def test_language_select_non_rtl_no_warning(clean_env_state):
    """Test selecting non-RTL languages doesn't show warning."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with (
            patch("gac.language_cli.GAC_ENV_PATH", fake_path),
            patch("gac.language_cli.show_rtl_warning") as mock_rtl_warning,
            patch("questionary.select") as mock_select,
        ):
            mock_select.return_value.ask.side_effect = [
                "Español",  # Select Spanish (non-RTL)
                "Keep prefixes in English (feat:, fix:, etc.)",  # Prefix choice
            ]

            result = runner.invoke(language)

            assert result.exit_code == 0
            # RTL warning should not be called for non-RTL languages
            mock_rtl_warning.assert_not_called()
            assert "✓ Set language to Español" in result.output
            assert "GAC_LANGUAGE=Spanish" in result.output


def test_language_with_existing_env_file(clean_env_state):
    """Test language selection when .gac.env file already exists (lines 34-35)."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Create the env file first to test the existing file path
            fake_path.write_text("# Existing config\nGAC_EXISTING=true\n")

            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.side_effect = [
                    "Français",  # Language selection
                    "Keep prefixes in English (feat:, fix:, etc.)",  # Prefix choice
                ]
                result = runner.invoke(language)

                assert result.exit_code == 0
                assert "✓ Set language to Français" in result.output
                assert "GAC_LANGUAGE=French" in result.output
                assert fake_path.exists()

                # Verify the file contents include both old and new content
                content = fake_path.read_text()
                assert "GAC_EXISTING=true" in content
                assert "GAC_LANGUAGE=French" in content or "GAC_LANGUAGE='French'" in content


def test_center_text_function(clean_env_state):
    """Test the center_text function (helps cover line 245)."""
    from gac.language_cli import center_text

    # Test basic centering - text should be padded with spaces
    result = center_text("test", width=20)
    assert "test" in result
    assert result.startswith(" ")  # Should start with spaces for centering

    # Test with odd width
    result = center_text("x", width=10)
    assert "x" in result
    assert result.startswith(" ")  # Should be centered

    # Test with default width
    result = center_text("hello")
    assert "hello" in result
    assert result.startswith(" ")  # Should be centered in default 80-width

    # Test with longer text than width
    result = center_text("very long text", width=10)
    assert "very long text" in result
    # Should not be overly centered when text is longer than width


def test_is_rtl_text_edge_cases(clean_env_state):
    """Test edge cases for RTL detection (covers more RTL logic)."""
    from gac.language_cli import is_rtl_text

    # Test with empty string
    assert not is_rtl_text("")

    # Test with special characters that are RTL
    assert is_rtl_text("فارسی")  # Persian
    assert is_rtl_text("اردو")  # Urdu

    # Test mixed text (should be RTL if any character is RTL)
    assert is_rtl_text("Hello العربية World")

    # Test with script detection
    assert is_rtl_text("יִידיש")  # Yiddish
