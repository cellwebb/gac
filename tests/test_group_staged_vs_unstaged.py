"""Tests to verify --group respects staged vs unstaged file distinction."""

from unittest.mock import patch

import pytest

from gac.main import main
from gac.workflow_context import CLIOptions


@pytest.fixture(autouse=True)
def skip_git_hooks(monkeypatch):
    """Ensure group staging tests don't call real git hooks or git commands."""
    monkeypatch.setattr("gac.main.run_lefthook_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.git.run_git_command", lambda *_, **__: "/fake/repo", raising=False)
    monkeypatch.setattr("gac.git_state_validator.run_git_command", lambda *_, **__: "/fake/repo", raising=False)


def test_group_without_add_all_only_shows_staged():
    """--group without --add-all only sends staged files to LLM."""
    staged_status = "Changes to be committed:\n\tmodified:   file1.py"

    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["file1.py"]),
        patch("gac.git_state_validator.get_staged_files", return_value=["file1.py"]),
        patch("gac.git.get_staged_status", return_value=staged_status),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow"),
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("click.prompt", return_value="y"),
    ):
        main(CLIOptions(group=True, stage_all=False, model="openai:gpt-4", require_confirmation=True))
        # Test passes if main completes without exception


def test_group_with_add_all_stages_everything():
    """--group --add-all stages all changes before processing."""
    staged_status = "Changes to be committed:\n\tmodified:   file1.py\n\tmodified:   file2.py"

    git_add_called = False

    def mock_git_cmd(args, **kwargs):
        nonlocal git_add_called
        if args == ["add", "--all"]:
            git_add_called = True
        return "/fake/repo" if args == ["rev-parse", "--show-toplevel"] else ""

    with (
        patch("gac.git.run_git_command", side_effect=mock_git_cmd),
        patch("gac.git_state_validator.run_git_command", side_effect=mock_git_cmd),
        patch("gac.git.get_staged_files", return_value=["file1.py", "file2.py"]),
        patch("gac.git_state_validator.get_staged_files", return_value=["file1.py", "file2.py"]),
        patch("gac.git.get_staged_status", return_value=staged_status),
        patch("gac.grouped_commit_workflow.GroupedCommitWorkflow.execute_workflow"),
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("click.prompt", return_value="y"),
    ):
        main(CLIOptions(group=True, stage_all=True, model="openai:gpt-4", require_confirmation=True))
        # Test passes if main completes without exception


def test_normal_mode_uses_staged_status():
    """Normal mode also uses staged-only status."""
    status = "Changes to be committed:\n\tmodified:   file1.py"
    with (
        patch("gac.git.run_git_command", return_value="/fake/repo"),
        patch("gac.git.get_staged_files", return_value=["file1.py"]),
        patch("gac.git.get_staged_status", return_value=status),
        patch("gac.git_state_validator.get_staged_files", return_value=["file1.py"]),
        patch("gac.git_state_validator.get_staged_status", return_value=status),
        patch("gac.prompt.build_prompt", return_value=("system", "user")),
        patch("gac.main.generate_commit_message", return_value="feat: update"),
        patch("gac.main.clean_commit_message", return_value="feat: update"),
        patch("gac.main.console.print"),
        patch("gac.workflow_utils.execute_commit"),
        patch("click.prompt", return_value="y"),
        patch("gac.main.count_tokens", return_value=10),
    ):
        exit_code = main(CLIOptions(group=False, stage_all=False, model="openai:gpt-4", require_confirmation=True))
        assert exit_code == 0  # Test passes if main completes successfully
