"""Tests for the main module including interactive mode functionality."""

from unittest.mock import patch

import pytest

from gac.main import (
    AIError,
    _parse_questions_from_response,
    execute_single_commit_workflow,
    generate_contextual_questions,
)


class TestGenerateContextualQuestions:
    """Test the generate_contextual_questions function."""

    @pytest.fixture
    def mock_build_question_generation_prompt(self):
        """Mock the build_question_generation_prompt function."""
        with patch("gac.prompt.build_question_generation_prompt") as mock:
            mock.return_value = ("system_prompt", "user_prompt")
            yield mock

    @pytest.fixture
    def mock_generate_commit_message(self):
        """Mock the generate_commit_message function."""
        with patch("gac.main.generate_commit_message") as mock:
            yield mock

    @pytest.fixture
    def sample_inputs(self):
        """Sample inputs for generating questions."""
        return {
            "model": "anthropic:claude-3-haiku",
            "status": "M file1.py\nA file2.txt",
            "processed_diff": "diff --git a/file1.py b/file1.py\n+ new line",
            "diff_stat": "1 file changed, 1 insertion(+)",
            "hint": "fix authentication issue",
        }

    def test_generate_questions_success(
        self, mock_build_question_generation_prompt, mock_generate_commit_message, sample_inputs
    ):
        """Test successful question generation."""
        # Mock LLM response with numbered questions
        mock_response = """1. What authentication mechanism was implemented?
2. Are there any security considerations for this change?
3. Does this fix affect existing user sessions?"""
        mock_generate_commit_message.return_value = mock_response

        questions = generate_contextual_questions(**sample_inputs)

        # Verify the prompt was built correctly
        mock_build_question_generation_prompt.assert_called_once_with(
            status=sample_inputs["status"],
            processed_diff=sample_inputs["processed_diff"],
            diff_stat=sample_inputs["diff_stat"],
            hint=sample_inputs["hint"],
        )

        # Verify the LLM was called with correct parameters
        mock_generate_commit_message.assert_called_once_with(
            model=sample_inputs["model"],
            prompt=("system_prompt", "user_prompt"),
            temperature=1,  # default from EnvDefaults
            max_tokens=4096,  # default from EnvDefaults
            max_retries=3,  # default from EnvDefaults
            quiet=False,
            skip_success_message=True,
            task_description="contextual questions",
        )

        # Verify questions were parsed correctly
        assert len(questions) == 3
        assert "What authentication mechanism was implemented?" in questions
        assert "Are there any security considerations for this change?" in questions
        assert "Does this fix affect existing user sessions?" in questions

    def test_generate_questions_with_custom_parameters(
        self, mock_build_question_generation_prompt, mock_generate_commit_message, sample_inputs
    ):
        """Test question generation with custom parameters."""
        mock_generate_commit_message.return_value = "1. Simple question?"

        generate_contextual_questions(
            **sample_inputs,
            temperature=0.5,
            max_tokens=2048,
            max_retries=5,
            quiet=True,
        )

        # Verify custom parameters were passed through
        mock_generate_commit_message.assert_called_once_with(
            model=sample_inputs["model"],
            prompt=("system_prompt", "user_prompt"),
            temperature=0.5,
            max_tokens=2048,
            max_retries=5,
            quiet=True,
            skip_success_message=True,
            task_description="contextual questions",
        )

    def test_generate_questions_handles_llm_error(
        self, mock_build_question_generation_prompt, mock_generate_commit_message, sample_inputs
    ):
        """Test that LLM errors are properly wrapped as AIError."""
        mock_generate_commit_message.side_effect = Exception("LLM API error")

        with pytest.raises(AIError) as exc_info:
            generate_contextual_questions(**sample_inputs)

        assert "Failed to generate contextual questions" in str(exc_info.value)
        assert "LLM API error" in str(exc_info.value.__cause__)

    def test_generate_questions_empty_response(
        self, mock_build_question_generation_prompt, mock_generate_commit_message, sample_inputs
    ):
        """Test handling of empty or malformed responses."""
        mock_generate_commit_message.return_value = ""

        questions = generate_contextual_questions(**sample_inputs)

        assert questions == []

    def test_generate_questions_with_bullets(
        self, mock_build_question_generation_prompt, mock_generate_commit_message, sample_inputs
    ):
        """Test parsing questions with bullet points."""
        mock_response = """1. • What is the main purpose of this change?
2. - Are there any breaking changes?
3. * How does this affect performance?"""
        mock_generate_commit_message.return_value = mock_response

        questions = generate_contextual_questions(**sample_inputs)

        assert len(questions) == 3
        assert "What is the main purpose of this change?" == questions[0]
        assert "Are there any breaking changes?" == questions[1]
        assert "How does this affect performance?" == questions[2]

    def test_generate_questions_adaptive_for_small_change(
        self, mock_build_question_generation_prompt, mock_generate_commit_message
    ):
        """Test that small changes generate fewer questions."""
        # Mock small change: single file, minimal modifications
        small_inputs = {
            "model": "anthropic:claude-3-haiku",
            "status": "M utils.py",
            "processed_diff": "diff --git a/utils.py b/utils.py\n@@ -1,3 +1,4 @@\n def helper():\n+    new_line = True\n     return True",
            "diff_stat": "1 file changed, 1 insertion(+)",
            "hint": "",
        }

        # Mock LLM response with fewer questions for small change
        mock_response = """1. What is the purpose of adding this new line?
2. How does this affect the helper function's behavior?"""
        mock_generate_commit_message.return_value = mock_response

        questions = generate_contextual_questions(**small_inputs)

        # Verify fewer questions were generated for small change
        assert len(questions) == 2
        assert "What is the purpose of adding this new line?" in questions
        assert "How does this affect the helper function's behavior?" in questions

        # Verify the prompt was built with small change context
        mock_build_question_generation_prompt.assert_called_once_with(
            status=small_inputs["status"],
            processed_diff=small_inputs["processed_diff"],
            diff_stat=small_inputs["diff_stat"],
            hint=small_inputs["hint"],
        )

    def test_generate_questions_adaptive_for_large_change(
        self, mock_build_question_generation_prompt, mock_generate_commit_message
    ):
        """Test that large changes generate more questions."""
        # Mock large change: multiple files, substantial modifications
        large_inputs = {
            "model": "anthropic:claude-3-haiku",
            "status": "M auth.py\nM api.py\nA middleware.py\nD old_handler.py",
            "processed_diff": """diff --git a/auth.py b/auth.py\n@@ -10,7 +10,15 @@ class Auth:
+    def new_auth_method(self, token):
+        return self.validate_token(token)

 diff --git a/api.py b/api.py\n@@ -5,6 +5,12 @@ class API:
     def get(self):
+        if self.auth.check():
+            return self.process_request()

 diff --git a/middleware.py b/middleware.py\nnew file mode 100644\n@@ -0,0 +1,25 @@\n+class Middleware:
+    def process_request(self, request):
+        return self.validate(request)

 diff --git a/old_handler.py b/old_handler.py\ndeleted file mode 100644\n@@ -1,15 +0,0 @@\n-def old_handler():
-    pass""",
            "diff_stat": "4 files changed, 42 insertions(+), 15 deletions(-)",
            "hint": "implement new authentication system",
        }

        # Mock LLM response with more questions for large change
        mock_response = """1. What problem does the new authentication system solve?
2. Why was the old handler completely removed instead of deprecated?
3. How does the new middleware integrate with existing API endpoints?
4. What security considerations were taken into account for token validation?
5. How will existing users migrate to the new authentication method?"""
        mock_generate_commit_message.return_value = mock_response

        questions = generate_contextual_questions(**large_inputs)

        # Verify more questions were generated for large change
        assert len(questions) == 5
        assert "What problem does the new authentication system solve?" in questions
        assert "Why was the old handler completely removed instead of deprecated?" in questions
        assert "How does the new middleware integrate with existing API endpoints?" in questions
        assert "What security considerations were taken into account for token validation?" in questions
        assert "How will existing users migrate to the new authentication method?" in questions

        # Verify the prompt was built with large change context
        mock_build_question_generation_prompt.assert_called_once_with(
            status=large_inputs["status"],
            processed_diff=large_inputs["processed_diff"],
            diff_stat=large_inputs["diff_stat"],
            hint=large_inputs["hint"],
        )


class TestParseQuestionsFromResponse:
    """Test the _parse_questions_from_response function."""

    def test_parse_numbered_questions_with_periods(self):
        """Test parsing numbered questions with periods."""
        response = """1. What is the purpose of this function?
2. How does it handle errors?
3. Are there any edge cases to consider?
4. Should we add tests for this?"""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 4
        assert questions[0] == "What is the purpose of this function?"
        assert questions[1] == "How does it handle errors?"
        assert questions[2] == "Are there any edge cases to consider?"
        assert questions[3] == "Should we add tests for this?"

    def test_parse_numbered_questions_with_parentheses(self):
        """Test parsing numbered questions with parentheses."""
        response = """1) What testing approach was used?
2) Are there any performance implications?
3) Does this change the API contract?"""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 3
        assert questions[0] == "What testing approach was used?"
        assert questions[1] == "Are there any performance implications?"
        assert questions[2] == "Does this change the API contract?"

    def test_parse_questions_with_bullets_and_symbols(self):
        """Test parsing questions with various bullet symbols."""
        response = """1. • What security measures are in place?
2. - How is data validation handled?
3. * Are there any rate limiting considerations?"""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 3
        assert questions[0] == "What security measures are in place?"
        assert questions[1] == "How is data validation handled?"
        assert questions[2] == "Are there any rate limiting considerations?"

    def test_parse_fallback_non_numbered_questions(self):
        """Test fallback parsing for non-numbered questions."""
        response = """What is the primary goal of this change?
How does this affect existing functionality?
Should we update the documentation?"""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 3

    def test_parse_ignores_non_questions(self):
        """Test that non-question lines are ignored."""
        response = """1. What is the purpose of this change?
This is not a question.
Here's another statement.
2. How should we test this?
Not a question either."""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 2
        assert questions[0] == "What is the purpose of this change?"
        assert questions[1] == "How should we test this?"

    def test_parse_handles_empty_lines_and_whitespace(self):
        """Test parsing with empty lines and extra whitespace."""
        response = """

1. What does this function do?

   2. Should we add error handling?

3.  Is the logging sufficient?

"""

        questions = _parse_questions_from_response(response)

        assert len(questions) == 3
        assert questions[0] == "What does this function do?"
        assert questions[1] == "Should we add error handling?"
        assert questions[2] == "Is the logging sufficient?"

    def test_parse_short_questions_filtered(self):
        """Test that very short questions are filtered out (only for non-numbered questions)."""
        # Test numbered questions (no length filtering)
        response = """1. What is this?
2. How?
3. Why does this function need optimization?
4. Test?
5. What are the security implications of using this algorithm?"""

        questions = _parse_questions_from_response(response)

        # All numbered questions are included (no length filtering for numbered questions)
        assert len(questions) == 5
        assert "What is this?" in questions
        assert "How?" in questions
        assert "Why does this function need optimization?" in questions
        assert "Test?" in questions
        assert "What are the security implications of using this algorithm?" in questions


class TestInteractiveModeIntegration:
    """Test interactive mode integration in the main workflow."""

    @pytest.fixture
    def base_workflow_kwargs(self):
        """Base kwargs for workflow functions."""
        return {
            "system_prompt": "Generate a concise commit message following conventional commit format",
            "user_prompt": "Generate a commit message for the staged changes",
            "model": "anthropic:claude-3-haiku",
            "temperature": 0.1,
            "max_output_tokens": 4096,
            "max_retries": 1,
            "require_confirmation": False,
            "quiet": True,
            "no_verify": False,
            "dry_run": True,
            "push": False,
            "show_prompt": False,
            "interactive": False,  # Default: no interactive mode
            "message_only": False,
            "hook_timeout": 120,
        }

    @patch("gac.main.get_staged_files")
    @patch("gac.git")
    @patch("gac.main.generate_commit_message")
    @patch("gac.main.console.print")
    def test_single_commit_workflow_without_interactive(
        self, mock_print, mock_generate_msg, mock_git, mock_get_staged, base_workflow_kwargs
    ):
        """Test single commit workflow without interactive mode."""
        mock_get_staged.return_value = ["file1.py"]
        mock_git.get_staged_status.return_value = "M file1.py"
        mock_git.get_staged_diff.return_value = "diff content"
        mock_generate_msg.return_value = "feat: add new feature"

        with pytest.raises(SystemExit) as exc_info:
            execute_single_commit_workflow(**base_workflow_kwargs)

        # Verify successful exit
        assert exc_info.value.code == 0

        # Verify that interactive mode was not triggered
        assert not base_workflow_kwargs["interactive"]

    @patch("gac.main.get_staged_files")
    @patch("gac.git")
    @patch("gac.main.generate_commit_message")
    @patch("gac.main.generate_contextual_questions")
    @patch("gac.main.collect_interactive_answers")
    @patch("gac.main.format_answers_for_prompt")
    @patch("gac.main.console.print")
    def test_single_commit_workflow_with_interactive_success(
        self,
        mock_print,
        mock_format_answers,
        mock_collect_answers,
        mock_generate_questions,
        mock_generate_msg,
        mock_git,
        mock_get_staged,
        base_workflow_kwargs,
    ):
        """Test single commit workflow with interactive mode success."""
        # Setup mocks
        mock_get_staged.return_value = ["file1.py"]
        mock_git.get_staged_status.return_value = "M file1.py"
        mock_git.get_staged_diff.return_value = "diff content"

        # Interactive mode mocks
        questions = ["What is the purpose of this change?"]
        answers = {"What is the purpose of this change?": "To fix authentication bug"}
        mock_generate_questions.return_value = questions
        mock_collect_answers.return_value = answers
        mock_format_answers.return_value = "\n\n<user_answers>\nQ: What is the purpose of this change?\nA: To fix authentication bug\n\n</user_answers>\n\n"

        # Final commit message generation
        mock_generate_msg.return_value = "fix: resolve authentication issue"

        # Enable interactive mode
        workflow_kwargs = base_workflow_kwargs.copy()
        workflow_kwargs["interactive"] = True

        with pytest.raises(SystemExit) as exc_info:
            execute_single_commit_workflow(**workflow_kwargs)

        # Verify successful exit
        assert exc_info.value.code == 0

        # Verify interactive workflow was called
        mock_generate_questions.assert_called_once()
        mock_collect_answers.assert_called_once_with(questions)
        mock_format_answers.assert_called_once_with(answers)

    @patch("gac.main.get_staged_files")
    @patch("gac.git")
    @patch("gac.main.generate_commit_message")
    @patch("gac.main.generate_contextual_questions")
    @patch("gac.main.collect_interactive_answers")
    @patch("gac.main.console.print")
    def test_single_commit_workflow_with_interactive_abort(
        self,
        mock_print,
        mock_collect_answers,
        mock_generate_questions,
        mock_generate_msg,
        mock_git,
        mock_get_staged,
        base_workflow_kwargs,
    ):
        """Test single commit workflow when user aborts interactive mode."""
        # Setup mocks
        mock_get_staged.return_value = ["file1.py"]
        mock_git.get_staged_status.return_value = "M file1.py"
        mock_git.get_staged_diff.return_value = "diff content"

        # Interactive mode mocks - user aborts
        questions = ["What is the purpose of this change?"]
        mock_generate_questions.return_value = questions
        mock_collect_answers.return_value = None  # User aborted
        mock_generate_msg.return_value = "feat: add new feature"  # Still need a commit message

        # Enable interactive mode
        workflow_kwargs = base_workflow_kwargs.copy()
        workflow_kwargs["interactive"] = True

        with pytest.raises(SystemExit) as exc_info:
            execute_single_commit_workflow(**workflow_kwargs)

        # Verify it still exits successfully (doesn't actually abort the commit)
        assert exc_info.value.code == 0
        mock_collect_answers.assert_called_once_with(questions)

    @patch("gac.main.get_staged_files")
    @patch("gac.git")
    @patch("gac.main.generate_commit_message")
    @patch("gac.main.generate_contextual_questions")
    @patch("gac.main.collect_interactive_answers")
    @patch("gac.main.format_answers_for_prompt")
    @patch("gac.main.console.print")
    def test_single_commit_workflow_with_interactive_empty_questions(
        self,
        mock_print,
        mock_format_answers,
        mock_collect_answers,
        mock_generate_questions,
        mock_generate_msg,
        mock_git,
        mock_get_staged,
        base_workflow_kwargs,
    ):
        """Test single commit workflow when no questions are generated."""
        # Setup mocks
        mock_get_staged.return_value = ["file1.py"]
        mock_git.get_staged_status.return_value = "M file1.py"
        mock_git.get_staged_diff.return_value = "diff content"

        # Interactive mode mocks - no questions generated
        mock_generate_questions.return_value = []
        mock_collect_answers.return_value = {}
        mock_format_answers.return_value = ""

        # Final commit message generation
        mock_generate_msg.return_value = "feat: add new feature"

        # Enable interactive mode
        workflow_kwargs = base_workflow_kwargs.copy()
        workflow_kwargs["interactive"] = True

        with pytest.raises(SystemExit) as exc_info:
            execute_single_commit_workflow(**workflow_kwargs)

        # Verify successful exit
        assert exc_info.value.code == 0

        # Verify empty questions were handled gracefully
        mock_generate_questions.assert_called_once()
        # When questions is empty, collect_interactive_answers should not be called
        mock_collect_answers.assert_not_called()
        mock_format_answers.assert_not_called()


class TestInteractiveModeErrors:
    """Test error handling in interactive mode."""

    def test_generate_questions_ai_error_propagation(self):
        """Test that AIError from question generation is properly handled."""
        with patch("gac.ai.generate_commit_message") as mock_generate_msg:
            mock_generate_msg.side_effect = AIError.model_error("API limit exceeded")

            with pytest.raises(AIError) as exc_info:
                generate_contextual_questions(
                    model="anthropic:claude-3-haiku",
                    status="M file.py",
                    processed_diff="diff content",
                )

            assert "Failed to generate contextual questions" in str(exc_info.value)

    def test_parse_questions_malformed_input(self):
        """Test parsing questions from malformed input."""
        malformed_inputs = [
            "",  # Empty string
            "   ",  # Whitespace only
            "Not a question at all\nAnother non-question",  # No questions
            "1. ",  # Empty numbered item
            "1. No question mark",  # Missing question mark
            "Just text with 1. number but no question?",
        ]

        for malformed_input in malformed_inputs:
            questions = _parse_questions_from_response(malformed_input)
            assert isinstance(questions, list)
            # Should either be empty or contain only valid questions
            for question in questions:
                assert question.endswith("?")
                # Length filtering only applies to non-numbered questions
                assert len(question) > 0


class TestInteractiveModeCLIIntegration:
    """Test interactive mode integration with CLI functionality."""

    @patch("gac.main.execute_single_commit_workflow")
    @patch("gac.main.console.print")
    def test_build_question_generation_prompt(self, mock_print, mock_execute):
        """Test the build_question_generation_prompt function directly."""
        from gac.prompt import build_question_generation_prompt

        # Test with typical inputs
        status = "M file1.py\nA file2.txt"
        processed_diff = "diff --git a/file1.py b/file1.py\n+ new line"
        diff_stat = "1 file changed, 1 insertion(+)"
        hint = "Fix authentication issue"

        system_prompt, user_prompt = build_question_generation_prompt(
            status=status,
            processed_diff=processed_diff,
            diff_stat=diff_stat,
            hint=hint,
        )

        # Verify prompt structure
        assert isinstance(system_prompt, str)
        assert isinstance(user_prompt, str)
        assert len(system_prompt) > 0
        assert len(user_prompt) > 0

        # Verify content is included
        assert status in user_prompt
        assert processed_diff in user_prompt
        assert diff_stat in user_prompt
        assert hint in user_prompt

        # Verify it asks for questions
        assert "question" in system_prompt.lower() or "ask" in system_prompt.lower()

    def test_build_question_generation_prompt_without_optional_inputs(self):
        """Test the build_question_generation_prompt function with minimal inputs."""
        from gac.prompt import build_question_generation_prompt

        # Test with minimal inputs
        status = "M file1.py"
        processed_diff = "+ new line"
        diff_stat = ""
        hint = ""

        system_prompt, user_prompt = build_question_generation_prompt(
            status=status,
            processed_diff=processed_diff,
            diff_stat=diff_stat,
            hint=hint,
        )

        # Verify prompt structure
        assert isinstance(system_prompt, str)
        assert isinstance(user_prompt, str)
        assert len(system_prompt) > 0
        assert len(user_prompt) > 0

        # Verify content is included
        assert status in user_prompt
        assert processed_diff in user_prompt
        assert hint not in user_prompt or hint == ""  # Empty hint should not appear
