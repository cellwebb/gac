#!/usr/bin/env python3
"""Interactive mode handling for gac."""

import logging
import re

from rich.console import Console

from gac.ai import generate_commit_message
from gac.config import GACConfig
from gac.git_state_validator import GitState
from gac.workflow_utils import (
    collect_interactive_answers,
    format_answers_for_prompt,
    handle_confirmation_loop,
)

logger = logging.getLogger(__name__)
console = Console()


class InteractiveMode:
    """Handles interactive question generation and user interaction flows."""

    def __init__(self, config: GACConfig):
        self.config = config

    def generate_contextual_questions(
        self,
        model: str,
        git_state: GitState,
        hint: str,
        temperature: float,
        max_tokens: int,
        max_retries: int,
        quiet: bool = False,
    ) -> list[str]:
        """Generate contextual questions about staged changes."""
        from gac.prompt import build_question_generation_prompt

        status = git_state.status
        diff = git_state.processed_diff
        diff_stat = git_state.diff_stat

        try:
            # Build prompts for question generation
            system_prompt, question_prompt = build_question_generation_prompt(
                status=status,
                processed_diff=diff,
                diff_stat=diff_stat,
                hint=hint,
            )

            # Generate questions using existing infrastructure
            logger.info("Generating contextual questions about staged changes...")
            questions_text = generate_commit_message(
                model=model,
                prompt=(system_prompt, question_prompt),
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=max_retries,
                quiet=quiet,
                skip_success_message=True,  # Don't show "Generated commit message" for questions
                task_description="contextual questions",
            )

            # Parse the response to extract individual questions
            questions = self._parse_questions_from_response(questions_text)

            logger.info(f"Generated {len(questions)} contextual questions")
            return questions

        except Exception as e:
            logger.warning(f"Failed to generate contextual questions, proceeding without them: {e}")
            if not quiet:
                console.print("[yellow]⚠️  Could not generate contextual questions, proceeding normally[/yellow]\n")
            return []

    def _parse_questions_from_response(self, response: str) -> list[str]:
        """Parse the AI response to extract individual questions from a numbered list.

        Args:
            response: The raw response from the AI model

        Returns:
            A list of cleaned questions
        """
        questions = []
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match numbered list format (e.g., "1. Question text?" or "1) Question text?")
            match = re.match(r"^\d+\.\s+(.+)$", line)
            if not match:
                match = re.match(r"^\d+\)\s+(.+)$", line)

            if match:
                question = match.group(1).strip()
                # Remove any leading symbols like •, -, *
                question = re.sub(r"^[•\-*]\s+", "", question)
                if question and question.endswith("?"):
                    questions.append(question)
            elif line.endswith("?") and len(line) > 5:  # Fallback for non-numbered questions
                questions.append(line)

        return questions

    def handle_interactive_flow(
        self,
        model: str,
        user_prompt: str,
        git_state: GitState,
        hint: str,
        conversation_messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        max_retries: int,
        quiet: bool = False,
    ) -> None:
        """Handle the complete interactive flow for collecting user context."""
        try:
            questions = self.generate_contextual_questions(
                model=model,
                git_state=git_state,
                hint=hint,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=max_retries,
                quiet=quiet,
            )

            if not questions:
                return

            # Collect answers interactively
            answers = collect_interactive_answers(questions)

            if answers is None:
                # User aborted interactive mode
                if not quiet:
                    console.print("[yellow]Proceeding with commit without additional context[/yellow]\n")
            elif answers:
                # User provided some answers, format them for the prompt
                answers_context = format_answers_for_prompt(answers)
                enhanced_user_prompt = user_prompt + answers_context

                # Update the conversation messages with the enhanced prompt
                if conversation_messages and conversation_messages[-1]["role"] == "user":
                    conversation_messages[-1]["content"] = enhanced_user_prompt

                logger.info(f"Collected answers for {len(answers)} questions")
            else:
                # User skipped all questions
                if not quiet:
                    console.print("[dim]No answers provided, proceeding with original context[/dim]\n")

        except Exception as e:
            logger.warning(f"Failed to generate contextual questions, proceeding without them: {e}")
            if not quiet:
                console.print("[yellow]⚠️  Could not generate contextual questions, proceeding normally[/yellow]\n")

    def handle_single_commit_confirmation(
        self,
        model: str,
        commit_message: str,
        conversation_messages: list[dict[str, str]],
        quiet: bool = False,
    ) -> tuple[str, str]:
        """Handle confirmation loop for single commit. Returns (final_message, decision).

        Decision is one of: "yes", "no", "regenerate"
        """
        decision, final_message, _ = handle_confirmation_loop(commit_message, conversation_messages, quiet, model)

        return final_message, decision
