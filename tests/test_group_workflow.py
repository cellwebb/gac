"""Tests for grouped commits workflow."""

import json
from unittest.mock import patch

import pytest

from gac.main import main


@pytest.fixture(autouse=True)
def skip_git_hooks(monkeypatch):
    """Avoid invoking lefthook/pre-commit binaries during unit tests."""
    monkeypatch.setattr("gac.main.run_lefthook_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_pre_commit_hooks", lambda *_, **__: True)
    monkeypatch.setattr("gac.main.run_git_command", lambda *_, **__: "/fake/repo", raising=False)


def test_group_with_no_staged_changes(tmp_path, monkeypatch):
    """--group with no staged changes shows appropriate error."""
    monkeypatch.chdir(tmp_path)

    with (
        patch("gac.main.run_git_command", return_value=str(tmp_path)),
        patch("gac.main.get_staged_files", return_value=[]),
        patch("gac.main.console.print") as mock_print,
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=False)
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


def test_group_restores_staging_on_first_commit_failure():
    """Staging is restored when the first commit fails."""
    response = json.dumps(
        {
            "commits": [
                {"files": ["a.py"], "message": "feat: add a"},
                {"files": ["b.py"], "message": "feat: add b"},
            ]
        }
    )

    original_files = ["a.py", "b.py"]

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=original_files),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit", side_effect=Exception("Commit failed")) as mock_commit,
        patch("gac.main.restore_staging") as mock_restore,
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 1
        mock_commit.assert_called_once()
        mock_restore.assert_called_once_with(original_files, "/fake/repo")


def test_group_does_not_restore_staging_on_later_commit_failure():
    """Staging is not restored when a commit after the first fails (commits already made)."""
    response = json.dumps(
        {
            "commits": [
                {"files": ["a.py"], "message": "feat: add a"},
                {"files": ["b.py"], "message": "feat: add b"},
            ]
        }
    )

    original_files = ["a.py", "b.py"]

    def commit_side_effect(msg, no_verify, hook_timeout):
        if "add b" in msg:
            raise Exception("Second commit failed")

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=original_files),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit", side_effect=commit_side_effect) as mock_commit,
        patch("gac.main.restore_staging") as mock_restore,
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit) as exc:
            main(group=True, model="openai:gpt-4", require_confirmation=True)
        assert exc.value.code == 1
        assert mock_commit.call_count == 2
        mock_restore.assert_not_called()


def test_group_displays_file_lists():
    """File lists are displayed for each commit in dim/gray text."""
    response = json.dumps(
        {
            "commits": [
                {"files": ["src/auth.py", "src/login.py"], "message": "feat: add auth"},
                {"files": ["tests/test_auth.py"], "message": "test: add auth tests"},
                {"files": ["README.md", "docs/auth.md"], "message": "docs: document auth"},
            ]
        }
    )

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch(
            "gac.main.get_staged_files",
            return_value=["src/auth.py", "src/login.py", "tests/test_auth.py", "README.md", "docs/auth.md"],
        ),
        patch("gac.ai.generate_grouped_commits", return_value=response),
        patch("gac.main.console.print") as mock_print,
        patch("gac.main.execute_commit"),
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit):
            main(group=True, model="openai:gpt-4", require_confirmation=True)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("src/auth.py, src/login.py" in call for call in print_calls), "First commit files not displayed"
        assert any("tests/test_auth.py" in call for call in print_calls), "Second commit files not displayed"
        assert any("README.md, docs/auth.md" in call for call in print_calls), "Third commit files not displayed"


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
    response = json.dumps({"commits": [{"files": [f"file{i}.py" for i in range(num_files)], "message": "feat: add"}]})
    base_tokens = 512

    mock_config = {
        "temperature": 0.7,
        "max_output_tokens": base_tokens,
        "max_retries": 3,
        "warning_limit_tokens": 4096,
    }

    with (
        patch("gac.main.run_git_command", return_value="/fake/repo"),
        patch("gac.main.get_staged_files", return_value=[f"file{i}.py" for i in range(num_files)]),
        patch("gac.main.config", mock_config),
        patch("gac.ai.generate_grouped_commits", return_value=response) as mock_gen,
        patch("gac.main.console.print"),
        patch("gac.main.execute_commit"),
        patch("gac.main.click.prompt", return_value="y"),
    ):
        with pytest.raises(SystemExit):
            main(group=True, model="openai:gpt-4", require_confirmation=True)

        call_args = mock_gen.call_args
        actual_max_tokens = call_args.kwargs["max_tokens"]
        expected_tokens = base_tokens * expected_multiplier
        assert actual_max_tokens == expected_tokens, (
            f"For {num_files} files, expected {expected_multiplier}x scaling "
            f"({expected_tokens} tokens), got {actual_max_tokens}"
        )
