from unittest.mock import patch

from gac.workflow_utils import check_token_warning, handle_confirmation_loop, restore_staging


def test_confirmation_no():
    with patch("click.prompt", return_value="no"):
        result, _ = handle_confirmation_loop("msg", [], False, "m")
        assert result == "no"


def test_confirmation_empty():
    with patch("click.prompt", side_effect=["", "y"]):
        result, _ = handle_confirmation_loop("msg", [], False, "m")
        assert result == "yes"


def test_confirmation_regenerate():
    with patch("click.prompt", return_value="r"):
        result, msgs = handle_confirmation_loop("msg", [], False, "m")
        assert result == "regenerate"
        assert msgs[-1]["content"] == "Please provide an alternative commit message using the same repository context."


def test_confirmation_reroll():
    with patch("click.prompt", return_value="reroll"):
        result, msgs = handle_confirmation_loop("msg", [], False, "m")
        assert result == "regenerate"


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
