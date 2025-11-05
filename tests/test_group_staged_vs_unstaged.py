"""Tests to verify --group respects staged vs unstaged file distinction."""

import json
from unittest.mock import patch

import pytest

from gac.main import main


@pytest.fixture(autouse=True)
def skip_git_hooks(monkeypatch):
    """Ensure group staging tests don't call real git hooks."""
    monkeypatch.setattr("gac.main.run_lefthook_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_git_command", lambda *_, **__: "/fake/repo", raising=False)


def test_group_without_add_all_only_shows_staged():
    """--group without --add-all only sends staged files to LLM."""
    staged_status = "Changes to be committed:\n\tmodified:   file1.py"
    response = json.dumps({"commits": [{"files": ["file1.py"], "message": "feat: update"}]})

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["file1.py"]),
        patch("gac.main.get_staged_status", return_value=staged_status) as mock_status,
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit"),
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, stage_all=False, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 0
        mock_status.assert_called()


def test_group_with_add_all_stages_everything():
    """--group --add-all stages all changes before processing."""
    staged_status = "Changes to be committed:\n\tmodified:   file1.py\n\tmodified:   file2.py"
    response = json.dumps(
        {
            "commits": [
                {"files": ["file1.py"], "message": "feat: update file1"},
                {"files": ["file2.py"], "message": "fix: update file2"},
            ]
        }
    )

    git_add_called = False

    def mock_git_cmd(args, **kwargs):
        nonlocal git_add_called
        if args == ["add", "--all"]:
            git_add_called = True
        return "/fake/repo" if args == ["rev-parse", "--show-toplevel"] else ""

    with (
        patch("gac.main.run_git_command", side_effect=mock_git_cmd),
        patch("gac.main.get_staged_files", return_value=["file1.py", "file2.py"]),
        patch("gac.main.get_staged_status", return_value=staged_status),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit"),
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, stage_all=True, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 0
        assert git_add_called


def test_normal_mode_uses_staged_status():
    """Normal mode also uses staged-only status."""
    status = "Changes to be committed:\n\tmodified:   file1.py"
    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["file1.py"]),
        patch("gac.main.get_staged_status", return_value=status) as mock_status,
        patch("gac.main.build_prompt", return_value=("system", "user")),
        patch("gac.main.generate_commit_message", return_value="feat: update"),
        patch("gac.main.clean_commit_message", return_value="feat: update"),
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit"),
        patch("gac.main.click.prompt", return_value="y"),
        patch("gac.main.count_tokens", return_value=10),
    ):
        with pytest.raises(SystemExit):
            main(group=False, stage_all=False, model="openai:gpt-4", require_confirmation=True)
        mock_status.assert_called()
