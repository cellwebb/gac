"""Tests for gac.constants module."""

from gac.constants import FileStatus, Logging, Utility


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
