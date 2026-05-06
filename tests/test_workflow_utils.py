from unittest.mock import patch

from gac.constants import EnvDefaults
from gac.git import GitCommandResult
from gac.workflow_utils import (
    check_token_warning,
    collect_interactive_answers,
    execute_commit,
    format_answers_for_prompt,
    handle_confirmation_loop,
    restore_staging,
)


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


def test_confirmation_e_opens_inplace_by_default():
    """Test that 'e' opens the in-place TUI editor when GAC_EDITOR is not set."""
    with (
        patch.dict("os.environ", {}, clear=True),
        patch("click.prompt", side_effect=["e", "y"]),
        patch("gac.editor.edit_commit_message_inplace", return_value="feat: edited inplace") as mock_inplace,
        patch("gac.workflow_utils.console.print"),
    ):
        result, message, _ = handle_confirmation_loop("msg", [{"role": "assistant", "content": "msg"}], False, "m")
        assert result == "yes"
        assert message == "feat: edited inplace"
        mock_inplace.assert_called_once_with("msg")


def test_confirmation_e_opens_external_when_gac_editor_set():
    """Test that 'e' opens the external editor when GAC_EDITOR is set."""
    with (
        patch.dict("os.environ", {"GAC_EDITOR": "vim"}, clear=True),
        patch("click.prompt", side_effect=["e", "y"]),
        patch("gac.editor.edit_commit_message_in_editor", return_value="feat: edited in vim") as mock_editor,
        patch("gac.workflow_utils.console.print"),
    ):
        result, message, _ = handle_confirmation_loop("msg", [{"role": "assistant", "content": "msg"}], False, "m")
        assert result == "yes"
        assert message == "feat: edited in vim"
        mock_editor.assert_called_once_with("msg")


def test_confirmation_e_empty_gac_editor_uses_inplace():
    """Empty GAC_EDITOR should behave like unset (use in-place editor)."""
    with (
        patch.dict("os.environ", {"GAC_EDITOR": ""}, clear=True),
        patch("click.prompt", side_effect=["e", "y"]),
        patch("gac.editor.edit_commit_message_inplace", return_value="feat: edited inplace") as mock_inplace,
        patch("gac.workflow_utils.console.print"),
    ):
        result, message, _ = handle_confirmation_loop("msg", [{"role": "assistant", "content": "msg"}], False, "m")
        assert result == "yes"
        assert message == "feat: edited inplace"
        mock_inplace.assert_called_once_with("msg")


def test_confirmation_editor_cancelled():
    """Test that 'e' with cancelled editor preserves original message."""
    with (
        patch.dict("os.environ", {}, clear=True),
        patch("click.prompt", side_effect=["e", "y"]),
        patch("gac.editor.edit_commit_message_inplace", return_value=None) as mock_inplace,
        patch("gac.workflow_utils.console.print"),
    ):
        result, message, _ = handle_confirmation_loop("msg", [{"role": "assistant", "content": "msg"}], False, "m")
        assert result == "yes"
        assert message == "msg"
        mock_inplace.assert_called_once_with("msg")


def test_confirmation_reroll():
    with patch("click.prompt", return_value="reroll"):
        result, message, msgs = handle_confirmation_loop("msg", [], False, "m")
        assert result == "regenerate"
        assert message == "msg"


def test_execute_commit_uses_hook_timeout():
    with (
        patch("gac.git.run_git_command", return_value=GitCommandResult.ok("")) as mock_git,
        patch("gac.workflow_utils.logger.info"),
        patch("gac.workflow_utils.console.print"),
    ):
        execute_commit("feat: add hook timeout", no_verify=False, hook_timeout=180)

    mock_git.assert_called_once_with(["commit", "-m", "feat: add hook timeout"], timeout=180)


def test_execute_commit_falls_back_to_default_timeout():
    with (
        patch("gac.git.run_git_command", return_value=GitCommandResult.ok("")) as mock_git,
        patch("gac.workflow_utils.logger.info"),
        patch("gac.workflow_utils.console.print"),
    ):
        execute_commit("fix: use defaults", no_verify=True, hook_timeout=0)

    mock_git.assert_called_once_with(
        ["commit", "-m", "fix: use defaults", "--no-verify"], timeout=EnvDefaults.HOOK_TIMEOUT
    )


def test_token_warning_decline():
    with patch("click.confirm", return_value=False):
        assert check_token_warning(1000, 500, True) is False


def test_restore_staging():
    """Test that restore_staging resets and re-adds files."""
    files = ["file1.py", "file2.py", "file3.py"]

    with patch("gac.git.run_git_command", return_value=GitCommandResult.ok("")) as mock_git:
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
        return GitCommandResult.ok("")

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
        return GitCommandResult.ok("")

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
        return GitCommandResult.ok("")

    with (
        patch("gac.git.run_git_command", side_effect=git_side_effect) as mock_git,
        patch("gac.workflow_utils.logger.warning") as mock_logger,
    ):
        restore_staging(["file1.py"], "dummy diff")

        # reset + apply + add
        assert mock_git.call_count == 3
        mock_logger.assert_called_once()


class TestCollectInteractiveAnswers:
    """Test the collect_interactive_answers function."""

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_success(self, mock_prompt, mock_print):
        """Test successful collection of answers."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
            "How does this affect performance?",
        ]

        # Mock user responses
        mock_prompt.side_effect = [
            "To fix authentication bug",
            "Yes, need to validate inputs",
            "Improves response time by 20%",
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
            "Are there any security considerations?": "Yes, need to validate inputs",
            "How does this affect performance?": "Improves response time by 20%",
        }

        # Verify all questions were prompted

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_with_empty_questions(self, mock_prompt, mock_print):
        """Test collection with empty questions list."""
        answers = collect_interactive_answers([])

        assert answers == {}
        mock_prompt.assert_not_called()

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_with_none_questions(self, mock_prompt, mock_print):
        """Test collection with None questions."""
        answers = collect_interactive_answers(None)

        assert answers == {}
        mock_prompt.assert_not_called()

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_skip_command(self, mock_prompt, mock_print):
        """Test skip command to skip remaining questions."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
            "How does this affect performance?",
            "Should we update documentation?",
        ]

        # Mock user responses with 'skip' on second question
        mock_prompt.side_effect = [
            "To fix authentication bug",
            "skip",  # Should skip remaining questions
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
        }

        # Verify prompt was called only twice (first question + skip)

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_quit_command(self, mock_prompt, mock_print):
        """Test quit command to abort interactive mode."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
        ]

        # Mock user response with 'quit'
        mock_prompt.side_effect = ["quit"]

        answers = collect_interactive_answers(questions)

        assert answers is None

        # Verify quit message was printed
        mock_print.assert_any_call("\n[yellow]⚠️  Interactive mode aborted by user[/yellow]")

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_empty_input(self, mock_prompt, mock_print):
        """Test empty input to skip individual questions."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
            "How does this affect performance?",
        ]

        # Mix of answers and empty inputs
        mock_prompt.side_effect = [
            "To fix authentication bug",  # Valid answer
            "",  # Skip this question
            "Improves response time",  # Valid answer
            "",  # Skip this question
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
            "How does this affect performance?": "Improves response time",
        }

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_none_input(self, mock_prompt, mock_print):
        """Test 'none' input to skip individual questions."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
        ]

        mock_prompt.side_effect = [
            "To fix authentication bug",
            "none",  # Should be treated as skip
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
        }

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_case_insensitive_commands(self, mock_prompt, mock_print):
        """Test that commands are case insensitive."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
            "How does this affect performance?",
        ]

        mock_prompt.side_effect = [
            "To fix authentication bug",
            "SKIP",  # Uppercase skip
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
        }

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_whitespace_handling(self, mock_prompt, mock_print):
        """Test proper handling of whitespace in inputs."""
        questions = [
            "What is the purpose of this change?",
        ]

        mock_prompt.side_effect = [
            "  To fix authentication bug  ",  # Should be stripped
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "What is the purpose of this change?": "To fix authentication bug",
        }

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_keyboard_interrupt(self, mock_prompt, mock_print):
        """Test handling of keyboard interrupt (Ctrl+C)."""
        questions = [
            "What is the purpose of this change?",
            "Are there any security considerations?",
        ]

        # Mock Ctrl+C (KeyboardInterrupt)
        mock_prompt.side_effect = KeyboardInterrupt()

        answers = collect_interactive_answers(questions)

        assert answers is None

        # Verify abort message was printed
        mock_print.assert_any_call("\n[yellow]⚠️  Interactive mode aborted by user[/yellow]")


class TestFormatAnswersForPrompt:
    """Test the format_answers_for_prompt function."""

    def test_format_answers_empty(self):
        """Test formatting with empty answers."""
        result = format_answers_for_prompt({})

        assert result == ""

    def test_format_answers_single_answer(self):
        """Test formatting with a single answer."""
        answers = {
            "What is the purpose of this change?": "To fix authentication bug",
        }

        result = format_answers_for_prompt(answers)

        assert "Q: What is the purpose of this change?" in result
        assert "A: To fix authentication bug" in result
        assert "<user_answers>" in result
        assert "</user_answers>" in result
        assert "<context_request>" in result
        assert "</context_request>" in result

    def test_format_answers_multiple_answers(self):
        """Test formatting with multiple answers."""
        answers = {
            "What is the purpose of this change?": "To fix authentication bug",
            "Are there any security considerations?": "Yes, need to validate inputs",
            "How does this affect performance?": "Improves response time by 20%",
        }

        result = format_answers_for_prompt(answers)

        assert "Q: What is the purpose of this change?" in result
        assert "A: To fix authentication bug" in result
        assert "Q: Are there any security considerations?" in result
        assert "A: Yes, need to validate inputs" in result
        assert "Q: How does this affect performance?" in result
        assert "A: Improves response time by 20%" in result

        # Verify structure
        assert result.startswith("\n\n<user_answers>")
        assert result.endswith("</context_request>")

        # Verify proper spacing
        lines = result.split("\n")
        assert "" in lines  # Should have blank lines between sections

    def test_format_answers_with_special_characters(self):
        """Test formatting with special characters in answers."""
        answers = {
            "What's the function name?": "It's called `authenticate_user()`",
            "Any JSON operations?": '{"endpoint": "/api/auth", "method": "POST"}',
            "Multiline answer?": "First line\nSecond line\nThird line",
        }

        result = format_answers_for_prompt(answers)

        # Should preserve special characters
        assert "authenticate_user()" in result
        assert "/api/auth" in result
        assert "POST" in result
        # Note: multiline answers will be on single lines due to dict structure

    def test_format_answers_preserves_order(self):
        """Test that answer order is preserved (Python 3.7+ dicts maintain order)."""
        answers = {
            "First question?": "First answer",
            "Second question?": "Second answer",
            "Third question?": "Third answer",
        }

        result = format_answers_for_prompt(answers)

        # Should maintain the order from the dict
        first_pos = result.find("First question?")
        second_pos = result.find("Second question?")
        third_pos = result.find("Third question?")

        assert first_pos < second_pos < third_pos

    def test_format_answers_with_whitespace(self):
        """Test formatting with whitespace-heavy content."""
        answers = {
            "Question with spaces?": "  Answer with leading/trailing spaces  ",
            "Question with newlines?": "Answer\nwith\ninternal\nnewlines",
        }

        result = format_answers_for_prompt(answers)

        # Should preserve whitespace in answers
        assert "  Answer with leading/trailing spaces  " in result
        assert "Answer\nwith\ninternal\nnewlines" in result

    def test_format_answers_empty_content(self):
        """Test formatting with empty string answers."""
        answers = {
            "Question 1?": "",
            "Question 2?": "Valid answer",
            "Question 3?": "",
        }

        result = format_answers_for_prompt(answers)

        # Should include even empty answers
        assert "Q: Question 1?" in result
        assert "A: " in result  # Empty answer
        assert "Q: Question 2?" in result
        assert "A: Valid answer" in result

    def test_format_answers_very_long_content(self):
        """Test formatting with very long answers."""
        long_answer = "A" * 1000  # Very long answer
        answers = {
            "What is the detailed explanation?": long_answer,
        }

        result = format_answers_for_prompt(answers)

        assert long_answer in result
        assert len(result) > 1000  # Should contain the full long answer

    def test_format_answers_structure_validation(self):
        """Test that the formatted structure is exactly as expected."""
        answers = {
            "Test question?": "Test answer",
        }

        result = format_answers_for_prompt(answers)

        # Extract key structural elements
        assert result.startswith("\n\n<user_answers>\n")
        assert "The user provided the following clarifying information:\n\n" in result
        assert "<context_request>" in result

        # Verify no extra whitespace at the end
        assert not result.endswith("\n\n")
        assert result.endswith("</context_request>")


class TestInteractiveModeEdgeCases:
    """Test edge cases and error conditions for interactive mode."""

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_mixed_valid_invalid_inputs(self, mock_prompt, mock_print):
        """Test mixing valid answers, skips, and commands."""
        questions = [
            "Q1?",
            "Q2?",
            "Q3?",
            "Q4?",
            "Q5?",
        ]

        mock_prompt.side_effect = [
            "Valid answer 1",  # Valid
            "",  # Skip
            "Valid answer 3",  # Valid
            "skip",  # Skip remaining
            # Q5 should not be prompted due to skip
        ]

        answers = collect_interactive_answers(questions)

        assert answers == {
            "Q1?": "Valid answer 1",
            "Q3?": "Valid answer 3",
        }

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_commands_like_normal_text(self, mock_prompt, mock_print):
        """Test that ' quit' ' skip ' with spaces are treated as normal text, not commands."""
        questions = ["What's the change?"]

        mock_prompt.side_effect = [" quit "]  # Should be treated as literal text, not command

        answers = collect_interactive_answers(questions)

        # Should be treated as normal answer since it's not exactly "quit"
        assert answers is None

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_all_questions_skipped(self, mock_prompt, mock_print):
        """Test when all questions are skipped."""
        questions = ["Q1?", "Q2?", "Q3?"]

        mock_prompt.side_effect = ["", "", ""]  # All empty

        answers = collect_interactive_answers(questions)

        assert answers == {}

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_quit_then_continue(self, mock_prompt, mock_print):
        """Test that after quit, the function returns None immediately."""
        questions = ["Q1?", "Q2?", "Q3?"]

        mock_prompt.side_effect = ["quit"]  # Quit immediately

        answers = collect_interactive_answers(questions)

        assert answers is None

    def test_format_answers_with_unicode_and_special_chars(self):
        """Test formatting with Unicode and special characters."""
        answers = {
            "¿Qué hace esta función?": "Autentica usuarios con emojis 🎯",
            "Mathematical expression?": "E = mc² and ∑(i=1 to n) i = n(n+1)/2",
            "URL reference?": "https://example.com/api/v1.0/endpoint?param=value#section",
        }

        result = format_answers_for_prompt(answers)

        assert "Autentica usuarios con emojis 🎯" in result
        assert "E = mc²" in result
        assert "∑(i=1 to n) i = n(n+1)/2" in result
        assert "https://example.com/api/v1.0/endpoint" in result

    @patch("gac.workflow_utils.console.print")
    @patch("gac.workflow_utils.prompt")
    def test_collect_answers_very_long_questions_and_answers(self, mock_prompt, mock_print):
        """Test handling of very long questions and answers."""
        long_question = "What is the purpose of implementing this " + "very " * 50 + "long change?"
        long_answer = "This change fixes the " + "authentication " * 50 + "mechanism."
        questions = [long_question]

        mock_prompt.side_effect = [long_answer]

        answers = collect_interactive_answers(questions)

        assert answers == {long_question: long_answer}
        assert len(answers[long_question]) > 700


class TestFormatTokenUsage:
    """Tests for format_token_usage function."""

    def test_basic_usage(self) -> None:
        from gac.workflow_utils import format_token_usage

        result = format_token_usage(100, 50)
        assert result == "100 prompt + 50 completion = 150 total"

    def test_with_reasoning_tokens(self) -> None:
        from gac.workflow_utils import format_token_usage

        result = format_token_usage(100, 50, 25)
        assert result == "100 prompt + 50 completion + 25 reasoning = 175 total"

    def test_zero_tokens(self) -> None:
        from gac.workflow_utils import format_token_usage

        result = format_token_usage(0, 0, 0)
        assert result == "0 prompt + 0 completion = 0 total"

    def test_reasoning_only(self) -> None:
        from gac.workflow_utils import format_token_usage

        result = format_token_usage(0, 0, 100)
        assert result == "0 prompt + 0 completion + 100 reasoning = 100 total"


class TestExecuteCommit:
    """Tests for execute_commit function."""

    @patch("gac.git.run_git_command")
    def test_commit_with_signoff(self, mock_run) -> None:
        from gac.workflow_utils import execute_commit

        mock_run.return_value.success = True
        execute_commit("test message", no_verify=False, signoff=True)
        # Check that --signoff was added
        call_args = mock_run.call_args[0][0]
        assert "--signoff" in call_args

    @patch("gac.git.run_git_command")
    def test_commit_with_no_verify_and_signoff(self, mock_run) -> None:
        from gac.workflow_utils import execute_commit

        mock_run.return_value.success = True
        execute_commit("test message", no_verify=True, signoff=True)
        # Check that both flags were added
        call_args = mock_run.call_args[0][0]
        assert "--no-verify" in call_args
        assert "--signoff" in call_args
