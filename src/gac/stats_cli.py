"""CLI for viewing gac usage statistics."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gac.stats import get_stats_summary, reset_stats

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def stats(ctx: click.Context) -> None:
    """View your gac usage statistics."""
    if ctx.invoked_subcommand is None:
        ctx.forward(show)


@stats.command()
def show() -> None:
    """Show your gac usage statistics."""
    summary = get_stats_summary()
    total = summary["total_commits"]

    if total == 0:
        console.print("[yellow]No commits yet! Time to start gaccing! 🚀[/yellow]")
        console.print("[dim]Run 'gac' in a git repository to make your first commit.[/dim]")
        return

    # Main stats panel
    today = summary["today_commits"]
    streak = summary["streak"]

    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]{total}[/bold cyan] {'commit' if total == 1 else 'commits'} made with gac!",
            title="🚀 GAC Stats",
            border_style="green",
        )
    )

    # Details table
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("First gac", summary["first_used"])
    table.add_row("Last gac", summary["last_used"])
    table.add_row("Today's gacs", str(today))
    table.add_row("Current streak", f"{streak} day{'s' if streak != 1 else ''}")

    console.print(table)

    # Encouragement message based on usage
    if today > 0:
        if today >= 5:
            console.print("[green]🔥 You're on fire today! Keep those commits flowing![/green]")
        elif streak >= 7:
            console.print("[green]🚀 Wow, a week-long streak! You're a gac machine![/green]")
        else:
            console.print("[green]✨ Nice work today! Every commit counts![/green]")
    elif streak > 0:
        console.print("[yellow]💪 Don't break that streak! Time for a commit![/yellow]")

    console.print()


@stats.command()
def reset() -> None:
    """Reset all statistics (cannot be undone)."""
    console.print("[red]⚠️  This will delete all your gac statistics![/red]")
    console.print("[dim]Total commits, streaks, and history will be lost.[/dim]")
    console.print()

    confirm = click.confirm("Are you sure you want to reset your stats?")
    if confirm:
        reset_stats()
        console.print("[green]Statistics reset. Starting fresh! 🚀[/green]")
    else:
        console.print("[dim]Reset cancelled. Your stats are safe![/dim]")
