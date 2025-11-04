"""Extended tests for language_cli module to improve coverage."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from gac.language_cli import (
    center_text,
    get_terminal_width,
    is_rtl_text,
    language,
    should_show_rtl_warning,
    show_rtl_warning,
)


def test_should_show_rtl_warning_no_config():
    """Test should_show_rtl_warning when no config exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Clear any existing environment variable first
            if "GAC_RTL_CONFIRMED" in os.environ:
                del os.environ["GAC_RTL_CONFIRMED"]
            # No config file should return True (show warning)
            assert should_show_rtl_warning() is True


def test_should_show_rtl_warning_config_exists_not_confirmed():
    """Test should_show_rtl_warning when config exists but RTL not confirmed."""
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        # Create config with RTL not confirmed explicitly set to false
        fake_path.write_text("GAC_LANGUAGE=Spanish\nGAC_TRANSLATE_PREFIXES=false\nGAC_RTL_CONFIRMED=false\n")

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Clear any existing environment variable first
            if "GAC_RTL_CONFIRMED" in os.environ:
                del os.environ["GAC_RTL_CONFIRMED"]
            assert should_show_rtl_warning() is True


def test_should_show_rtl_warning_config_exists_confirmed_true():
    """Test should_show_rtl_warning when RTL confirmed as true."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        # Create config with RTL confirmed as true
        fake_path.write_text("GAC_RTL_CONFIRMED=true\n")

        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Clear any existing environment variable first
            if "GAC_RTL_CONFIRMED" in os.environ:
                del os.environ["GAC_RTL_CONFIRMED"]
            assert should_show_rtl_warning() is False


def test_should_show_rtl_warning_config_exists_confirmed_variants():
    """Test should_show_rtl_warning with various confirmation values."""
    # should_show_rtl_warning returns True when we should show the warning
    # i.e., when RTL is NOT confirmed
    test_values = {
        "true": False,  # Don't show warning - RTL is confirmed
        "1": False,
        "yes": False,
        "on": False,
        "false": True,  # Show warning - RTL is not confirmed
        "0": True,
        "no": True,
        "off": True,
    }

    for value, expected in test_values.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = Path(tmpdir) / ".gac.env"
            fake_path.write_text(f"GAC_RTL_CONFIRMED={value}\n")
            with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
                # Clear any existing environment variable first
                if "GAC_RTL_CONFIRMED" in os.environ:
                    del os.environ["GAC_RTL_CONFIRMED"]
                assert should_show_rtl_warning() is expected, f"Failed for value: {value}"

    # Test empty config (no file)
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        with patch("gac.language_cli.GAC_ENV_PATH", fake_path):
            # Clear any existing environment variable first
            if "GAC_RTL_CONFIRMED" in os.environ:
                del os.environ["GAC_RTL_CONFIRMED"]
            assert should_show_rtl_warning() is True  # Show warning when no config exists


def test_is_rtl_text_with_rtl_characters():
    """Test RTL text detection with actual RTL characters."""
    # Test Arabic characters
    assert is_rtl_text("مرحبا") is True
    assert is_rtl_text("العربية") is True

    # Test Hebrew characters
    assert is_rtl_text("שלום") is True
    assert is_rtl_text("עברית") is True

    # Test mixed with RTL characters
    assert is_rtl_text("Hello مرحبا") is True
    assert is_rtl_text("Test שלום World") is True


def test_is_rtl_text_edge_cases():
    """Test RTL detection with edge cases."""
    # Empty string
    assert is_rtl_text("") is False

    # Only spaces
    assert is_rtl_text("   ") is False

    # Special characters but not RTL
    assert is_rtl_text("@#$%^&*()") is False

    # Numbers and punctuation
    assert is_rtl_text("123 456") is False

    # Unicode but not RTL scripts
    assert is_rtl_text("🎉🎊👍") is False
    assert is_rtl_text("αβγδε") is False  # Greek
    assert is_rtl_text("абвгд") is False  # Cyrillic


def test_center_text_basic():
    """Test basic text centering functionality."""
    # Single line centering
    result = center_text("Hello", width=20)
    # The result should be centered (padding + Hello)
    assert "Hello" in result
    assert result.strip() == "Hello"
    # Result should be shorter than or equal to width
    assert len(result) <= 20

    # Text wider than width
    result = center_text("This is a very long text", width=10)
    assert "This is a very long text" in result


def test_center_text_multiline():
    """Test centering with multi-line text."""
    text = "Line 1\nLine 2\nLine 3"
    result = center_text(text, width=20)

    lines = result.split("\n")
    assert len(lines) == 3

    for line in lines:
        if line.strip():  # Skip empty lines
            assert len(line) <= 20
            assert line.strip() in ["Line 1", "Line 2", "Line 3"]


def test_center_text_empty_and_whitespace():
    """Test centering with empty lines and whitespace."""
    text = "Line 1\n\nLine 3"
    result = center_text(text, width=20)

    lines = result.split("\n")
    assert len(lines) == 3
    assert "Line 1" in lines[0]  # Centered (first line)
    assert lines[1] == ""  # Empty line preserved
    assert "Line 3" in lines[2]  # Centered (third line)


def test_center_text_with_wide_characters():
    """Test centering with East Asian wide characters."""
    # Test with CJK characters (which are double-width)
    text = "日本語"
    result = center_text(text, width=20)
    assert "日本語" in result

    # Test mixed ASCII and wide characters
    text = "Hello 日本語"
    result = center_text(text, width=30)
    assert "Hello 日本語" in result


def test_get_terminal_width_success():
    """Test get_terminal_width when successfully getting terminal size."""
    with patch("shutil.get_terminal_size") as mock_get_size:
        mock_size = MagicMock()
        mock_size.columns = 120
        mock_get_size.return_value = mock_size

        assert get_terminal_width() == 120


def test_get_terminal_width_os_error():
    """Test get_terminal_width when OSError occurs."""
    with patch("shutil.get_terminal_size") as mock_get_size:
        mock_get_size.side_effect = OSError("No terminal")

        assert get_terminal_width() == 80  # Fallback value


def test_get_terminal_width_attribute_error():
    """Test get_terminal_width when AttributeError occurs."""
    with patch("shutil.get_terminal_size") as mock_get_size:
        mock_get_size.side_effect = AttributeError("No columns attribute")

        assert get_terminal_width() == 80  # Fallback value


def test_show_rtl_warning_proceed_true():
    """Test show_rtl_warning when user chooses to proceed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.language_cli.GAC_ENV_PATH", fake_path),
            patch("gac.language_cli.get_terminal_width", return_value=80),
            patch("gac.language_cli.center_text", return_value="  ⚠️  RTL Language Detected  "),
            patch("questionary.confirm") as mock_confirm,
        ):
            mock_confirm.return_value.ask.return_value = True

            result = show_rtl_warning("Arabic")

            assert result is True
            # Check that RTL preference was saved
            content = fake_path.read_text()
            assert "GAC_RTL_CONFIRMED='true'" in content


def test_show_rtl_warning_proceed_false():
    """Test show_rtl_warning when user chooses not to proceed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.language_cli.GAC_ENV_PATH", fake_path),
            patch("gac.language_cli.get_terminal_width", return_value=80),
            patch("gac.language_cli.center_text", return_value="  ⚠️  RTL Language Detected  "),
            patch("questionary.confirm") as mock_confirm,
        ):
            mock_confirm.return_value.ask.return_value = False

            result = show_rtl_warning("Hebrew")

            assert result is False


def test_show_rtl_warning_proceed_none():
    """Test show_rtl_warning when user cancels (returns None)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"

        with (
            patch("gac.language_cli.GAC_ENV_PATH", fake_path),
            patch("gac.language_cli.get_terminal_width", return_value=80),
            patch("gac.language_cli.center_text", return_value="  ⚠️  RTL Language Detected  "),
            patch("questionary.confirm") as mock_confirm,
        ):
            mock_confirm.return_value.ask.return_value = None

            result = show_rtl_warning("Urdu")

            assert result is False


def test_rtl_previously_confirmed_flow():
    """Test the flow when RTL warning was previously confirmed."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_path = Path(tmpdir) / ".gac.env"
        # Create config with RTL already confirmed
        fake_path.write_text("GAC_RTL_CONFIRMED=true\n")

        with (
            patch("gac.language_cli.GAC_ENV_PATH", fake_path),
            patch("questionary.select") as mock_select,
            patch("questionary.text") as mock_text,
        ):
            # Test custom RTL language
            mock_select.return_value.ask.side_effect = [
                "Custom",  # Select Custom
                "Keep prefixes in English (feat:, fix:, etc.)",
            ]
            mock_text.return_value.ask.return_value = "Arabic"

            result = runner.invoke(language)

            assert result.exit_code == 0
            # Should show "previously confirmed" message
            assert "RTL warning previously confirmed" in result.output


def test_rtl_multiple_scripts():
    """Test RTL detection with lesser-known RTL scripts."""
    # Test actual Arabic characters that will have ARABIC in their Unicode name
    assert is_rtl_text("أ") is True  # Arabic letter alef with hamza above

    # Test actual Hebrew characters that will have HEBREW in their Unicode name
    assert is_rtl_text("א") is True  # Hebrew letter alef


def test_center_text_edge_cases():
    """Test edge cases for text centering."""
    # Very short width
    result = center_text("Hello", width=5)
    assert "Hello" in result

    # Zero width
    result = center_text("Hello", width=0)
    assert "Hello" in result

    # Negative width (shouldn't happen but let's be safe)
    result = center_text("Hello", width=-10)
    assert "Hello" in result
