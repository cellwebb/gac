from unittest.mock import patch

import pytest

from gac.main import execute_grouped_commits_workflow, execute_single_commit_workflow


def _workflow_kwargs(**overrides):
    base = {
        "system_prompt": "",
        "user_prompt": "",
        "model": "invalid-model",
        "temperature": 0.1,
        "max_output_tokens": 4096,
        "max_retries": 1,
        "require_confirmation": False,
        "quiet": True,
        "no_verify": False,
        "dry_run": True,
        "push": False,
        "show_prompt": False,
        "interactive": False,
        "message_only": False,
    }
    base.update(overrides)
    return base


def test_grouped_workflow_invalid_model_exits_with_message():
    kwargs = _workflow_kwargs()

    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        execute_grouped_commits_workflow(**kwargs)

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed


def test_single_workflow_invalid_model_exits_with_message():
    kwargs = _workflow_kwargs()

    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        execute_single_commit_workflow(**kwargs)

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed


def test_trailing_colon_model_exits_with_message():
    """Test that 'openai:' (trailing colon, empty model name) is rejected."""
    kwargs = _workflow_kwargs(model="openai:")

    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        execute_single_commit_workflow(**kwargs)

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed
    assert "provider and model name are required" in printed


def test_leading_colon_model_exits_with_message():
    """Test that ':gpt-4' (leading colon, empty provider) is rejected."""
    kwargs = _workflow_kwargs(model=":gpt-4")

    with patch("gac.main.console.print") as mock_print, pytest.raises(SystemExit) as exc:
        execute_single_commit_workflow(**kwargs)

    assert exc.value.code == 1
    printed = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Invalid model format" in printed
    assert "provider and model name are required" in printed
