"""Tests for grouped commits workflow."""

import json
from unittest.mock import patch

import pytest

from gac.main import main


def test_group_with_no_staged_changes(tmp_path, monkeypatch):
    """--group with no staged changes shows appropriate error."""
    monkeypatch.chdir(tmp_path)

    with (
        patch("gac.main.run_git_command", return_value=str(tmp_path)),
        patch("gac.main.get_staged_files", return_value=[]),
        patch("gac.main.console.print") as mock_print,
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, require_confirmation=False)
        assert exc.value.code == 0
        assert any("No staged changes" in str(call) for call in mock_print.call_args_list)


def test_group_json_parsing_success():
    """Successful JSON parsing and validation."""
    response = json.dumps(
        {
            "commits": [
                {"files": ["src/file1.py", "tests/test_file1.py"], "message": "feat: add feature 1"},
                {"files": ["README.md"], "message": "docs: update readme"},
            ]
        }
    )

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["src/file1.py", "tests/test_file1.py", "README.md"]),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print"),
        patch("gac.main.click.prompt", return_value="y"),
        patch("gac.main.execute_commit") as mock_commit,
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 0
        assert mock_commit.call_count == 2


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
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["file.py"]),
        patch("gac.ai.generate_grouped_commits", return_value=invalid_data),
        patch("gac.main.console.print"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=False)
        assert exc.value.code == 1


def test_group_dry_run():
    """Dry run shows commits but doesn't execute."""
    response = json.dumps({"commits": [{"files": ["file1.py"], "message": "feat: add"}]})

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["file1.py"]),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print") as mock_print,
        patch("gac.main.execute_commit") as mock_commit,
    ):
        with pytest.raises(SystemExit):
            main(group=True, dry_run=True, require_confirmation=False, model="openai:gpt-4")
        mock_commit.assert_not_called()
        assert any("Dry run" in str(call) for call in mock_print.call_args_list)


def test_group_retries_when_files_missing():
    """If grouped response omits staged files, auto-retry with corrective feedback."""
    first = json.dumps({"commits": [{"files": ["a.py"], "message": "feat: update a"}]})
    second = json.dumps(
        {
            "commits": [
                {"files": ["a.py"], "message": "feat: update a"},
                {"files": ["b.py"], "message": "fix: update b"},
            ]
        }
    )

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=["a.py", "b.py"]),
        patch("gac.ai.generate_grouped_commits", side_effect=[first, second]) as mock_gen,
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit") as mock_commit,
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 0
        assert mock_commit.call_count == 2
        assert mock_gen.call_count == 2
