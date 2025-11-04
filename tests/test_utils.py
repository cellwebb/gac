"""Tests for gac.utils module."""

import subprocess
from unittest import mock

import pytest

from gac.errors import GacError
from gac.utils import get_safe_encodings, print_message, run_subprocess, run_subprocess_with_encoding, setup_logging


def test_setup_logging_all_branches(monkeypatch):
    # Test string log_level, quiet, force, suppress_noisy
    setup_logging("DEBUG", quiet=False, force=True, suppress_noisy=True)
    setup_logging("INFO", quiet=True)  # Should set log_level to ERROR
    setup_logging(10, quiet=False)  # int log level


def test_print_message_all_levels():
    # Just ensure no exceptions for various levels
    for level in ["info", "success", "warning", "error", "header", "notification"]:
        print_message("test", level=level)


def test_run_subprocess_success(monkeypatch):
    class Result:
        def __init__(self):
            self.returncode = 0
            self.stdout = "output\n"
            self.stderr = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: Result())
    assert run_subprocess(["echo", "hi"]) == "output"


def test_run_subprocess_nonzero(monkeypatch):
    class Result:
        def __init__(self):
            self.returncode = 1
            self.stdout = "fail\n"
            self.stderr = "bad"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: Result())
    import subprocess as sp

    import pytest

    with pytest.raises(sp.CalledProcessError):
        run_subprocess(["fail"], check=True, raise_on_error=True)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], check=True, raise_on_error=False) == ""


def test_run_subprocess_timeout(monkeypatch):
    import subprocess as sp

    # Mock subprocess.run to simulate a timeout
    with mock.patch("subprocess.run", side_effect=sp.TimeoutExpired(cmd="timeout", timeout=0.1)):
        with pytest.raises(GacError):
            run_subprocess(["timeout"])  # Should raise GacError


def test_run_subprocess_calledprocesserror(monkeypatch):
    import subprocess as sp

    def raise_cpe(*a, **kw):
        raise sp.CalledProcessError(1, ["fail"], "", "fail")

    monkeypatch.setattr("subprocess.run", raise_cpe)
    import pytest

    with pytest.raises(sp.CalledProcessError):
        run_subprocess(["fail"], raise_on_error=True)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], raise_on_error=False) == ""


def test_run_subprocess_exception(monkeypatch):
    def raise_exc(*a, **kw):
        raise Exception("fail")

    monkeypatch.setattr("subprocess.run", raise_exc)
    # Should not raise if raise_on_error is False
    assert run_subprocess(["fail"], raise_on_error=False) == ""
    # Should raise if raise_on_error is True
    import pytest

    with pytest.raises(subprocess.CalledProcessError):
        run_subprocess(["fail"], raise_on_error=True)


class TestEncodingFunctions:
    """Test encoding-related functions."""

    def test_get_safe_encodings(self):
        """Test that get_safe_encodings returns expected encodings."""
        encodings = get_safe_encodings()

        # Should always include utf-8 first
        assert encodings[0] == "utf-8"
        assert len(encodings) >= 1

        # Should include multiple encodings
        assert len(set(encodings)) == len(encodings)  # No duplicates

    @mock.patch("sys.platform", "win32")
    @mock.patch("locale.getpreferredencoding", return_value="cp936")
    def test_get_safe_encodings_windows_chinese(self, mock_locale):
        """Test Windows Chinese locale encoding fallback."""
        encodings = get_safe_encodings()

        # Should include Windows-specific encodings
        assert "utf-8" in encodings
        assert "cp936" in encodings  # GBK
        assert "cp1252" in encodings  # Windows-1252
        assert "cp65001" in encodings  # UTF-8 Windows code page

    @mock.patch("sys.platform", "darwin")
    @mock.patch("locale.getpreferredencoding", return_value="UTF-8")
    def test_get_safe_encodings_macos(self, mock_locale):
        """Test macOS encoding selection."""
        encodings = get_safe_encodings()

        # Should prioritize utf-8 and locale encoding
        assert encodings[0] == "utf-8"
        assert "UTF-8" in encodings

    def test_run_subprocess_with_encoding_success(self):
        """Test successful subprocess call with specific encoding."""

        class MockResult:
            def __init__(self):
                self.returncode = 0
                self.stdout = "test output"
                self.stderr = ""

        with mock.patch("subprocess.run", return_value=MockResult()):
            result = run_subprocess_with_encoding(["echo", "test"], encoding="utf-8")
            assert result == "test output"

    def test_run_subprocess_with_encoding_unicode_error(self):
        """Test handling of UnicodeDecodeError."""

        with mock.patch("subprocess.run", side_effect=UnicodeError("encoding error")):
            with pytest.raises(UnicodeError):
                run_subprocess_with_encoding(["fail"], encoding="utf-8")

    def test_run_subprocess_encoding_fallback_success(self):
        """Test successful encoding fallback."""

        class MockResult:
            def __init__(self):
                self.returncode = 0
                self.stdout = "test output"
                self.stderr = ""

        def mock_run(*args, **kwargs):
            encoding = kwargs.get("encoding", "utf-8")
            if encoding == "utf-8":
                raise UnicodeError("UTF-8 failed")
            elif encoding == "cp936":
                return MockResult()
            else:
                raise UnicodeError("Other encoding failed")

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "cp936"]):
                result = run_subprocess(["echo", "test"])
                assert result == "test output"

    def test_run_subprocess_encoding_fallback_all_fail(self):
        """Test when all encodings fail."""

        def mock_run(*args, **kwargs):
            raise UnicodeError(f"Failed with encoding {kwargs.get('encoding', 'unknown')}")

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "cp936"]):
                with pytest.raises(subprocess.CalledProcessError) as exc_info:
                    run_subprocess(["echo", "test"])

                # Should include encoding error information in stderr
                assert "Encoding error" in str(exc_info.value.stderr)

    def test_run_subprocess_non_encoding_error_no_retry(self):
        """Test that non-encoding errors don't trigger fallback."""
        import subprocess as sp

        def mock_run(*args, **kwargs):
            raise sp.CalledProcessError(1, ["fail"], "", "Command failed")

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "cp936"]):
                with pytest.raises(subprocess.CalledProcessError):
                    run_subprocess(["fail"])

    def test_run_subprocess_chinese_content_simulation(self):
        """Test handling of content that might cause Unicode issues on Chinese Windows."""
        # Simulate the exact scenario from the bug report
        # This would be a byte 0xa6 in GBK that's not valid GBK but is valid UTF-8

        class MockResult:
            def __init__(self, encoding):
                self.returncode = 0
                self.stdout = "test content with special char: \xa6"
                self.stderr = ""

        def mock_run(*args, **kwargs):
            encoding = kwargs.get("encoding", "utf-8")
            if encoding == "gbk" or encoding == "cp936":
                # Simulate UnicodeDecodeError
                raise UnicodeError("'gbk' codec can't decode byte 0xa6 in position 831")
            else:
                return MockResult(encoding)

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "gbk"]):
                result = run_subprocess(["git", "status"])
                assert "test content with special char" in result

    @mock.patch("sys.platform", "win32")
    @mock.patch("locale.getpreferredencoding", return_value="cp936")
    def test_run_subprocess_windows_chinese_integration(self, mock_locale):
        """Test integration scenario for Chinese Windows."""

        # Mock git command that would fail with GBK but succeed with UTF-8
        def mock_run(*args, **kwargs):
            encoding = kwargs.get("encoding", "utf-8")
            if encoding in ["gbk", "cp936"]:
                # This simulates the exact error from the bug report
                raise UnicodeError("'gbk' codec can't decode byte 0xa6 in position 831: illegal multibyte sequence")
            else:
                # UTF-8 succeeds
                result = mock.Mock()
                result.returncode = 0
                result.stdout = "M\t中文文件名.txt\nA\t测试.py"
                result.stderr = ""
                return result

        with mock.patch("subprocess.run", side_effect=mock_run):
            # Should work because it will try UTF-8 after GBK fails
            result = run_subprocess(["git", "diff", "--name-status"])
            assert "中文文件名.txt" in result
            assert "测试.py" in result
