"""Tests to close coverage gaps in git.py.

Targeting uncovered lines:
- Lines 40-71: run_subprocess_with_encoding_fallback (encoding errors, subprocess errors, all-failed)
- Line 139: get_staged_status with malformed line (< 2 tab-separated parts)
- Lines 172->176: get_diff exception path (SubprocessError etc.)
- Lines 346-370, 363-364: detect_rename_mappings edge cases
"""

import subprocess
from unittest.mock import patch

import pytest

from gac.errors import GitError
from gac.git import (
    detect_rename_mappings,
    get_diff,
    get_staged_status,
    run_subprocess_with_encoding_fallback,
)

# ── Lines 40-71: run_subprocess_with_encoding_fallback ──────────────


class TestRunSubprocessWithEncodingFallback:
    """Test encoding fallback paths in run_subprocess_with_encoding_fallback."""

    def test_unicode_error_tries_next_encoding(self):
        """UnicodeError should cause fallback to next encoding."""
        with patch("gac.utils.get_safe_encodings", return_value=["bad-enc", "utf-8"]):
            with patch("subprocess.run") as mock_run:
                # First call raises UnicodeError, second succeeds
                mock_run.side_effect = [
                    UnicodeError("bad encoding"),
                    subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr=""),
                ]
                result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=True)
                assert result.returncode == 0
                assert mock_run.call_count == 2

    def test_subprocess_error_tries_next_encoding(self):
        """SubprocessError should cause fallback to next encoding."""
        with patch("gac.utils.get_safe_encodings", return_value=["utf-8", "utf-8"]):
            with patch("subprocess.run") as mock_run:
                # First call raises OSError, second succeeds
                mock_run.side_effect = [
                    OSError("command not found"),
                    subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr=""),
                ]
                result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=True)
                assert result.returncode == 0
                assert mock_run.call_count == 2

    def test_timeout_expired_is_reraised(self):
        """TimeoutExpired should NOT be caught — it should propagate."""
        with patch("gac.utils.get_safe_encodings", return_value=["utf-8"]):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo", timeout=5)
                with pytest.raises(subprocess.TimeoutExpired):
                    run_subprocess_with_encoding_fallback(["echo", "test"])

    def test_all_encodings_failed_raises(self):
        """When all encodings fail, should raise CalledProcessError."""
        with patch("gac.utils.get_safe_encodings", return_value=["enc1", "enc2"]):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = UnicodeError("bad")
                with pytest.raises(subprocess.CalledProcessError) as exc_info:
                    run_subprocess_with_encoding_fallback(["echo", "test"], silent=True)
                assert "Encoding error" in exc_info.value.stderr

    def test_all_encodings_failed_no_exception(self):
        """When all encodings fail with no last_exception, should still raise CalledProcessError."""
        # This is a contrived case but covers the else branch
        with patch("gac.utils.get_safe_encodings", return_value=[]):
            with pytest.raises(subprocess.CalledProcessError) as exc_info:
                run_subprocess_with_encoding_fallback(["echo", "test"], silent=True)
            assert "All encoding attempts failed" in exc_info.value.stderr

    def test_silent_mode_no_logging(self):
        """Silent mode should suppress debug logging."""
        with patch("gac.utils.get_safe_encodings", return_value=["utf-8"]):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr="")
                with patch("gac.git.logger") as mock_logger:
                    result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=True)
                    assert result.returncode == 0
                    mock_logger.debug.assert_not_called()

    def test_non_silent_mode_logs_debug(self):
        """Non-silent mode should log debug messages."""
        with patch("gac.utils.get_safe_encodings", return_value=["utf-8"]):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr="")
                with patch("gac.git.logger") as mock_logger:
                    result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=False)
                    assert result.returncode == 0
                    mock_logger.debug.assert_called()

    def test_unicode_error_non_silent_logs(self):
        """UnicodeError in non-silent mode should log the error."""
        with patch("gac.utils.get_safe_encodings", return_value=["bad-enc", "utf-8"]):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    UnicodeError("bad encoding"),
                    subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr=""),
                ]
                with patch("gac.git.logger") as mock_logger:
                    result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=False)
                    assert result.returncode == 0
                    # Should have logged about the failed encoding
                    assert mock_logger.debug.call_count >= 2

    def test_subprocess_error_non_silent_logs(self):
        """SubprocessError in non-silent mode should log the error."""
        with patch("gac.utils.get_safe_encodings", return_value=["utf-8", "utf-8"]):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    OSError("command error"),
                    subprocess.CompletedProcess(args=["test"], returncode=0, stdout="ok", stderr=""),
                ]
                with patch("gac.git.logger") as mock_logger:
                    result = run_subprocess_with_encoding_fallback(["echo", "test"], silent=False)
                    assert result.returncode == 0
                    # Should have logged about the command error
                    assert mock_logger.debug.call_count >= 2


# ── Line 139: get_staged_status with malformed line ─────────────────


class TestGetStagedStatusMalformedLine:
    """Test get_staged_status with various malformed input lines."""

    def test_malformed_line_skipped(self):
        """Lines with fewer than 2 tab-separated parts should be skipped."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "M\tfile1.py\nmalformed_line\nA\tfile2.py"
            result = get_staged_status()
            assert "file1.py" in result
            assert "file2.py" in result
            assert "malformed_line" not in result

    def test_empty_lines_skipped(self):
        """Empty lines should be skipped."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "M\tfile1.py\n\nA\tfile2.py"
            result = get_staged_status()
            assert "file1.py" in result
            assert "file2.py" in result

    def test_unknown_change_type_uses_modified(self):
        """Unknown change type characters should default to 'modified'."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "X\tunknown_file.py"
            result = get_staged_status()
            assert "modified:   unknown_file.py" in result


# ── Lines 172->176: get_diff exception path ────────────────────────


class TestGetDiffExceptionPath:
    """Test get_diff when git command raises subprocess errors."""

    def test_subprocess_error_raises_git_error(self):
        """SubprocessError should be converted to GitError."""
        from gac.git import get_diff

        with patch("gac.git.run_git_command") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("git failed")
            with pytest.raises(GitError, match="Failed to get diff"):
                get_diff(staged=True)

    def test_os_error_raises_git_error(self):
        """OSError should be converted to GitError."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.side_effect = OSError("no such file")
            with pytest.raises(GitError, match="Failed to get diff"):
                get_diff(staged=True)

    def test_filenotfound_error_raises_git_error(self):
        """FileNotFoundError should be converted to GitError."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            with pytest.raises(GitError, match="Failed to get diff"):
                get_diff(staged=True)

    def test_successful_diff_with_commits(self):
        """get_diff with commit1 and commit2 should pass them correctly."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "diff content"
            get_diff(commit1="abc123", commit2="def456")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "abc123" in args
            assert "def456" in args

    def test_successful_diff_with_single_commit(self):
        """get_diff with only commit1 should compare working tree to that commit."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "diff content"
            get_diff(commit1="abc123")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "abc123" in args

    def test_diff_no_color(self):
        """get_diff with color=False should not include --color."""
        with patch("gac.git.run_git_command") as mock_run:
            mock_run.return_value = "diff content"
            get_diff(staged=True, color=False)
            args = mock_run.call_args[0][0]
            assert "--color" not in args


# ── Lines 346-370, 363-364: detect_rename_mappings edge cases ───────


class TestDetectRenameMappingsEdgeCases:
    """Test detect_rename_mappings with tricky diff formats."""

    def test_diff_header_without_b_slash_uses_rename_lines(self):
        """Even with a malformed header, rename from/to lines provide unambiguous paths."""
        diff = "diff --git a/file.txt\nsimilarity index 100%\nrename from file.txt\nrename to new_file.txt"
        mappings = detect_rename_mappings(diff)
        # rename from/to lines are authoritative regardless of header
        assert mappings == {"new_file.txt": "file.txt"}

    def test_diff_header_without_b_slash_no_rename_lines(self):
        """Malformed header with no rename lines should produce no mapping."""
        diff = "diff --git a/file.txt\nsimilarity index 100%"
        mappings = detect_rename_mappings(diff)
        # No rename lines, header has no ' b/' separator — fallback rfind fails too
        assert mappings == {}

    def test_rename_with_similarity_but_no_b_in_header(self):
        """Similarity index without rename from/to lines produces no mapping."""
        diff = "diff --git a/file.txt\nsimilarity index 100%"
        mappings = detect_rename_mappings(diff)
        # No rename from/to → can't determine paths unambiguously
        assert mappings == {}

    def test_similarity_index_without_rename_lines_no_mapping(self):
        """When only similarity index is present (no rename from/to), no mapping is produced.

        Header parsing is fundamentally ambiguous when paths contain ' a/' or ' b/',
        so we only produce mappings from rename from/to lines.
        """
        diff = "diff --git a/old.py b/new.py\nsimilarity index 100%"
        mappings = detect_rename_mappings(diff)
        assert mappings == {}

    def test_header_with_b_in_new_path_no_rename_lines(self):
        """New path containing ' b/' without rename lines produces no mapping.

        Previously the rfind(' b/') fallback would misparse this header,
        splitting at the wrong ' b/' and producing a bogus mapping.
        """
        diff = "diff --git a/old.py b/new b/new.py\nsimilarity index 100%"
        mappings = detect_rename_mappings(diff)
        assert mappings == {}

    def test_rename_with_rename_from_line(self):
        """Rename detected via 'rename from' line instead of 'similarity index'."""
        diff = "diff --git a/old.py b/new.py\nrename from old.py\nrename to new.py"
        mappings = detect_rename_mappings(diff)
        assert "new.py" in mappings
        assert mappings["new.py"] == "old.py"

    def test_no_rename_when_old_equals_new(self):
        """When old_path == new_path, should NOT create a rename mapping."""
        diff = "diff --git a/file.py b/file.py\nsimilarity index 100%\nrename from file.py\nrename to file.py"
        mappings = detect_rename_mappings(diff)
        # old_path == new_path, so no mapping
        assert mappings == {}

    def test_diff_without_rename_markers(self):
        """Regular diff without rename markers should return empty."""
        diff = "diff --git a/src/main.py b/src/main.py\nindex abc..def 100644\n+new line"
        mappings = detect_rename_mappings(diff)
        assert mappings == {}

    def test_rename_with_nested_paths(self):
        """Rename with directory components in paths."""
        diff = "diff --git a/src/old_module.py b/src/new_module.py\nsimilarity index 95%\nrename from src/old_module.py\nrename to src/new_module.py"
        mappings = detect_rename_mappings(diff)
        assert "src/new_module.py" in mappings
        assert mappings["src/new_module.py"] == "src/old_module.py"

    def test_diff_header_with_a_in_path(self):
        """Paths containing ' a/' should be parsed correctly via rename lines."""
        diff = "diff --git a/path a/file.py b/path b/new_file.py\nsimilarity index 100%\nrename from path a/file.py\nrename to path b/new_file.py"
        mappings = detect_rename_mappings(diff)
        # rename from/to lines are unambiguous regardless of header content
        assert mappings == {"path b/new_file.py": "path a/file.py"}

    def test_diff_header_with_b_in_old_path(self):
        """Old path containing ' b/' should be parsed correctly via rename lines."""
        diff = (
            "diff --git a/path b/file.py b/new.py\nsimilarity index 100%\nrename from path b/file.py\nrename to new.py"
        )
        mappings = detect_rename_mappings(diff)
        assert mappings == {"new.py": "path b/file.py"}

    def test_rename_with_b_in_new_path_via_rename_lines(self):
        """New path containing ' b/' is parsed correctly via rename from/to lines."""
        diff = "diff --git a/old.py b/new b/new.py\nsimilarity index 100%\nrename from old.py\nrename to new b/new.py"
        mappings = detect_rename_mappings(diff)
        assert mappings == {"new b/new.py": "old.py"}
