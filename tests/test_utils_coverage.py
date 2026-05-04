"""Additional tests for utils module to improve coverage."""

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from gac.errors import GacError


class TestUtilsLazyExports:
    """Test lazy __getattr__ re-exports in utils module."""

    def test_getattr_count_tokens(self):
        """Test lazy re-export of count_tokens."""
        from gac.utils import count_tokens

        assert callable(count_tokens)

    def test_getattr_extract_text_content(self):
        """Test lazy re-export of extract_text_content."""
        from gac.utils import extract_text_content

        assert callable(extract_text_content)

    def test_getattr_edit_commit_message_inplace(self):
        """Test lazy re-export of edit_commit_message_inplace."""
        from gac.utils import edit_commit_message_inplace

        assert callable(edit_commit_message_inplace)

    def test_getattr_edit_commit_message_in_editor(self):
        """Test lazy re-export of edit_commit_message_in_editor."""
        from gac.utils import edit_commit_message_in_editor

        assert callable(edit_commit_message_in_editor)

    def test_getattr_unknown_raises(self):
        """Test that unknown attributes raise AttributeError."""
        import gac.utils as utils_module

        with pytest.raises(AttributeError, match="has no attribute"):
            utils_module.__getattr__("nonexistent_attr")


class TestRunSubprocessEdgeCases:
    """Test run_subprocess edge cases for coverage."""

    def test_run_subprocess_nonzero_exit_no_raise(self):
        """When command fails and raise_on_error=False, return output."""
        from gac.utils import run_subprocess

        with patch("gac.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="output", stderr="error")
            result = run_subprocess(["false"], raise_on_error=False, check=False)
            assert result == "output"

    def test_run_subprocess_generic_exception_no_raise(self):
        """When command raises generic exception and raise_on_error=False, return empty string."""
        from gac.utils import run_subprocess

        with patch("gac.utils.subprocess.run", side_effect=OSError("broken")):
            result = run_subprocess(["test"], raise_on_error=False)
            assert result == ""

    def test_run_subprocess_generic_exception_raise(self):
        """When command raises generic exception and raise_on_error=True, raise CalledProcessError."""
        from gac.utils import run_subprocess

        with patch("gac.utils.subprocess.run", side_effect=OSError("broken")):
            with pytest.raises(subprocess.CalledProcessError):
                run_subprocess(["test"], raise_on_error=True)

    def test_run_subprocess_timeout(self):
        """When command times out, raise GacError."""
        from gac.utils import run_subprocess

        with patch("gac.utils.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 60)):
            with pytest.raises(GacError, match="timed out"):
                run_subprocess(["test"])

    def test_run_subprocess_with_encoding_fallback(self):
        """When utf-8 fails with UnicodeError, try next encoding."""
        from gac.utils import run_subprocess

        call_count = 0

        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and kwargs.get("encoding") == "utf-8":
                raise UnicodeError("bad utf-8")
            return MagicMock(returncode=0, stdout="success", stderr="")

        with patch("gac.utils.subprocess.run", side_effect=mock_run_side_effect):
            result = run_subprocess(["test"])
            assert result == "success"

    def test_run_subprocess_all_encodings_fail(self):
        """When all encodings fail with UnicodeError, raise CalledProcessError."""
        from gac.utils import run_subprocess

        with patch("gac.utils.subprocess.run", side_effect=UnicodeError("bad")):
            with pytest.raises(subprocess.CalledProcessError):
                run_subprocess(["test"])

    def test_run_subprocess_with_encoding_check_false(self):
        """When check=False and returncode != 0, don't raise by default."""
        from gac.utils import run_subprocess_with_encoding

        with patch("gac.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="output", stderr="error")
            result = run_subprocess_with_encoding(["test"], "utf-8", check=False, raise_on_error=False)
            assert result == "output"

    def test_run_subprocess_with_encoding_strip_false(self):
        """When strip_output=False, don't strip whitespace."""
        from gac.utils import run_subprocess_with_encoding

        with patch("gac.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  output  ", stderr="")
            result = run_subprocess_with_encoding(["test"], "utf-8", strip_output=False)
            assert result == "  output  "

    def test_run_subprocess_with_encoding_silent(self):
        """When silent=True, don't log debug messages."""
        from gac.utils import run_subprocess_with_encoding

        with patch("gac.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
            result = run_subprocess_with_encoding(["test"], "utf-8", silent=True)
            assert result == "output"


class TestSSLVerification:
    """Test SSL verification utility functions."""

    def test_get_ssl_verify_default(self):
        """Default is True (verify SSL)."""
        from gac.utils import get_ssl_verify

        with patch.dict("os.environ", {}, clear=False):
            # Remove any GAC_NO_VERIFY_SSL
            os_env = dict(os.environ)
            os_env.pop("GAC_NO_VERIFY_SSL", None)
            with patch.dict("os.environ", os_env, clear=True):
                result = get_ssl_verify()
                assert result is True

    def test_should_skip_ssl_verification_enabled(self):
        """When GAC_NO_VERIFY_SSL=true, should skip."""
        from gac.utils import should_skip_ssl_verification

        with patch.dict("os.environ", {"GAC_NO_VERIFY_SSL": "true"}):
            assert should_skip_ssl_verification() is True

    def test_should_skip_ssl_verification_disabled(self):
        """When GAC_NO_VERIFY_SSL=false, should not skip."""
        from gac.utils import should_skip_ssl_verification

        with patch.dict("os.environ", {"GAC_NO_VERIFY_SSL": "false"}):
            assert should_skip_ssl_verification() is False
