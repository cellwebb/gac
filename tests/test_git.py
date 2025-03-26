"""Test module for gac.git."""

import subprocess
import unittest
from unittest.mock import patch

from gac.git import (
    commit_changes,
    get_existing_staged_python_files,
    get_staged_files,
    get_staged_python_files,
    stage_files,
)


class TestGit(unittest.TestCase):
    """Tests for git functions."""

    @patch("gac.git.run_subprocess")
    def test_get_staged_files(self, mock_run_subprocess):
        """Test get_staged_files returns correct result."""
        # Mock run_subprocess to return staged files
        mock_run_subprocess.return_value = "file1.py\nfile2.md\nfile3.js"

        # Call get_staged_files
        result = get_staged_files()

        # Assert mock was called correctly with git diff command
        mock_run_subprocess.assert_called_once_with(["git", "diff", "--staged", "--name-only"])

        # Assert result is list of files
        self.assertEqual(result, ["file1.py", "file2.md", "file3.js"])

    @patch("gac.git.get_staged_files")
    def test_get_staged_python_files(self, mock_get_staged_files):
        """Test get_staged_python_files returns only Python files."""
        # Mock get_staged_files to return mixed file types
        mock_get_staged_files.return_value = ["file1.py", "file2.md", "file3.js", "file4.py"]

        # Call get_staged_python_files
        result = get_staged_python_files()

        # Assert only Python files are returned
        self.assertEqual(result, ["file1.py", "file4.py"])

    @patch("os.path.exists")
    @patch("gac.git.get_staged_python_files")
    def test_get_existing_staged_python_files(self, mock_get_staged_python_files, mock_exists):
        """Test get_existing_staged_python_files returns only existing Python files."""
        # Mock get_staged_python_files to return Python files
        mock_get_staged_python_files.return_value = ["file1.py", "file2.py", "file3.py"]

        # Mock os.path.exists to return True for specific files
        mock_exists.side_effect = lambda f: f != "file2.py"  # file2.py doesn't exist

        # Call get_existing_staged_python_files
        result = get_existing_staged_python_files()

        # Assert only existing Python files are returned
        self.assertEqual(result, ["file1.py", "file3.py"])

    @patch("gac.git.run_subprocess")
    def test_git_commit_changes(self, mock_run_subprocess):
        """Test commit_changes calls git commit with the provided message."""
        # Setup mock to avoid actual git command execution
        mock_run_subprocess.return_value = "Commit successful"

        # Call commit_changes
        commit_changes("Test commit message")

        # Assert git commit was called with the message
        mock_run_subprocess.assert_called_once_with(["git", "commit", "-m", "Test commit message"])

    def test_commit_changes_empty_message(self):
        """Test commit_changes raises ValueError for empty message."""
        # Call commit_changes with empty message and expect ValueError
        with self.assertRaises(ValueError):
            commit_changes("")

    @patch("gac.git.run_subprocess")
    def test_commit_changes_failure(self, mock_run_subprocess):
        """Test commit_changes raises CalledProcessError when git commit fails."""
        # Setup mock to raise CalledProcessError
        mock_run_subprocess.side_effect = subprocess.CalledProcessError(
            1, ["git", "commit"], "Error output"
        )

        # Call commit_changes and expect CalledProcessError
        with self.assertRaises(subprocess.CalledProcessError):
            commit_changes("Test commit message")

    @patch("gac.git.run_subprocess")
    def test_stage_files(self, mock_run_subprocess):
        """Test stage_files calls git add with the provided files."""
        # Setup mock
        mock_run_subprocess.return_value = "Files staged"

        # Call stage_files
        result = stage_files(["file1.py", "file2.py"])

        # Assert git add was called with the files
        mock_run_subprocess.assert_called_once_with(["git", "add", "file1.py", "file2.py"])

        # Assert result is True
        self.assertTrue(result)

    def test_stage_files_empty_list(self):
        """Test stage_files raises ValueError for empty file list."""
        # Call stage_files with empty list and expect ValueError
        with self.assertRaises(ValueError):
            stage_files([])

    @patch("gac.git.run_subprocess")
    def test_stage_files_failure(self, mock_run_subprocess):
        """Test stage_files returns False when git add fails."""
        # Setup mock to raise CalledProcessError
        mock_run_subprocess.side_effect = subprocess.CalledProcessError(
            1, ["git", "add"], "Error output"
        )

        # Call stage_files
        result = stage_files(["file1.py", "file2.py"])

        # Assert result is False
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
