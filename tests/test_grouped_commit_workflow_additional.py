"""Simple targeted tests to improve grouped_commit_workflow.py coverage.

Focuses on high-impact missing areas with minimal mocking.
"""

from unittest import mock

from gac.config import GACConfig
from gac.errors import GitError
from gac.grouped_commit_workflow import GroupedCommitResult, GroupedCommitWorkflow


def test_display_quiet_mode():
    """Test that quiet mode suppresses all display output."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=1000):
        with mock.patch("gac.grouped_commit_workflow.console.print") as mock_console:
            workflow.display_grouped_commits(result, "openai:gpt-4", 1000, quiet=True)

            # In quiet mode, no console output should be produced
            mock_console.assert_not_called()


def test_keyboard_interrupt_handling():
    """Test keyboard interrupt handling during commit execution."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.get_staged_files", return_value=[]):
        with mock.patch("gac.grouped_commit_workflow.run_git_command"):
            with mock.patch("gac.grouped_commit_workflow.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_workflow.execute_commit", side_effect=KeyboardInterrupt()):
                    with mock.patch("gac.grouped_commit_workflow.restore_staging") as mock_restore:
                        with mock.patch("gac.grouped_commit_workflow.console.print"):
                            exit_code = workflow.execute_grouped_commits(
                                result=result,
                                dry_run=False,
                                push=False,
                                no_verify=False,
                                hook_timeout=120,
                            )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_oserror_handling():
    """Test OSError handling during commit execution."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.get_staged_files", return_value=[]):
        with mock.patch("gac.grouped_commit_workflow.run_git_command"):
            with mock.patch("gac.grouped_commit_workflow.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_workflow.execute_commit", side_effect=OSError("Permission denied")):
                    with mock.patch("gac.grouped_commit_workflow.restore_staging") as mock_restore:
                        with mock.patch("gac.grouped_commit_workflow.console.print"):
                            exit_code = workflow.execute_grouped_commits(
                                result=result,
                                dry_run=False,
                                push=False,
                                no_verify=False,
                                hook_timeout=120,
                            )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_dry_run_with_push():
    """Test dry run with push enabled shows appropriate message."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.console.print") as mock_console:
        exit_code = workflow.execute_grouped_commits(
            result=result,
            dry_run=True,
            push=True,
            no_verify=False,
            hook_timeout=120,
        )

    assert exit_code == 0
    console_calls = [str(call) for call in mock_console.call_args_list]
    assert any("Dry run: Would push changes" in call for call in console_calls)


def test_dry_run_multiple_commits():
    """Test dry run with multiple commits shows all previews."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[
            {"files": ["file1.py"], "message": "First commit"},
            {"files": ["file2.py"], "message": "Second commit"},
        ],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.console.print") as mock_console:
        exit_code = workflow.execute_grouped_commits(
            result=result,
            dry_run=True,
            push=False,
            no_verify=False,
            hook_timeout=120,
        )

    assert exit_code == 0
    console_calls = [str(call) for call in mock_console.call_args_list]
    assert any("Dry run: Would create 2 commits" in call for call in console_calls)
    assert any("Commit 1/2:" in call for call in console_calls)
    assert any("Commit 2/2:" in call for call in console_calls)


def test_conversation_state_preservation():
    """Test that conversation state is preserved across retries."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    conversation_messages = [
        {"role": "system", "content": "Custom system prompt"},
        {"role": "user", "content": "Generate commits"},
    ]

    with mock.patch("gac.grouped_commit_workflow.check_token_warning", return_value=True):
        with mock.patch("gac.grouped_commit_workflow.generate_grouped_commits") as mock_generate:
            with mock.patch("gac.grouped_commit_workflow.get_staged_files", return_value=[]):
                # First call fails, second succeeds
                mock_generate.side_effect = [
                    "Invalid JSON",
                    '{"commits": [{"files": ["file1.py"], "message": "Fixed"}]}',
                ]

                staged_files_set = {"file1.py"}

                result = workflow.generate_grouped_commits_with_retry(
                    model="openai:gpt-4",
                    conversation_messages=conversation_messages,
                    temperature=0.7,
                    max_output_tokens=1000,
                    max_retries=3,
                    quiet=True,
                    staged_files_set=staged_files_set,
                    require_confirmation=True,
                )

    assert isinstance(result, GroupedCommitResult)
    # Should preserve original system message
    assert conversation_messages[0]["content"] == "Custom system prompt"


def test_model_identifier_different_formats():
    """Test display with different model identifier formats."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=1000):
        with mock.patch("gac.grouped_commit_workflow.console.print") as mock_console:
            # Test various model formats to ensure ModelIdentifier parsing works
            model_formats = ["openai:gpt-4", "anthropic:claude-3", "local:llama-2"]

            for model in model_formats:
                mock_console.reset_mock()
                workflow.display_grouped_commits(result, model, 1000, quiet=False)

                # Should not raise any exceptions for different formats
                assert mock_console.call_count > 0


def test_display_single_vs_multiple_commits():
    """Test display logic for single vs multiple commits."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    with mock.patch("gac.grouped_commit_workflow.count_tokens", return_value=1000):
        with mock.patch("gac.grouped_commit_workflow.console.print") as mock_console:
            # Test single commit
            single_result = GroupedCommitResult(
                commits=[{"files": ["file1.py"], "message": "Single commit"}],
                raw_response="test response",
            )
            workflow.display_grouped_commits(single_result, "openai:gpt-4", 1000, quiet=False)

            # Test multiple commits
            mock_console.reset_mock()
            multi_result = GroupedCommitResult(
                commits=[
                    {"files": ["file1.py"], "message": "First commit"},
                    {"files": ["file2.py"], "message": "Second commit"},
                ],
                raw_response="test response",
            )
            workflow.display_grouped_commits(multi_result, "openai:gpt-4", 1000, quiet=False)

            # Should have been called for multiple commits
            assert mock_console.call_count > 0


def test_push_failure_triggers_restore():
    """Test that push failure triggers staging restore."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[{"files": ["file1.py"], "message": "Test commit"}],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.get_staged_files", return_value=[]):
        with mock.patch("gac.grouped_commit_workflow.run_git_command"):
            with mock.patch("gac.grouped_commit_workflow.detect_rename_mappings", return_value={}):
                with mock.patch("gac.grouped_commit_workflow.execute_commit"):
                    with mock.patch("gac.git.push_changes", return_value=False):
                        with mock.patch("gac.grouped_commit_workflow.restore_staging") as mock_restore:
                            with mock.patch("gac.grouped_commit_workflow.console.print"):
                                exit_code = workflow.execute_grouped_commits(
                                    result=result,
                                    dry_run=False,
                                    push=True,
                                    no_verify=False,
                                    hook_timeout=120,
                                )

    assert exit_code == 1
    mock_restore.assert_called_once()


def test_multiple_commit_failures():
    """Test multiple commit failures with proper rollback."""
    config = GACConfig({"warning_limit_tokens": 4096})
    workflow = GroupedCommitWorkflow(config)

    result = GroupedCommitResult(
        commits=[
            {"files": ["file1.py"], "message": "Commit 1"},
            {"files": ["file2.py"], "message": "Commit 2"},  # This will fail
            {"files": ["file3.py"], "message": "Commit 3"},  # Should not be reached
        ],
        raw_response="test response",
    )

    with mock.patch("gac.grouped_commit_workflow.get_staged_files", return_value=[]):
        with mock.patch("gac.grouped_commit_workflow.run_git_command"):
            with mock.patch("gac.grouped_commit_workflow.detect_rename_mappings", return_value={}):
                commit_call_count = 0

                def fail_on_second(*args, **kwargs):
                    nonlocal commit_call_count
                    commit_call_count += 1
                    if commit_call_count == 2:
                        raise GitError("Commit failed")  # Use proper exception type

                with mock.patch("gac.grouped_commit_workflow.execute_commit", side_effect=fail_on_second):
                    with mock.patch("gac.grouped_commit_workflow.restore_staging") as mock_restore:
                        with mock.patch("gac.grouped_commit_workflow.console.print"):
                            exit_code = workflow.execute_grouped_commits(
                                result=result,
                                dry_run=False,
                                push=False,
                                no_verify=False,
                                hook_timeout=120,
                            )

    assert exit_code == 1
    mock_restore.assert_called_once()
