import logging
import tempfile
from pathlib import Path
from typing import Any, Protocol

import click
from prompt_toolkit import prompt
from rich.panel import Panel

from gac.constants import EnvDefaults
from gac.utils import console

logger = logging.getLogger(__name__)


class PromptFn(Protocol):
    """Protocol for prompt functions that accept keyword arguments."""

    def __call__(self, __msg: str, **kwargs: Any) -> str: ...


def format_token_usage(prompt_tokens: int, completion_tokens: int, reasoning_tokens: int = 0) -> str:
    """Format token usage for display."""
    total = prompt_tokens + completion_tokens + reasoning_tokens
    if reasoning_tokens > 0:
        return f"{prompt_tokens} prompt + {completion_tokens} completion + {reasoning_tokens} reasoning = {total} total"
    return f"{prompt_tokens} prompt + {completion_tokens} completion = {total} total"


def handle_confirmation_loop(
    commit_message: str,
    conversation_messages: list[dict[str, str]],
    quiet: bool,
    model: str,
    prompt_fn: PromptFn | None = None,
) -> tuple[str, str, list[dict[str, str]]]:
    from gac.editor import edit_commit_message_inplace

    _prompt = prompt_fn or click.prompt

    while True:
        response = _prompt(
            "Proceed with commit above? [y/n/r/e/<feedback>]",
            type=str,
            show_default=False,
        ).strip()
        response_lower = response.lower()

        if response_lower in ["y", "yes"]:
            return ("yes", commit_message, conversation_messages)
        if response_lower in ["n", "no"]:
            return ("no", commit_message, conversation_messages)
        if response == "":
            continue
        if response_lower in ["e", "edit"]:
            edited_message = edit_commit_message_inplace(commit_message)
            if edited_message:
                commit_message = edited_message
                conversation_messages[-1] = {"role": "assistant", "content": commit_message}
                logger.info("Commit message edited by user")
                console.print("\n[bold green]Edited commit message:[/bold green]")
                console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
            else:
                console.print("[yellow]Using previous message.[/yellow]")
                console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))
            continue
        if response_lower in ["r", "reroll"]:
            msg = "Please provide an alternative commit message using the same repository context."
            conversation_messages.append({"role": "user", "content": msg})
            console.print("[cyan]Regenerating commit message...[/cyan]")
            return ("regenerate", commit_message, conversation_messages)

        msg = f"Please revise the commit message based on this feedback: {response}"
        conversation_messages.append({"role": "user", "content": msg})
        console.print(f"[cyan]Regenerating commit message with feedback: {response}[/cyan]")
        return ("regenerate", commit_message, conversation_messages)


def execute_commit(
    commit_message: str, no_verify: bool, hook_timeout: int | None = None, signoff: bool = False
) -> None:
    from gac.git import run_git_command

    commit_args = ["commit", "-m", commit_message]
    if no_verify:
        commit_args.append("--no-verify")
    if signoff:
        commit_args.append("--signoff")
    effective_timeout = hook_timeout if hook_timeout and hook_timeout > 0 else EnvDefaults.HOOK_TIMEOUT
    run_git_command(commit_args, timeout=effective_timeout)
    logger.info("Commit created successfully")
    console.print("[green]Commit created successfully[/green]")


def check_token_warning(
    prompt_tokens: int,
    warning_limit: int,
    require_confirmation: bool,
) -> bool:
    if warning_limit and prompt_tokens > warning_limit:
        console.print(
            f"[yellow]⚠️  WARNING: Prompt has {prompt_tokens} tokens (warning threshold: {warning_limit})[/yellow]"
        )
        if require_confirmation:
            proceed = click.confirm("Do you want to continue anyway?", default=True)
            if not proceed:
                console.print("[yellow]Aborted due to large token count.[/yellow]")
                return False
    return True


def display_commit_message(
    commit_message: str,
    prompt_tokens: int,
    model: str,
    quiet: bool,
    completion_tokens: int | None = None,
    reasoning_tokens: int = 0,
) -> None:
    console.print("[bold green]Generated commit message:[/bold green]")
    console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))

    if not quiet:
        if completion_tokens is None:
            from gac.ai_utils import count_tokens

            completion_tokens = count_tokens(commit_message, model)
        console.print(
            f"[dim]Token usage: {format_token_usage(prompt_tokens, completion_tokens, reasoning_tokens)}[/dim]"
        )


def restore_staging(staged_files: list[str], staged_diff: str | None = None) -> None:
    """Restore the git staging area to a previous state.

    Args:
        staged_files: List of file paths that should be staged
        staged_diff: Optional staged diff to reapply for partial staging
    """
    from gac.git import run_git_command

    run_git_command(["reset", "HEAD"])

    if staged_diff:
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
                tmp.write(staged_diff)
                temp_path = Path(tmp.name)
            run_git_command(["apply", "--cached", str(temp_path)])
            return
        except Exception as e:
            logger.warning(f"Failed to reapply staged diff, falling back to file list: {e}")
        finally:
            if temp_path:
                temp_path.unlink(missing_ok=True)

    for file_path in staged_files:
        try:
            run_git_command(["add", file_path])
        except Exception as e:
            logger.warning(f"Failed to restore staging for {file_path}: {e}")


def collect_interactive_answers(questions: list[str]) -> dict[str, str] | None:
    """Collect user answers to generated questions interactively.

    Args:
        questions: List of generated questions

    Returns:
        Dictionary mapping questions to answers, or None if user aborted
    """
    if not questions:
        return {}

    console.print("\n[bold cyan]🤝 Let's clarify your commit intent:[/bold cyan]")
    console.print("[dim]Answer each question, press Enter to skip, or type:[/dim]")
    console.print("[dim]  • 'skip' - skip remaining questions[/dim]")
    console.print("[dim]  • 'quit' - abort interactive mode[/dim]\n")

    answers = {}

    for i, question in enumerate(questions, 1):
        # Display the question with nice formatting
        console.print(f"[bold blue]Question {i}:[/bold blue] {question}")

        try:
            answer = prompt("Your answer: ").strip()

            # Handle special commands
            answer_lower = answer.lower()

            if answer_lower == "quit":
                console.print("\n[yellow]⚠️  Interactive mode aborted by user[/yellow]")
                return None
            elif answer_lower == "skip":
                console.print("[dim]Skipping remaining questions...[/dim]")
                break
            elif answer_lower == "" or answer_lower == "none":
                # User explicitly skipped this question
                console.print("[dim]↳ Skipped[/dim]")
                continue
            else:
                # Valid answer provided
                answers[question] = answer
                console.print("[dim]↳ Got it![/dim]")

        except KeyboardInterrupt:
            # User pressed Ctrl+C
            console.print("\n[yellow]⚠️  Interactive mode aborted by user[/yellow]")
            return None

        console.print()  # Add spacing between questions

    return answers


def format_answers_for_prompt(answers: dict[str, str]) -> str:
    """Format collected answers for inclusion in the commit message prompt.

    Args:
        answers: Dictionary mapping questions to answers

    Returns:
        Formatted string for inclusion in the prompt
    """
    if not answers:
        return ""

    formatted_lines = []
    for question, answer in answers.items():
        formatted_lines.append(f"Q: {question}")
        formatted_lines.append(f"A: {answer}")
        formatted_lines.append("")

    answers_text = "\n".join(formatted_lines).rstrip()

    return (
        f"\n\n<user_answers>\n"
        f"The user provided the following clarifying information:\n\n"
        f"{answers_text}\n\n"
        f"</user_answers>\n\n"
        f"<context_request>Use the user's answers above to craft a more accurate and informative commit message that captures their specific intent and context.</context_request>"
    )
