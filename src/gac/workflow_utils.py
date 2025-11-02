import logging

import click
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


def handle_confirmation_loop(
    commit_message: str,
    conversation_messages: list[dict[str, str]],
    quiet: bool,
    model: str,
) -> tuple[str, list[dict[str, str]]]:
    from rich.panel import Panel

    from gac.utils import edit_commit_message_inplace

    while True:
        response = click.prompt(
            "Proceed with commit above? [y/n/r/e/<feedback>]",
            type=str,
            show_default=False,
        ).strip()
        response_lower = response.lower()

        if response_lower in ["y", "yes"]:
            return ("yes", conversation_messages)
        if response_lower in ["n", "no"]:
            return ("no", conversation_messages)
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
            return ("regenerate", conversation_messages)

        msg = f"Please revise the commit message based on this feedback: {response}"
        conversation_messages.append({"role": "user", "content": msg})
        console.print(f"[cyan]Regenerating commit message with feedback: {response}[/cyan]")
        return ("regenerate", conversation_messages)


def execute_commit(commit_message: str, no_verify: bool) -> None:
    from gac.git import run_git_command

    commit_args = ["commit", "-m", commit_message]
    if no_verify:
        commit_args.append("--no-verify")
    run_git_command(commit_args)
    logger.info("Commit created successfully")
    console.print("[green]Commit created successfully[/green]")


def check_token_warning(
    prompt_tokens: int,
    warning_limit: int,
    require_confirmation: bool,
) -> bool:
    if warning_limit and prompt_tokens > warning_limit:
        console.print(f"[yellow]⚠️  WARNING: Prompt has {prompt_tokens} tokens (limit: {warning_limit})[/yellow]")
        if require_confirmation:
            proceed = click.confirm("Do you want to continue anyway?", default=True)
            if not proceed:
                console.print("[yellow]Aborted due to token limit.[/yellow]")
                return False
    return True


def display_commit_message(commit_message: str, prompt_tokens: int, model: str, quiet: bool) -> None:
    from rich.panel import Panel

    from gac.ai_utils import count_tokens

    console.print("[bold green]Generated commit message:[/bold green]")
    console.print(Panel(commit_message, title="Commit Message", border_style="cyan"))

    if not quiet:
        completion_tokens = count_tokens(commit_message, model)
        total_tokens = prompt_tokens + completion_tokens
        console.print(
            f"[dim]Token usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total[/dim]"
        )
