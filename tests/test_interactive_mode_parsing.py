"""Unit tests for question parsing functionality in interactive_mode.py."""

from unittest.mock import MagicMock, patch

from gac.config import GACConfig
from gac.interactive_mode import InteractiveMode


class TestParseQuestionsFromResponse:
    """Tests for the _parse_questions_from_response method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.interactive_mode = InteractiveMode(self.config)

    def test_numbered_list_format_dot(self):
        """Test parsing numbered list with dot separator."""
        response = "1. What changed?\n2. Why did it change?\n3. How was it tested?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What changed?", "Why did it change?", "How was it tested?"]
        assert questions == expected

    def test_numbered_list_format_paren(self):
        """Test parsing numbered list with parenthesis separator."""
        response = "1) What files were modified?\n2) What is the impact?\n3) Are there breaking changes?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What files were modified?", "What is the impact?", "Are there breaking changes?"]
        assert questions == expected

    def test_mixed_numbered_formats(self):
        """Test parsing mixed numbered formats in the same response."""
        response = "1. First question?\n2) Second question?\n3. Third question?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["First question?", "Second question?", "Third question?"]
        assert questions == expected

    def test_bullet_points(self):
        """Test parsing bullet points with various symbols."""
        response = "• What was the motivation?\n- What are the side effects?\n* How does this help?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        # Note: Bullet points are only removed when they appear after numbered format
        # Pure bullet points without numbers are treated as fallback questions
        expected = ["• What was the motivation?", "- What are the side effects?", "* How does this help?"]
        assert questions == expected

    def test_fallback_format_questions_only(self):
        """Test fallback format for non-numbered questions."""
        response = "What is the purpose of this change?\nHow does this improve the codebase?\nAre there any risks?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = [
            "What is the purpose of this change?",
            "How does this improve the codebase?",
            "Are there any risks?",
        ]
        assert questions == expected

    def test_numbered_questions_with_bullet_points(self):
        """Test numbered questions that also have bullet point symbols."""
        response = "1. • What functionality was added?\n2. - What bugs were fixed?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What functionality was added?", "What bugs were fixed?"]
        assert questions == expected

    def test_empty_response(self):
        """Test handling of empty responses."""
        response = ""
        questions = self.interactive_mode._parse_questions_from_response(response)
        assert questions == []

    def test_only_whitespace(self):
        """Test handling of responses with only whitespace."""
        response = "   \n\n   \t\n   "
        questions = self.interactive_mode._parse_questions_from_response(response)
        assert questions == []

    def test_malformed_responses(self):
        """Test handling of malformed responses."""
        response = "This is not a question\nSome random text\nAnother line"
        questions = self.interactive_mode._parse_questions_from_response(response)
        assert questions == []

    def test_questions_without_question_marks(self):
        """Test that questions without question marks are excluded."""
        response = "1. This is not a question\n2. This is also not a question\n3. This is a proper question?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["This is a proper question?"]
        assert questions == expected

    def test_questions_too_short(self):
        """Test that very short numbered questions are still included (length check only applies to fallback)."""
        response = "1. A?\n2. Why?\n3. How about this very long question that should be included?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        # Note: Short numbered questions are included because length check only applies to non-numbered fallback
        expected = ["A?", "Why?", "How about this very long question that should be included?"]
        assert questions == expected

    def test_questions_with_extra_whitespace(self):
        """Test handling of questions with extra whitespace."""
        response = "  1.   What changed?   \n  2)   Why change it?   \n"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What changed?", "Why change it?"]
        assert questions == expected

    def test_multiline_questions(self):
        """Test handling of questions that span multiple lines - each line processed separately."""
        response = "1. What changed and why is\nthis on multiple lines?\n2. Second question?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        # The current implementation treats each line separately, so the multiline gets split
        expected = ["this on multiple lines?", "Second question?"]
        assert questions == expected

    def test_real_world_scenario(self):
        """Test a real-world AI response scenario."""
        response = """Based on your changes, here are some questions to help provide better context:

1. What specific functionality did you add?
2. Why was this change necessary?
3) Are there any breaking changes?
4. • How does this improve the user experience?
5. - What testing was done?

Please provide as much detail as possible."""
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = [
            "What specific functionality did you add?",
            "Why was this change necessary?",
            "Are there any breaking changes?",
            "How does this improve the user experience?",
            "What testing was done?",
        ]
        assert questions == expected

    def test_numbered_questions_with_leading_text(self):
        """Test handling of numbered questions with leading explanatory text."""
        response = "Here are some questions:\n\n1. What changed?\n2. Why was it changed?\n\nThanks!"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What changed?", "Why was it changed?"]
        assert questions == expected

    def test_mixed_content_with_questions_and_statements(self):
        """Test mixed content with both questions and statements."""
        response = "This is an introduction.\n1. What changed?\nThis is additional context.\n2. Why change it?\nMore context here.\n3. How tested?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["What changed?", "Why change it?", "How tested?"]
        assert questions == expected

    def test_questions_with_special_characters(self):
        """Test questions containing special characters."""
        response = "1. What's the impact on API v2?\n2. How does this affect user's data?\n3. Are there any security implications?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = [
            "What's the impact on API v2?",
            "How does this affect user's data?",
            "Are there any security implications?",
        ]
        assert questions == expected

    def test_empty_lines_between_questions(self):
        """Test handling of empty lines between questions."""
        response = "1. First question?\n\n2. Second question?\n\n3. Third question?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["First question?", "Second question?", "Third question?"]
        assert questions == expected

    def test_fallback_with_varying_question_lengths(self):
        """Test fallback format with questions of varying lengths."""
        response = "Short?\nThis is a much longer question that provides more context and detail?\nMedium length?"
        questions = self.interactive_mode._parse_questions_from_response(response)
        # Note: "Short?" has length 6, so it passes the > 5 check and gets included
        expected = ["Short?", "This is a much longer question that provides more context and detail?", "Medium length?"]
        assert questions == expected

    def test_unicode_characters_in_questions(self):
        """Test questions containing unicode characters."""
        response = (
            "1. What changed in the café?\n2. How does this affect naïve users?\n3. Are there any compliance issues?"
        )
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = [
            "What changed in the café?",
            "How does this affect naïve users?",
            "Are there any compliance issues?",
        ]
        assert questions == expected

    def test_questions_with_numbers_in_text(self):
        """Test questions containing numbers within the text."""
        response = (
            "1. How does this affect v2.1 users?\n2. What about API version 3.0?\n3. Should we support version 4?"
        )
        questions = self.interactive_mode._parse_questions_from_response(response)
        expected = ["How does this affect v2.1 users?", "What about API version 3.0?", "Should we support version 4?"]
        assert questions == expected


class TestGenerateContextualQuestions:
    """Tests for the generate_contextual_questions method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.interactive_mode = InteractiveMode(self.config)

    def test_generate_contextual_questions_success(self):
        """Test successful generation of contextual questions."""
        # Mock dependencies - patch where they are used
        with (
            patch("gac.prompt.build_question_generation_prompt") as mock_build_prompt,
            patch("gac.interactive_mode.generate_commit_message") as mock_generate,
        ):
            mock_build_prompt.return_value = ("system_prompt", "question_prompt")
            mock_generate.return_value = "1. What changed?\n2. Why did it change?"

            # Create mock git state
            mock_git_state = MagicMock()
            mock_git_state.status = "modified"
            mock_git_state.processed_diff = "diff content"
            mock_git_state.diff_stat = "1 file changed"

            # Test the method
            questions = self.interactive_mode.generate_contextual_questions(
                model="anthropic:claude-3-sonnet-20240229",
                git_state=mock_git_state,
                hint="test hint",
                temperature=0.7,
                max_tokens=100,
                max_retries=3,
                quiet=False,
            )

            # Verify results
            assert questions == ["What changed?", "Why did it change?"]
            mock_build_prompt.assert_called_once()
            mock_generate.assert_called_once()

    def test_generate_contextual_questions_exception_handling(self):
        """Test exception handling in generate_contextual_questions."""
        # Mock build_question_generation_prompt to raise an exception
        with patch("gac.prompt.build_question_generation_prompt", side_effect=Exception("Test error")):
            # Create mock git state
            mock_git_state = MagicMock()

            # Test the method handles exceptions gracefully
            questions = self.interactive_mode.generate_contextual_questions(
                model="anthropic:claude-3-sonnet-20240229",
                git_state=mock_git_state,
                hint="test hint",
                temperature=0.7,
                max_tokens=100,
                max_retries=3,
                quiet=True,  # Test quiet mode
            )

            # Should return empty list on exception
            assert questions == []

    def test_generate_contextual_questions_empty_response(self):
        """Test handling of empty AI response."""
        # Mock dependencies
        with (
            patch("gac.prompt.build_question_generation_prompt") as mock_build_prompt,
            patch("gac.ai.generate_commit_message") as mock_generate,
        ):
            mock_build_prompt.return_value = ("system_prompt", "question_prompt")
            mock_generate.return_value = ""  # Empty response

            # Create mock git state
            mock_git_state = MagicMock()

            # Test the method
            questions = self.interactive_mode.generate_contextual_questions(
                model="anthropic:claude-3-sonnet-20240229",
                git_state=mock_git_state,
                hint="test hint",
                temperature=0.7,
                max_tokens=100,
                max_retries=3,
                quiet=False,
            )

            # Should return empty list for empty response
            assert questions == []
