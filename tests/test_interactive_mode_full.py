"""Full functional tests for interactive_mode.py main workflow methods."""

import logging
from unittest.mock import MagicMock, patch

from gac.config import GACConfig
from gac.interactive_mode import InteractiveMode


class TestHandleInteractiveFlow:
    """Tests for the handle_interactive_flow method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.interactive_mode = InteractiveMode(self.config)

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    @patch("gac.interactive_mode.format_answers_for_prompt")
    def test_handle_interactive_flow_with_questions_and_answers(
        self, mock_format_answers, mock_collect_answers, mock_generate, caplog
    ):
        """Test complete flow with questions generated and user provides answers."""
        caplog.set_level(logging.INFO)
        # Mock dependencies
        mock_generate.return_value = "1. What changed?\n2. Why did it change?"
        mock_collect_answers.return_value = ["Files were modified", "To fix a bug"]
        mock_format_answers.return_value = "\n\nAdditional context: Files were modified to fix a bug."

        # Create mock git state
        mock_git_state = MagicMock()
        mock_git_state.status = "modified"
        mock_git_state.processed_diff = "diff content"
        mock_git_state.diff_stat = "1 file changed"

        # Create conversation messages
        conversation_messages = [{"role": "user", "content": "original prompt"}]

        # Test the method
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=conversation_messages,
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=False,
        )

        # Verify the flow
        mock_generate.assert_called_once()
        mock_collect_answers.assert_called_once_with(["What changed?", "Why did it change?"])
        mock_format_answers.assert_called_once_with(["Files were modified", "To fix a bug"])

        # Verify conversation was updated
        assert (
            conversation_messages[-1]["content"]
            == "Generate commit message\n\nAdditional context: Files were modified to fix a bug."
        )

        # Verify logging
        assert "Generated 2 contextual questions" in caplog.text
        assert "Collected answers for 2 questions" in caplog.text

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    def test_handle_interactive_flow_no_questions_generated(self, mock_collect_answers, mock_generate, caplog):
        """Test when no questions are generated (empty response)."""
        # Mock dependencies
        mock_generate.return_value = ""  # Empty response
        mock_collect_answers.return_value = None

        # Create mock git state
        mock_git_state = MagicMock()

        # Create conversation messages
        conversation_messages = [{"role": "user", "content": "original prompt"}]

        # Test the method
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=conversation_messages,
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=False,
        )

        # Verify no interactive collection happened
        mock_collect_answers.assert_not_called()
        # Conversation should be unchanged
        assert conversation_messages == [{"role": "user", "content": "original prompt"}]

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    def test_handle_interactive_flow_user_aborted(self, mock_collect_answers, mock_generate, capsys):
        """Test when user aborts interactive mode."""
        # Mock dependencies
        mock_generate.return_value = "1. What changed?"
        mock_collect_answers.return_value = None  # User aborted

        # Create mock git state
        mock_git_state = MagicMock()

        # Test the method
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=[],
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=False,
        )

        # Verify abort message was printed
        captured = capsys.readouterr()
        assert "Proceeding with commit without additional context" in captured.out

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    @patch("gac.interactive_mode.format_answers_for_prompt")
    def test_handle_interactive_flow_user_skipped_all_questions(
        self, mock_format_answers, mock_collect_answers, mock_generate, capsys
    ):
        """Test when user skips all questions."""
        # Mock dependencies
        mock_generate.return_value = "1. What changed?\n2. Why?"
        mock_collect_answers.return_value = []  # Empty list - user skipped all
        mock_format_answers.return_value = ""

        # Create mock git state
        mock_git_state = MagicMock()

        # Test the method
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=[],
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=False,
        )

        # Verify skip message was printed
        captured = capsys.readouterr()
        assert "No answers provided, proceeding with original context" in captured.out

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    def test_handle_interactive_flow_quiet_mode(self, mock_collect_answers, mock_generate, capsys):
        """Test that quiet mode suppresses console output."""
        # Mock dependencies
        mock_generate.return_value = ""  # Empty response
        mock_collect_answers.return_value = None

        # Create mock git state
        mock_git_state = MagicMock()

        # Test the method with quiet=True
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=[],
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=True,  # Quiet mode
        )

        # Verify no console output was produced
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    @patch("gac.interactive_mode.generate_commit_message")
    @patch("gac.interactive_mode.collect_interactive_answers")
    @patch("gac.interactive_mode.format_answers_for_prompt")
    def test_handle_interactive_flow_no_conversation_update(
        self, mock_format_answers, mock_collect_answers, mock_generate
    ):
        """Test when there's no conversation messages to update."""
        # Mock dependencies
        mock_generate.return_value = "1. What changed?"
        mock_collect_answers.return_value = ["Files modified"]
        mock_format_answers.return_value = "\n\nContext: Files modified."

        # Create mock git state
        mock_git_state = MagicMock()

        # Test with empty conversation messages
        conversation_messages = []
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=conversation_messages,
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=True,
        )

        # Conversation should remain empty since there's no last message to update
        assert conversation_messages == []

    @patch("gac.interactive_mode.generate_commit_message")
    def test_handle_interactive_flow_exception_handling(self, mock_generate, capsys, caplog):
        """Test exception handling in handle_interactive_flow."""
        caplog.set_level(logging.WARNING)
        # Mock generate_commit_message to raise exception
        mock_generate.side_effect = Exception("Test exception")

        # Create mock git state
        mock_git_state = MagicMock()

        # Test the method
        self.interactive_mode.handle_interactive_flow(
            model="anthropic:claude-3-sonnet-20240229",
            user_prompt="Generate commit message",
            git_state=mock_git_state,
            hint="test hint",
            conversation_messages=[],
            temperature=0.7,
            max_tokens=100,
            max_retries=3,
            quiet=False,
        )

        # Verify warning was logged and printed
        assert "Failed to generate contextual questions" in caplog.text
        captured = capsys.readouterr()
        assert "Could not generate contextual questions" in captured.out


class TestHandleSingleCommitConfirmation:
    """Tests for the handle_single_commit_confirmation method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GACConfig()
        self.interactive_mode = InteractiveMode(self.config)

    @patch("gac.interactive_mode.handle_confirmation_loop")
    def test_handle_single_commit_confirmation_yes_decision(self, mock_handle_confirmation):
        """Test confirmation with yes decision."""
        # Mock handle_confirmation_loop to return "yes" decision
        mock_handle_confirmation.return_value = ("yes", "final commit message", None)

        # Test the method
        final_message, decision = self.interactive_mode.handle_single_commit_confirmation(
            model="anthropic:claude-3-sonnet-20240229",
            commit_message="Initial commit message",
            conversation_messages=[],
            quiet=False,
        )

        # Verify results
        assert final_message == "final commit message"
        assert decision == "yes"
        mock_handle_confirmation.assert_called_once()

    @patch("gac.interactive_mode.handle_confirmation_loop")
    def test_handle_single_commit_confirmation_no_decision(self, mock_handle_confirmation):
        """Test confirmation with no decision."""
        # Mock handle_confirmation_loop to return "no" decision
        mock_handle_confirmation.return_value = ("no", "rejected message", None)

        # Test the method
        final_message, decision = self.interactive_mode.handle_single_commit_confirmation(
            model="anthropic:claude-3-sonnet-20240229",
            commit_message="Initial commit message",
            conversation_messages=[],
            quiet=False,
        )

        # Verify results
        assert final_message == "rejected message"
        assert decision == "no"

    @patch("gac.interactive_mode.handle_confirmation_loop")
    def test_handle_single_commit_confirmation_regenerate_decision(self, mock_handle_confirmation):
        """Test confirmation with regenerate decision."""
        # Mock handle_confirmation_loop to return "regenerate" decision
        mock_handle_confirmation.return_value = ("regenerate", "regenerated message", None)

        # Test the method
        final_message, decision = self.interactive_mode.handle_single_commit_confirmation(
            model="anthropic:claude-3-sonnet-20240229",
            commit_message="Initial commit message",
            conversation_messages=[],
            quiet=False,
        )

        # Verify results
        assert final_message == "regenerated message"
        assert decision == "regenerate"

    @patch("gac.interactive_mode.handle_confirmation_loop")
    def test_handle_single_commit_confirmation_quiet_mode(self, mock_handle_confirmation):
        """Test confirmation in quiet mode."""
        # Mock handle_confirmation_loop
        mock_handle_confirmation.return_value = ("yes", "final message", None)

        # Test the method with quiet=True
        final_message, decision = self.interactive_mode.handle_single_commit_confirmation(
            model="anthropic:claude-3-sonnet-20240229",
            commit_message="Initial commit message",
            conversation_messages=[],
            quiet=True,
        )

        # Verify quiet flag was passed through
        mock_handle_confirmation.assert_called_once_with(
            "Initial commit message", [], True, "anthropic:claude-3-sonnet-20240229"
        )
        assert final_message == "final message"
        assert decision == "yes"

    @patch("gac.interactive_mode.handle_confirmation_loop")
    def test_handle_single_commit_confirmation_with_conversation(self, mock_handle_confirmation):
        """Test confirmation with existing conversation messages."""
        # Mock handle_confirmation_loop
        mock_handle_confirmation.return_value = ("yes", "final message", None)

        # Create conversation messages
        conversation_messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Generate a commit message"},
        ]

        # Test the method
        final_message, decision = self.interactive_mode.handle_single_commit_confirmation(
            model="anthropic:claude-3-sonnet-20240229",
            commit_message="Initial commit message",
            conversation_messages=conversation_messages,
            quiet=False,
        )

        # Verify conversation was passed through
        mock_handle_confirmation.assert_called_once_with(
            "Initial commit message", conversation_messages, False, "anthropic:claude-3-sonnet-20240229"
        )
        assert final_message == "final message"
        assert decision == "yes"
