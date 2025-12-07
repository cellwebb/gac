"""Additional tests for utils.py to increase coverage from 92% to 95%+."""

from unittest.mock import MagicMock, patch

import pytest

from gac.utils import get_safe_encodings, run_subprocess, run_subprocess_with_encoding


class TestUtilsMissingCoverage:
    """Tests for uncovered lines in utils.py."""

    def test_get_safe_encodings_utf8_fallback(self):
        """Test line 122: utf-8 fallback path."""
        # Mock system encodings that don't include utf-8 initially
        with patch("locale.getpreferredencoding", return_value="iso-8859-1"):
            with patch("sys.platform", "linux"):  # Not Windows
                encodings = get_safe_encodings()

                # Should include utf-8 as first priority and iso-8859-1 as locale fallback
                assert "utf-8" in encodings
                assert "iso-8859-1" in encodings
                assert encodings[0] == "utf-8"  # utf-8 is always first

    @patch("subprocess.run")
    def test_run_subprocess_with_encoding_success(self, mock_run):
        """Test successful subprocess execution with encoding."""
        mock_result = MagicMock()
        mock_result.stdout = "success output"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_subprocess_with_encoding(["echo", "hello"], "utf-8")

        assert result == "success output"
        mock_run.assert_called_once_with(
            ["echo", "hello"],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )

    @patch("gac.utils.get_safe_encodings")
    def test_run_subprocess_with_multiple_encodings(self, mock_encodings):
        """Test subprocess with multiple encoding attempts using run_subprocess."""
        mock_encodings.return_value = ["utf-8", "iso-8859-1"]

        with patch("subprocess.run") as mock_run:
            # First attempt fails with UnicodeError
            mock_run.side_effect = [
                UnicodeError("decode failed"),
                MagicMock(returncode=0, stdout="final output", stderr=""),
            ]

            result = run_subprocess(["echo", "test"], raise_on_error=False)

            assert result == "final output"
            assert mock_run.call_count == 2

    @patch("gac.utils.get_safe_encodings")
    @patch("subprocess.run")
    def test_run_subprocess_all_encodings_fail(self, mock_run, mock_encodings):
        """Test subprocess where all encoding attempts fail with UnicodeError."""
        mock_encodings.return_value = ["utf-8", "ascii"]

        # All attempts fail with UnicodeError
        mock_run.side_effect = UnicodeError("decode failed")

        from subprocess import CalledProcessError

        with pytest.raises(CalledProcessError) as exc_info:
            run_subprocess(["false"])

        # The error message should be in stderr attribute
        assert exc_info.value.stderr == "Encoding error: decode failed"
