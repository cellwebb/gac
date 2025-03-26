"""Test module for gac.core."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from gac.core import (
    commit_changes,
    get_existing_staged_python_files,
    get_staged_files,
    get_staged_python_files,
    main,
    run_black,
    run_subprocess,
    stage_files,
)
from gac.git import (
    git_commit_changes,
    git_get_existing_staged_python_files,
    git_get_staged_files,
    git_get_staged_python_files,
    git_stage_files,
)


class TestCore(unittest.TestCase):
    """Tests for core functions."""

    @patch("gac.utils.subprocess.run")
    def test_run_subprocess_success(self, mock_run):
        """Test run_subprocess when command succeeds."""
        # Mock subprocess.run to return a success result
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Command output"
        mock_run.return_value = mock_process

        # Call run_subprocess
        result = run_subprocess(["git", "status"])

        # Assert mock was called correctly
        mock_run.assert_called_once_with(
            ["git", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Assert result matches mock stdout
        self.assertEqual(result, "Command output")

    @patch("gac.utils.subprocess.run")
    def test_run_subprocess_failure(self, mock_run):
        """Test run_subprocess when command fails."""
        # Mock subprocess.run to return a failure result
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Command failed"
        mock_run.return_value = mock_process

        # Call run_subprocess and expect exception
        with self.assertRaises(subprocess.CalledProcessError):
            run_subprocess(["git", "invalid"])

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

    @patch("gac.git.git_get_staged_files")
    def test_get_staged_python_files(self, mock_git_get_staged_files):
        """Test get_staged_python_files returns only Python files."""
        # Mock git_get_staged_files to return mixed file types
        mock_git_get_staged_files.return_value = ["file1.py", "file2.md", "file3.js", "file4.py"]

        # Call get_staged_python_files
        result = get_staged_python_files()

        # Assert only Python files are returned
        self.assertEqual(result, ["file1.py", "file4.py"])

    @patch("os.path.exists")
    @patch("gac.git.git_get_staged_python_files")
    def test_get_existing_staged_python_files(self, mock_git_get_staged_python_files, mock_exists):
        """Test get_existing_staged_python_files returns only existing Python files."""
        # Mock git_get_staged_python_files to return Python files
        mock_git_get_staged_python_files.return_value = ["file1.py", "file2.py", "file3.py"]

        # Mock os.path.exists to return True for specific files
        mock_exists.side_effect = lambda f: f != "file2.py"  # file2.py doesn't exist

        # Call get_existing_staged_python_files
        result = get_existing_staged_python_files()

        # Assert only existing Python files are returned
        self.assertEqual(result, ["file1.py", "file3.py"])

    @patch("gac.git.run_subprocess")
    def test_commit_changes(self, mock_run_subprocess):
        """Test commit_changes calls git commit with the provided message."""
        # Setup mock to avoid actual git command execution
        mock_run_subprocess.return_value = "Commit successful"

        # Call commit_changes
        commit_changes("Test commit message")

        # Assert git commit was called with the message
        mock_run_subprocess.assert_called_once_with(["git", "commit", "-m", "Test commit message"])

    @patch("gac.git.run_subprocess")
    def test_stage_files(self, mock_run_subprocess):
        """Test stage_files calls git add with the provided files."""
        # Setup mock
        mock_run_subprocess.return_value = "Files staged"

        # Call stage_files
        stage_files(["file1.py", "file2.py"])

        # Assert git add was called with the files
        mock_run_subprocess.assert_called_once_with(["git", "add", "file1.py", "file2.py"])

    @patch("gac.core.get_existing_staged_python_files")
    @patch("gac.core.run_subprocess")
    def test_run_black(self, mock_run_subprocess, mock_get_existing_staged_python_files):
        """Test run_black runs black on Python files."""
        # Mock get_existing_staged_python_files to return Python files
        mock_get_existing_staged_python_files.return_value = ["file1.py", "file2.py"]

        # Mock run_subprocess to avoid actual command execution
        mock_run_subprocess.return_value = ""

        # Call run_black
        result = run_black()

        # Assert black was called with the Python files
        mock_run_subprocess.assert_called_with(["black", "file1.py", "file2.py"])

        # Assert result is True
        self.assertTrue(result)

    @patch("gac.core.get_config")
    @patch("gac.core.get_staged_files")
    @patch("gac.core.send_to_llm")
    @patch("gac.core.run_subprocess")
    @patch("gac.core.stage_files")
    @patch("gac.core.commit_changes")
    @patch("click.prompt")
    @patch("builtins.print")
    def test_main_test_mode(
        self,
        mock_print,
        mock_prompt,
        mock_commit_changes,
        mock_stage_files,
        mock_run_subprocess,
        mock_send_to_llm,
        mock_get_staged_files,
        mock_get_config,
    ):
        """Test main in test mode."""
        # Setup mocks
        mock_get_config.return_value = {"model": "anthropic:claude-3-haiku", "use_formatting": True}
        mock_get_staged_files.return_value = ["file1.py"]
        mock_prompt.return_value = "y"  # Mock user confirming the commit

        # Call main in test mode
        result = main(test_mode=True)

        # Assert LLM was not called
        mock_send_to_llm.assert_not_called()

        # Assert commit was not made
        mock_commit_changes.assert_not_called()

        # Assert test message was returned
        self.assertTrue(result.startswith("[TEST MESSAGE]"))

    @patch("gac.core.get_config")
    @patch("gac.core.get_staged_files")
    @patch("gac.core.get_staged_python_files")
    @patch("gac.core.get_existing_staged_python_files")
    @patch("gac.core.run_black")
    @patch("gac.core.run_isort")
    @patch("gac.core.stage_files")
    @patch("gac.core.send_to_llm")
    @patch("gac.core.commit_changes")
    @patch("gac.core.run_subprocess")
    @patch("click.prompt")
    @patch("builtins.print")
    def test_main_normal_flow(
        self,
        mock_print,
        mock_prompt,
        mock_run_subprocess,
        mock_commit_changes,
        mock_send_to_llm,
        mock_stage_files,
        mock_run_isort,
        mock_run_black,
        mock_get_existing_staged_python_files,
        mock_get_staged_python_files,
        mock_get_staged_files,
        mock_get_config,
    ):
        """Test main with normal flow with formatting."""
        # Setup mocks
        mock_get_config.return_value = {"model": "anthropic:claude-3-haiku", "use_formatting": True}
        mock_get_staged_files.return_value = ["file1.py"]
        mock_get_staged_python_files.return_value = ["file1.py"]
        mock_get_existing_staged_python_files.return_value = ["file1.py"]
        mock_run_black.return_value = True
        mock_run_isort.return_value = True
        mock_send_to_llm.return_value = "Generated commit message"
        mock_prompt.return_value = "y"  # Mock user confirming the commit

        # Call main
        result = main()

        # Assert formatting was run
        mock_run_black.assert_called_once()
        mock_run_isort.assert_called_once()

        # Assert files were re-staged after formatting
        self.assertEqual(mock_stage_files.call_count, 2)  # Once after black, once after isort

        # Assert LLM was called
        mock_send_to_llm.assert_called_once()

        # Assert commit was made with the generated message
        mock_commit_changes.assert_called_once_with("Generated commit message")

        # Assert git push was called
        for call_args in mock_run_subprocess.call_args_list:
            if call_args[0][0] == ["git", "push"]:
                break
        else:
            self.fail("git push was not called")

        # Assert message was returned
        self.assertEqual(result, "Generated commit message")

    @patch("gac.core.get_config")
    @patch("gac.core.get_staged_files")
    @patch("gac.core.get_staged_python_files")
    @patch("gac.core.get_existing_staged_python_files")
    @patch("gac.core.run_black")
    @patch("gac.core.run_isort")
    @patch("gac.core.stage_files")
    @patch("gac.core.send_to_llm")
    @patch("gac.core.commit_changes")
    @patch("gac.core.run_subprocess")
    @patch("click.prompt")
    @patch("builtins.print")
    def test_main_no_push(
        self,
        mock_print,
        mock_prompt,
        mock_run_subprocess,
        mock_commit_changes,
        mock_send_to_llm,
        mock_stage_files,
        mock_run_isort,
        mock_run_black,
        mock_get_existing_staged_python_files,
        mock_get_staged_python_files,
        mock_get_staged_files,
        mock_get_config,
    ):
        """Test main when user declines to push."""
        # Setup mocks
        mock_get_config.return_value = {"model": "anthropic:claude-3-haiku", "use_formatting": True}
        mock_get_staged_files.return_value = ["file1.py"]
        mock_get_staged_python_files.return_value = ["file1.py"]
        mock_get_existing_staged_python_files.return_value = ["file1.py"]
        mock_run_black.return_value = True
        mock_run_isort.return_value = True
        mock_send_to_llm.return_value = "Generated commit message"
        mock_prompt.side_effect = ["y", "n"]  # Mock user confirming commit but declining push

        # Call main
        result = main()

        # Assert formatting was run
        mock_run_black.assert_called_once()
        mock_run_isort.assert_called_once()

        # Assert commit was made
        mock_commit_changes.assert_called_once_with("Generated commit message")

        # Assert git push was not called
        for call_args in mock_run_subprocess.call_args_list:
            self.assertNotEqual(call_args[0][0], ["git", "push"])

        # Assert message was returned
        self.assertEqual(result, "Generated commit message")

    @patch("gac.git.run_subprocess")
    def test_git_commit_changes(self, mock_run_subprocess):
        """Test git_commit_changes calls git commit with the provided message."""
        # Setup mock to avoid actual git command execution
        mock_run_subprocess.return_value = ""

        # Call git_commit_changes
        git_commit_changes("Test commit message")

        # Assert git commit was called with the message
        mock_run_subprocess.assert_called_once_with(["git", "commit", "-m", "Test commit message"])

    @patch("gac.git.run_subprocess")
    def test_git_get_staged_files(self, mock_run_subprocess):
        """Test git_get_staged_files returns correct result."""
        # Mock run_subprocess to return staged files
        mock_run_subprocess.return_value = "file1.py\nfile2.md\nfile3.js"

        # Call git_get_staged_files
        result = git_get_staged_files()

        # Assert mock was called correctly
        mock_run_subprocess.assert_called_once_with(["git", "diff", "--staged", "--name-only"])

        # Assert result is list of files
        self.assertEqual(result, ["file1.py", "file2.md", "file3.js"])

    @patch("gac.git.git_get_staged_files")
    def test_git_get_staged_python_files(self, mock_git_get_staged_files):
        """Test git_get_staged_python_files returns only Python files."""
        # Mock git_get_staged_files to return mixed file types
        mock_git_get_staged_files.return_value = ["file1.py", "file2.md", "file3.js", "file4.py"]

        # Call git_get_staged_python_files
        result = git_get_staged_python_files()

        # Assert result is list of Python files
        self.assertEqual(result, ["file1.py", "file4.py"])

    @patch("os.path.exists")
    @patch("gac.git.git_get_staged_python_files")
    def test_git_get_existing_staged_python_files(
        self, mock_git_get_staged_python_files, mock_exists
    ):
        """Test git_get_existing_staged_python_files returns only existing Python files."""
        # Mock git_get_staged_python_files to return Python files
        mock_git_get_staged_python_files.return_value = ["file1.py", "file2.py", "file3.py"]

        # Mock os.path.exists to return True for specific files
        mock_exists.side_effect = lambda f: f != "file2.py"  # file2.py doesn't exist

        # Call git_get_existing_staged_python_files
        result = git_get_existing_staged_python_files()

        # Assert result is list of existing Python files
        self.assertEqual(result, ["file1.py", "file3.py"])

    @patch("gac.git.run_subprocess")
    def test_git_stage_files(self, mock_run_subprocess):
        """Test git_stage_files calls git add with the provided files."""
        # Setup mock
        mock_run_subprocess.return_value = ""

        # Call git_stage_files
        git_stage_files(["file1.py", "file2.py"])

        # Assert git add was called with the files
        mock_run_subprocess.assert_called_once_with(["git", "add", "file1.py", "file2.py"])


if __name__ == "__main__":
    unittest.main()
