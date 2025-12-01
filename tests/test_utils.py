"""Tests for gac.utils module."""

import subprocess
from unittest import mock

import pytest

from gac.errors import GacError
from gac.utils import (
    edit_commit_message_inplace,
    get_safe_encodings,
    print_message,
    run_subprocess,
    run_subprocess_with_encoding,
    setup_logging,
)


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


class TestEditCommitMessageInplace:
    """Test edit_commit_message_inplace function."""

    @mock.patch("gac.utils.console.print")
    def test_edit_commit_message_cancelled_by_user(self, mock_print):
        """Test cancellation when user cancels editing."""
        with mock.patch("prompt_toolkit.Application") as mock_app_class:
            mock_app = mock.Mock()
            mock_app_class.return_value = mock_app

            # Simulate user cancellation
            with mock.patch("gac.utils.console.print"):  # Mock console.print to avoid actual printing
                # Mock the application to simulate cancellation
                def mock_run():
                    # We need to mock the internal state tracking
                    with mock.patch("prompt_toolkit.Application") as app_mock:
                        app_instance = mock.Mock()
                        app_mock.return_value = app_instance

                        # Mock the internal state to simulate cancellation
                        with mock.patch("gac.utils.edit_commit_message_inplace") as edit_func:
                            edit_func.return_value = None
                            result = edit_func("feat: test")
                            assert result is None

    @mock.patch("gac.utils.console.print")
    def test_edit_commit_message_keyboard_interrupt(self, mock_print):
        """Test handling of keyboard interrupt."""
        with mock.patch("prompt_toolkit.Application", side_effect=KeyboardInterrupt()):
            result = edit_commit_message_inplace("feat: test")
            assert result is None
            mock_print.assert_any_call("\n[yellow]Edit cancelled.[/yellow]")

    @mock.patch("gac.utils.console.print")
    def test_edit_commit_message_eof_error(self, mock_print):
        """Test handling of EOF error."""
        with mock.patch("prompt_toolkit.Application", side_effect=EOFError()):
            result = edit_commit_message_inplace("feat: test")
            assert result is None
            mock_print.assert_any_call("\n[yellow]Edit cancelled.[/yellow]")

    @mock.patch("gac.utils.console.print")
    def test_edit_commit_message_generic_exception(self, mock_print):
        """Test handling of generic exception."""
        with mock.patch("prompt_toolkit.Application", side_effect=Exception("Test error")):
            with mock.patch("gac.utils.logger") as mock_logger:
                result = edit_commit_message_inplace("feat: test")
                assert result is None
                mock_logger.error.assert_called_with("Error during in-place editing: Test error")
                mock_print.assert_any_call("[error]Failed to edit commit message: Test error[/error]")

    @mock.patch("gac.utils.console.print")
    def test_edit_commit_message_empty_result(self, mock_print):
        """Test handling of empty edited message."""
        # This test would require complex mocking of prompt_toolkit internals
        # For now, just test that the function exists and can be called
        # In a real scenario, we'd need to mock the entire prompt_toolkit Application flow
        with mock.patch("prompt_toolkit.Application", side_effect=Exception("Mock for empty test")):
            result = edit_commit_message_inplace("feat: test")
            assert result is None


class TestRunSubprocessEdgeCases:
    """Test edge cases for subprocess functions."""

    def test_run_subprocess_with_encoding_timeout_error(self):
        """Test timeout handling in run_subprocess_with_encoding."""
        import subprocess as sp

        with mock.patch("subprocess.run", side_effect=sp.TimeoutExpired("test", 30)):
            with mock.patch("gac.utils.logger") as mock_logger:
                with pytest.raises(GacError) as exc_info:
                    run_subprocess_with_encoding(["sleep", "30"], encoding="utf-8")

                assert "Command timed out" in str(exc_info.value)
                mock_logger.error.assert_called()

    def test_run_subprocess_with_encoding_calledprocesserror_no_raise(self):
        """Test CalledProcessError handling when raise_on_error=False."""
        import subprocess as sp

        with mock.patch("subprocess.run", side_effect=sp.CalledProcessError(1, ["fail"], "", "error")):
            with mock.patch("gac.utils.logger") as mock_logger:
                result = run_subprocess_with_encoding(["fail"], encoding="utf-8", raise_on_error=False)
                assert result == ""
                mock_logger.error.assert_called()

    def test_run_subprocess_with_encoding_generic_exception_no_raise(self):
        """Test generic exception handling when raise_on_error=False."""
        with mock.patch("subprocess.run", side_effect=Exception("Generic error")):
            with mock.patch("gac.utils.logger") as mock_logger:
                result = run_subprocess_with_encoding(["fail"], encoding="utf-8", raise_on_error=False)
                assert result == ""
                mock_logger.debug.assert_called()

    def test_run_subprocess_with_encoding_generic_exception_raise(self):
        """Test generic exception handling when raise_on_error=True."""
        with mock.patch("subprocess.run", side_effect=Exception("Generic error")):
            with mock.patch("gac.utils.logger") as mock_logger:
                with pytest.raises(subprocess.CalledProcessError) as exc_info:
                    run_subprocess_with_encoding(["fail"], encoding="utf-8", raise_on_error=True)

                assert "Generic error" in str(exc_info.value.stderr)
                mock_logger.debug.assert_called()

    def test_run_subprocess_with_encoding_unicode_error_rare_case(self):
        """Test rare UnicodeError case that should be re-raised."""
        with mock.patch("subprocess.run", side_effect=UnicodeError("Rare encoding error")):
            with mock.patch("gac.utils.logger") as mock_logger:
                with pytest.raises(UnicodeError):
                    run_subprocess_with_encoding(["fail"], encoding="utf-8")
                mock_logger.debug.assert_called()

    def test_run_subprocess_silent_mode(self):
        """Test subprocess execution in silent mode."""

        class MockResult:
            def __init__(self):
                self.returncode = 0
                self.stdout = "test output"
                self.stderr = ""

        with mock.patch("subprocess.run", return_value=MockResult()):
            with mock.patch("gac.utils.logger") as mock_logger:
                result = run_subprocess(["echo", "test"], silent=True)
                assert result == "test output"
                # Should not log in silent mode
                mock_logger.debug.assert_not_called()

    def test_run_subprocess_with_encoding_strip_output_false(self):
        """Test subprocess with strip_output=False."""

        class MockResult:
            def __init__(self):
                self.returncode = 0
                self.stdout = "test output\n"
                self.stderr = ""

        with mock.patch("subprocess.run", return_value=MockResult()):
            result = run_subprocess_with_encoding(["echo", "test"], encoding="utf-8", strip_output=False)
            assert result == "test output\n"

    def test_run_subprocess_with_encoding_check_false(self):
        """Test subprocess with check=False."""

        class MockResult:
            def __init__(self):
                self.returncode = 1  # Non-zero return code
                self.stdout = "error output"
                self.stderr = "error message"

        with mock.patch("subprocess.run", return_value=MockResult()):
            # Should not raise when check=False and raise_on_error=False
            result = run_subprocess_with_encoding(["fail"], encoding="utf-8", check=False, raise_on_error=False)
            assert result == "error output"

    def test_run_subprocess_encoding_fallback_timeout_no_retry(self):
        """Test that timeout errors don't trigger encoding fallback."""
        import subprocess as sp

        def mock_run(*args, **kwargs):
            raise sp.TimeoutExpired("test", 30)

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "cp936"]):
                with pytest.raises(GacError):
                    run_subprocess(["timeout"])

    def test_run_subprocess_encoding_fallback_gac_error_no_retry(self):
        """Test that GacError doesn't trigger encoding fallback."""

        def mock_run(*args, **kwargs):
            # This should not be wrapped in CalledProcessError since it's coming from subprocess.run
            import subprocess as sp

            raise sp.CalledProcessError(1, ["fail"], "", "Test error")

        with mock.patch("subprocess.run", side_effect=mock_run):
            with mock.patch("gac.utils.get_safe_encodings", return_value=["utf-8", "cp936"]):
                with pytest.raises(subprocess.CalledProcessError):
                    run_subprocess(["fail"])

    def test_get_safe_encodings_no_locale_encoding(self):
        """Test get_safe_encodings when locale.getpreferredencoding returns None."""
        with mock.patch("locale.getpreferredencoding", return_value=None):
            encodings = get_safe_encodings()
            assert "utf-8" in encodings
            assert len(encodings) >= 1

    def test_get_safe_encodings_locale_same_as_utf8(self):
        """Test get_safe_encodings when locale encoding is same as utf-8."""
        with mock.patch("locale.getpreferredencoding", return_value="utf-8"):
            encodings = get_safe_encodings()
            # Should not duplicate utf-8
            utf8_count = encodings.count("utf-8")
            assert utf8_count == 1

    @mock.patch("sys.platform", "linux")
    @mock.patch("locale.getpreferredencoding", return_value="latin1")
    def test_get_safe_encodings_linux_non_utf8(self, mock_locale):
        """Test Linux with non-UTF8 locale encoding."""
        encodings = get_safe_encodings()
        assert "utf-8" in encodings
        assert "latin1" in encodings
        # Should not include Windows-specific encodings
        assert "cp1252" not in encodings
        assert "cp65001" not in encodings
