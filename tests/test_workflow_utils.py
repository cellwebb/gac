from unittest.mock import patch

from gac.workflow_utils import check_token_warning, handle_confirmation_loop, restore_staging


def test_confirmation_no():
    with patch("click.prompt", return_value="no"):
        result, message, _ = handle_confirmation_loop("msg", [], False, "m")
        assert result == "no"
        assert message == "msg"


def test_confirmation_empty():
    with patch("click.prompt", side_effect=["", "y"]):
        result, message, _ = handle_confirmation_loop("msg", [], False, "m")
        assert result == "yes"
        assert message == "msg"


def test_confirmation_regenerate():
    with patch("click.prompt", return_value="r"):
        result, message, msgs = handle_confirmation_loop("msg", [], False, "m")
        assert result == "regenerate"
        assert message == "msg"
        assert msgs[-1]["content"] == "Please provide an alternative commit message using the same repository context."


def test_confirmation_reroll():
    with patch("click.prompt", return_value="reroll"):
        result, message, msgs = handle_confirmation_loop("msg", [], False, "m")
        assert result == "regenerate"
        assert message == "msg"


def test_token_warning_decline():
    with patch("click.confirm", return_value=False):
        assert check_token_warning(1000, 500, True) is False


def test_restore_staging():
    """Test that restore_staging resets and re-adds files."""
    files = ["file1.py", "file2.py", "file3.py"]

    with patch("gac.git.run_git_command") as mock_git:
        restore_staging(files)

        assert mock_git.call_count == 4
        mock_git.assert_any_call(["reset", "HEAD"])
        mock_git.assert_any_call(["add", "file1.py"])
        mock_git.assert_any_call(["add", "file2.py"])
        mock_git.assert_any_call(["add", "file3.py"])


def test_restore_staging_reapplies_diff(tmp_path):
    """Test that staged diff is reapplied when provided."""
    calls = []

    def fake_run_git(cmd):
        calls.append(cmd)
        return ""

    with patch("gac.git.run_git_command", side_effect=fake_run_git):
        restore_staging(["file1.py"], "dummy diff")

    assert calls[0] == ["reset", "HEAD"]
    assert calls[1][0:2] == ["apply", "--cached"]
    assert len(calls) == 2


def test_restore_staging_handles_errors():
    """Test that restore_staging continues even if individual file adds fail."""
    files = ["file1.py", "file2.py"]

    def git_side_effect(cmd):
        if cmd == ["add", "file1.py"]:
            raise Exception("File not found")

    with (
        patch("gac.git.run_git_command", side_effect=git_side_effect) as mock_git,
        patch("gac.workflow_utils.logger.warning") as mock_logger,
    ):
        restore_staging(files)

        assert mock_git.call_count == 3
        mock_logger.assert_called_once()


def test_restore_staging_diff_failure_falls_back():
    """Test that restore_staging falls back to file add when diff apply fails."""

    def git_side_effect(cmd):
        if cmd[:2] == ["apply", "--cached"]:
            raise Exception("apply failed")

    with (
        patch("gac.git.run_git_command", side_effect=git_side_effect) as mock_git,
        patch("gac.workflow_utils.logger.warning") as mock_logger,
    ):
        restore_staging(["file1.py"], "dummy diff")

        # reset + apply + add
        assert mock_git.call_count == 3
        mock_logger.assert_called_once()
