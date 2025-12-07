"""Tests for gac.constants module."""

from gac.constants import FileStatus, Logging, Utility
from gac.constants.languages import Languages


class TestConstants:
    """Tests for project constants."""

    def test_file_status_enum(self):
        """Test the FileStatus enum values."""
        # Test enum values
        assert FileStatus.MODIFIED.value == "M"
        assert FileStatus.ADDED.value == "A"
        assert FileStatus.DELETED.value == "D"
        assert FileStatus.RENAMED.value == "R"
        assert FileStatus.COPIED.value == "C"
        assert FileStatus.UNTRACKED.value == "?"

        # Test enum behavior
        assert FileStatus("M") == FileStatus.MODIFIED
        assert FileStatus("A") == FileStatus.ADDED

        # Verify we can use them as expected
        status = FileStatus.MODIFIED
        assert status.name == "MODIFIED"
        assert str(status.value) == "M"

    def test_logging_constants(self):
        """Test logging related constants."""
        assert Logging.DEFAULT_LEVEL == "WARNING"
        assert "DEBUG" in Logging.LEVELS
        assert "INFO" in Logging.LEVELS
        assert "WARNING" in Logging.LEVELS
        assert "ERROR" in Logging.LEVELS
        assert len(Logging.LEVELS) == 4  # Ensure no unexpected levels

    def test_encoding_constants(self):
        """Test encoding constants."""
        assert Utility.DEFAULT_ENCODING == "cl100k_base"  # Verify base encoding for tokenization

    def test_languages_code_map(self):
        """Test the language code mapping dictionary."""
        # Test some common mappings
        assert Languages.CODE_MAP["en"] == "English"
        assert Languages.CODE_MAP["zh"] == "Simplified Chinese"
        assert Languages.CODE_MAP["zh-cn"] == "Simplified Chinese"
        assert Languages.CODE_MAP["zh-hans"] == "Simplified Chinese"
        assert Languages.CODE_MAP["zh-tw"] == "Traditional Chinese"
        assert Languages.CODE_MAP["zh-hant"] == "Traditional Chinese"
        assert Languages.CODE_MAP["ja"] == "Japanese"
        assert Languages.CODE_MAP["ko"] == "Korean"
        assert Languages.CODE_MAP["es"] == "Spanish"
        assert Languages.CODE_MAP["fr"] == "French"
        assert Languages.CODE_MAP["de"] == "German"
        assert Languages.CODE_MAP["ru"] == "Russian"
        assert Languages.CODE_MAP["ar"] == "Arabic"

        # Test total count (should be >= 30 languages supported)
        assert len(Languages.CODE_MAP) >= 30

    def test_languages_list(self):
        """Test the languages selection list."""
        # Test that we have the expected first entry
        assert Languages.LANGUAGES[0] == ("English", "English")

        # Test some other entries
        assert ("简体中文", "Simplified Chinese") in Languages.LANGUAGES
        assert ("日本語", "Japanese") in Languages.LANGUAGES
        assert ("Español", "Spanish") in Languages.LANGUAGES
        assert ("العربية", "Arabic") in Languages.LANGUAGES
        assert ("Custom", "Custom") in Languages.LANGUAGES

        # Test that all tuples have the right format
        for display_name, english_name in Languages.LANGUAGES:
            assert isinstance(display_name, str)
            assert isinstance(english_name, str)
            assert len(display_name) > 0
            assert len(english_name) > 0

        # Test that we have a reasonable number of languages
        assert len(Languages.LANGUAGES) >= 20

    def test_resolve_code_with_recognized_codes(self):
        """Test resolve_code with recognized language codes."""
        # Test basic codes
        assert Languages.resolve_code("en") == "English"
        assert Languages.resolve_code("es") == "Spanish"
        assert Languages.resolve_code("fr") == "French"
        assert Languages.resolve_code("de") == "German"
        assert Languages.resolve_code("ja") == "Japanese"
        assert Languages.resolve_code("ko") == "Korean"
        assert Languages.resolve_code("zh") == "Simplified Chinese"
        assert Languages.resolve_code("ar") == "Arabic"
        assert Languages.resolve_code("ru") == "Russian"

        # Test Chinese variants
        assert Languages.resolve_code("zh-CN") == "Simplified Chinese"
        assert Languages.resolve_code("zh-cn") == "Simplified Chinese"
        assert Languages.resolve_code("ZH-HANS") == "Simplified Chinese"  # Case insensitive
        assert Languages.resolve_code("zh-tw") == "Traditional Chinese"
        assert Languages.resolve_code("zh-TW") == "Traditional Chinese"
        assert Languages.resolve_code("zh-hant") == "Traditional Chinese"

        # Test with extra spaces
        assert Languages.resolve_code("  en  ") == "English"
        assert Languages.resolve_code("\tes\n") == "Spanish"

    def test_resolve_code_with_unrecognized_codes(self):
        """Test resolve_code with unrecognized language codes."""
        # Test full names (should return as-is)
        assert Languages.resolve_code("English") == "English"
        assert Languages.resolve_code("Spanish") == "Spanish"
        assert Languages.resolve_code("Español") == "Español"  # Spanish script
        assert Languages.resolve_code("简体中文") == "简体中文"  # Chinese script

        # Test unrecognized codes (should return as-is)
        assert Languages.resolve_code("unknown") == "unknown"
        assert Languages.resolve_code("xx") == "xx"
        assert Languages.resolve_code("custom-lang") == "custom-lang"

        # Test edge cases
        assert Languages.resolve_code("") == ""
        assert Languages.resolve_code("xyz") == "xyz"
        assert Languages.resolve_code("MyCustomLanguage") == "MyCustomLanguage"
