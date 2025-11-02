from unittest.mock import patch

from gac.workflow_utils import check_token_warning, handle_confirmation_loop


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
