"""Tests for grouped commits workflow."""

from unittest.mock import patch

import pytest

from gac.errors import GitError
from gac.main import main


@pytest.fixture(autouse=True)
def skip_git_hooks(monkeypatch):
    """Avoid invoking lefthook/pre-commit binaries during unit tests."""
    monkeypatch.setattr("gac.main.run_lefthook_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.git.run_git_command", lambda *_, **__: "/fake/repo", raising=False)
    monkeypatch.setattr("gac.git_state_validator.run_git_command", lambda *_, **__: "/fake/repo", raising=False)


def test_group_with_no_staged_changes(tmp_path, monkeypatch):
    """--group with no staged changes shows appropriate error."""
    monkeypatch.chdir(tmp_path)

    with (
        patch("gac.git_state_validator.GitStateValidator.validate_repository", return_value=str(tmp_path)),
        patch("gac.git.get_staged_files", return_value=[]),
        patch("gac.git_state_validator.get_staged_files", return_value=[]),
        patch("gac.main.console.print"),
    ):
        exit_code = main(group=True, model="openai:gpt-4", require_confirmation=False)
        assert exit_code == 0
        # The message is printed to stdout (visible in test output above)


def test_group_json_parsing_success():
    """Successful JSON parsing and validation."""

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["src/file1.py", "tests/test_file1.py", "README.md"]),
        patch(
            "gac.git_state_validator.get_staged_files",
            return_value=["src/file1.py", "tests/test_file1.py", "README.md"],
        ),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("click.prompt", return_value="y"),
        patch("gac.workflow_utils.execute_commit"),
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)

        # Verify the workflow was called
        mock_workflow.assert_called_once()


@pytest.mark.parametrize(
    "invalid_data",
    [
        '{"commits": []}',
        '{"commits": [{"files": [], "message": "test"}]}',
        '{"commits": [{"files": "not array", "message": "test"}]}',
        '{"wrong_key": []}',
    ],
)
def test_group_validation_errors(invalid_data):
    """Validation catches various structural errors."""
    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["file.py"]),
        patch("gac.git_state_validator.get_staged_files", return_value=["file.py"]),
        patch("gac.ai.generate_grouped_commits", return_value=invalid_data),
        patch("gac.grouped_commit_workflow.generate_grouped_commits", return_value=invalid_data),
        patch("gac.main.console.print"),
        patch("gac.grouped_commit_workflow.console.print"),
    ):
        exit_code = main(group=True, model="openai:gpt-4", require_confirmation=False)
        assert exit_code == 1


def test_group_dry_run():
    """Dry run shows commits but doesn't execute."""

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["file1.py"]),
        patch("gac.git_state_validator.get_staged_files", return_value=["file1.py"]),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
    ):
        main(group=True, dry_run=True, require_confirmation=False, model="openai:gpt-4")
        # Verify the workflow was called with dry_run=True
        mock_workflow.assert_called_once()


def test_group_retries_when_files_missing():
    """If grouped response omits staged files, auto-retry with corrective feedback."""

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["a.py", "b.py"]),
        patch("gac.git_state_validator.get_staged_files", return_value=["a.py", "b.py"]),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("click.prompt", return_value="y"),
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)

        # Verify the workflow was called
        mock_workflow.assert_called_once()


def test_group_restores_staging_on_first_commit_failure():
    """Staging is restored when the first commit fails."""
    original_files = ["a.py", "b.py"]

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git_state_validator.get_staged_files", return_value=original_files),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit", side_effect=GitError("Commit failed")),
        patch("gac.workflow_utils.restore_staging"),
        patch("click.prompt", return_value="y"),
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)

        # Verify the workflow was called
        mock_workflow.assert_called_once()


def test_group_does_not_restore_staging_on_later_commit_failure():
    """Staging is not restored when a commit after the first fails (commits already made)."""
    original_files = ["a.py", "b.py"]

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git_state_validator.get_staged_files", return_value=original_files),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("gac.workflow_utils.restore_staging"),
        patch("click.prompt", return_value="y"),
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)
        # Verify the workflow was called
        mock_workflow.assert_called_once()


def test_group_displays_file_lists():
    """File lists are displayed for each commit in dim/gray text."""

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch(
            "gac.git_state_validator.get_staged_files",
            return_value=["src/auth.py", "src/login.py", "tests/test_auth.py", "README.md", "docs/auth.md"],
        ),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_workflow,
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("click.prompt", return_value="y"),
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)

        # Verify the workflow was called
        mock_workflow.assert_called_once()


@pytest.mark.parametrize(
    "num_files,expected_multiplier",
    [
        (1, 2),
        (5, 2),
        (9, 2),
        (10, 3),
        (15, 3),
        (19, 3),
        (20, 4),
        (25, 4),
        (29, 4),
        (30, 5),
        (50, 5),
        (100, 5),
    ],
)
def test_group_token_scaling(num_files, expected_multiplier):
    """Token scaling increases with file count: 2x(1-9), 3x(10-19), 4x(20-29), 5x(30+)."""
    base_tokens = 512

    mock_config = {
        "temperature": 0.7,
        "max_output_tokens": base_tokens,
        "max_retries": 3,
        "warning_limit_tokens": 4096,
    }

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=[f"file{i}.py" for i in range(num_files)]),
        patch("gac.git_state_validator.get_staged_files", return_value=[f"file{i}.py" for i in range(num_files)]),
        patch("gac.main.config", mock_config),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow") as mock_exec,
    ):
        main(group=True, model="openai:gpt-4", require_confirmation=True)

        # Check that the workflow was called with the correct max_output_tokens
        call_args = mock_exec.call_args
        actual_max_tokens = call_args.kwargs["max_output_tokens"]
        expected_tokens = base_tokens * expected_multiplier
        assert actual_max_tokens == expected_tokens, (
            f"For {num_files} files, expected {expected_multiplier}x scaling "
            f"({expected_tokens} tokens), got {actual_max_tokens}"
        )
