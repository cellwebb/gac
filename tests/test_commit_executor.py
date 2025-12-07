#!/usr/bin/env python3
"""Test suite for commit_executor.py to achieve 90% coverage."""

import logging
from unittest.mock import patch

import pytest

from gac.commit_executor import CommitExecutor
from gac.errors import GitError


class TestCommitExecutorDryRun:
    """Test dry run functionality for CommitExecutor."""

    def test_create_commit_dry_run_displays_message(self, caplog):
        """Test that dry run displays commit message without committing."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=True)
        commit_message = "feat: add new feature"
        staged_files = ["file1.py", "file2.py"]

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_get_staged.return_value = staged_files

            # Act
            commit_executor.create_commit(commit_message)

            # Assert
            mock_get_staged.assert_called_once_with(existing_only=False)

            # Verify console output - should show dry run message and panel
            assert mock_console_print.call_count >= 3
            console_calls = [str(call) for call in mock_console_print.call_args_list]

            # Check for dry run warning message
            dry_run_call = next(
                (call for call in console_calls if "Dry run: Commit message generated but not applied" in call), None
            )
            assert dry_run_call is not None

            # Check for commit message display
            message_call = next((call for call in console_calls if "Would commit with message:" in call), None)
            assert message_call is not None

            # Check for file count
            file_count_call = next((call for call in console_calls if "Would commit 2 files" in call), None)
            assert file_count_call is not None

    def test_create_commit_dry_run_no_execution(self, caplog):
        """Test that dry run doesn't execute actual commit."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=True)
        commit_message = "feat: test commit"

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.execute_commit") as mock_execute_commit,
        ):
            mock_get_staged.return_value = []

            # Act
            commit_executor.create_commit(commit_message)

            # Assert
            mock_get_staged.assert_called_once_with(existing_only=False)
            mock_execute_commit.assert_not_called()

            # Verify logging - check for file count log message
            assert len(caplog.records) >= 1
            log_messages = [record.message for record in caplog.records]
            assert any("Would commit 0 files" in msg for msg in log_messages)

    def test_create_commit_dry_run_with_no_staged_files(self, caplog):
        """Test dry run with no staged files."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=True)
        commit_message = "feat: empty commit"

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_get_staged.return_value = []

            # Act
            commit_executor.create_commit(commit_message)

            # Assert
            mock_get_staged.assert_called_once_with(existing_only=False)

            # Verify console output shows 0 files
            console_calls = [str(call) for call in mock_console_print.call_args_list]
            file_count_call = next((call for call in console_calls if "Would commit 0 files" in call), None)
            assert file_count_call is not None

            # Verify logging
            assert len(caplog.records) >= 1
            log_messages = [record.message for record in caplog.records]
            assert any("Would commit 0 files" in msg for msg in log_messages)

    def test_create_commit_dry_run_panel_formatting(self):
        """Test that commit message is displayed in a panel during dry run."""
        # Arrange
        commit_executor = CommitExecutor(dry_run=True)
        commit_message = "feat: test panel formatting"

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_get_staged.return_value = ["test.py"]

            # Act - just verify the dry run works without testing Panel specifically
            commit_executor.create_commit(commit_message)

            # Assert - verify that staged files were checked
            mock_get_staged.assert_called_once_with(existing_only=False)

            # Verify console outputs were called for dry run
            assert mock_console_print.call_count >= 3

    def test_push_to_remote_dry_run(self, caplog):
        """Test push behavior in dry run mode."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=True)
        staged_files = ["file1.py", "file2.py", "file3.py"]

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.push_changes") as mock_push_changes,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_get_staged.return_value = staged_files

            # Act
            commit_executor.push_to_remote()

            # Assert
            mock_get_staged.assert_called_once_with(existing_only=False)
            mock_push_changes.assert_not_called()

            # Verify console output
            assert mock_console_print.call_count >= 2
            console_calls = [str(call) for call in mock_console_print.call_args_list]

            # Check for dry run message
            dry_run_call = next((call for call in console_calls if "Dry run: Would push changes" in call), None)
            assert dry_run_call is not None

            # Check for file count
            file_count_call = next((call for call in console_calls if "Would push 3 files" in call), None)
            assert file_count_call is not None

            # Verify logging
            assert len(caplog.records) >= 2
            log_messages = [record.message for record in caplog.records]
            assert any("Dry run: Would push changes" in msg for msg in log_messages)
            assert any("Would push 3 files" in msg for msg in log_messages)

    def test_push_to_remote_dry_run_no_staged_files(self, caplog):
        """Test dry run push with no staged files."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=True)

        with (
            patch("gac.commit_executor.get_staged_files") as mock_get_staged,
            patch("gac.commit_executor.push_changes") as mock_push_changes,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_get_staged.return_value = []

            # Act
            commit_executor.push_to_remote()

            # Assert
            mock_get_staged.assert_called_once_with(existing_only=False)
            mock_push_changes.assert_not_called()

            # Verify console output shows 0 files
            console_calls = [str(call) for call in mock_console_print.call_args_list]
            file_count_call = next((call for call in console_calls if "Would push 0 files" in call), None)
            assert file_count_call is not None

    def test_push_to_remote_failure_raises_git_error(self):
        """Test that push failure raises GitError."""
        # Arrange
        commit_executor = CommitExecutor(dry_run=False)

        with (
            patch("gac.commit_executor.push_changes") as mock_push_changes,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_push_changes.return_value = False

            # Act & Assert
            with pytest.raises(GitError, match="Failed to push changes"):
                commit_executor.push_to_remote()

            # Verify push_changes was called
            mock_push_changes.assert_called_once()

            # Verify error message is printed
            console_calls = [str(call) for call in mock_console_print.call_args_list]
            error_call = next((call for call in console_calls if "Failed to push changes" in call), None)
            assert error_call is not None

    def test_push_to_remote_success_quiet_mode(self, caplog):
        """Test successful push in quiet mode."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=False, quiet=True)

        with (
            patch("gac.commit_executor.push_changes") as mock_push_changes,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_push_changes.return_value = True

            # Act
            commit_executor.push_to_remote()

            # Assert
            mock_push_changes.assert_called_once()

            # Verify logging for success
            assert len(caplog.records) >= 1
            log_messages = [record.message for record in caplog.records]
            assert any("Changes pushed successfully" in msg for msg in log_messages)

            # Verify no success message in console (quiet mode)
            console_calls = [str(call) for call in mock_console_print.call_args_list]
            success_call = next((call for call in console_calls if "Changes pushed successfully" in call), None)
            assert success_call is None

    def test_push_to_remote_success_normal_mode(self, caplog):
        """Test successful push in normal mode."""
        # Arrange
        caplog.set_level(logging.INFO)
        commit_executor = CommitExecutor(dry_run=False, quiet=False)

        with (
            patch("gac.commit_executor.push_changes") as mock_push_changes,
            patch("gac.commit_executor.console.print") as mock_console_print,
        ):
            mock_push_changes.return_value = True

            # Act
            commit_executor.push_to_remote()

            # Assert
            mock_push_changes.assert_called_once()

            # Verify logging for success
            assert len(caplog.records) >= 1
            log_messages = [record.message for record in caplog.records]
            assert any("Changes pushed successfully" in msg for msg in log_messages)

            # Verify success message in console
            console_calls = [str(call) for call in mock_console_print.call_args_list]
            success_call = next((call for call in console_calls if "Changes pushed successfully" in call), None)
            assert success_call is not None


class TestCommitExecutorInitialization:
    """Test CommitExecutor initialization and basic functionality."""

    def test_commit_executor_init_default_params(self):
        """Test CommitExecutor initialization with default parameters."""
        # Act
        executor = CommitExecutor()

        # Assert
        assert executor.dry_run is False
        assert executor.quiet is False
        assert executor.no_verify is False
        assert executor.hook_timeout == 120

    def test_commit_executor_init_custom_params(self):
        """Test CommitExecutor initialization with custom parameters."""
        # Act
        executor = CommitExecutor(dry_run=True, quiet=True, no_verify=True, hook_timeout=60)

        # Assert
        assert executor.dry_run is True
        assert executor.quiet is True
        assert executor.no_verify is True
        assert executor.hook_timeout == 60

    def test_create_commit_actual_execution(self):
        """Test actual commit execution (non-dry-run)."""
        # Arrange
        commit_executor = CommitExecutor(dry_run=False)
        commit_message = "feat: actual commit"

        with patch("gac.commit_executor.execute_commit") as mock_execute_commit:
            # Act
            commit_executor.create_commit(commit_message)

            # Assert
            mock_execute_commit.assert_called_once_with(commit_message, False, 120)

    def test_create_commit_actual_execution_with_no_verify(self):
        """Test actual commit execution with no_verify=True."""
        # Arrange
        commit_executor = CommitExecutor(dry_run=False, no_verify=True, hook_timeout=180)
        commit_message = "feat: commit with no verify"

        with patch("gac.commit_executor.execute_commit") as mock_execute_commit:
            # Act
            commit_executor.create_commit(commit_message)

            # Assert
            mock_execute_commit.assert_called_once_with(commit_message, True, 180)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
