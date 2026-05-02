"""CLI for viewing gac usage statistics."""

from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gac.stats import (
    get_current_project_name,
    get_stats_summary,
    load_stats,
    project_activity,
    reset_stats,
    stats_enabled,
)


def _format_tokens(n: int) -> str:
    """Format a token count with thousands separators (e.g. 1,234,567)."""
    return f"{n:,}"


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
    # Check if stats tracking is disabled
    if not stats_enabled():
        console.print("[dim]Stats tracking is currently disabled (GAC_DISABLE_STATS is set to a truthy value).[/dim]")
        console.print("[dim]Unset GAC_DISABLE_STATS or set it to 'false' to start tracking your gacs! 🚀[/dim]")
        return

    summary = get_stats_summary()
    total_gacs = summary.get("total_gacs", 0)
    total_commits = summary.get("total_commits", 0)
    total_tokens = summary.get("total_tokens", 0)

    if total_gacs == 0 and total_commits == 0 and total_tokens == 0:
        console.print("[yellow]No gacs yet! Time to start gaccing! 🚀[/yellow]")
        console.print("[dim]Run 'gac' or 'uvx gac' in a git repository to make your first commit.[/dim]")
        return

    # Main stats panel
    today_gacs = summary.get("today_gacs", 0)
    today_commits = summary.get("today_commits", 0)
    today_tokens = summary.get("today_tokens", 0)
    streak = summary["streak"]
    longest_streak = summary.get("longest_streak", 0)
    biggest_gac_tokens = summary.get("biggest_gac_tokens", 0)
    biggest_gac_date = summary.get("biggest_gac_date")
    peak_daily_gacs = summary.get("peak_daily_gacs", 0)
    peak_daily_commits = summary.get("peak_daily_commits", 0)
    peak_daily_tokens = summary.get("peak_daily_tokens", 0)
    week_gacs = summary.get("week_gacs", 0)
    week_commits = summary.get("week_commits", 0)
    week_tokens = summary.get("week_tokens", 0)
    peak_weekly_gacs = summary.get("peak_weekly_gacs", 0)
    peak_weekly_commits = summary.get("peak_weekly_commits", 0)
    peak_weekly_tokens = summary.get("peak_weekly_tokens", 0)

    # Compute previous peak (excluding today) to distinguish new records from ties
    today_str = datetime.now().strftime("%Y-%m-%d")
    prev_peak_gacs = max((v for d, v in summary.get("daily_gacs", {}).items() if d != today_str), default=0)
    prev_peak_commits = max((v for d, v in summary.get("daily_commits", {}).items() if d != today_str), default=0)
    prev_peak_tokens = max((v for d, v in summary.get("daily_total_tokens", {}).items() if d != today_str), default=0)
    # Previous weekly peak (excluding this week)
    iso_week = datetime.now().isocalendar()
    this_week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    prev_peak_weekly_gacs = max((v for w, v in summary.get("weekly_gacs", {}).items() if w != this_week_key), default=0)
    prev_peak_weekly_commits = max(
        (v for w, v in summary.get("weekly_commits", {}).items() if w != this_week_key), default=0
    )
    prev_peak_weekly_tokens = max(
        (v for w, v in summary.get("weekly_total_tokens", {}).items() if w != this_week_key), default=0
    )
    # Previous longest streak: if current streak equals longest, the previous
    # record is longest_streak minus what today contributed (at most 1 day)
    prev_longest = longest_streak - 1 if streak == longest_streak and streak > 0 else longest_streak

    # Determine high scores for trophy display
    new_peak_gacs = today_gacs > 0 and today_gacs > prev_peak_gacs
    tied_peak_gacs = today_gacs > 0 and today_gacs == prev_peak_gacs
    new_peak_commits = today_commits > 0 and today_commits > prev_peak_commits
    tied_peak_commits = today_commits > 0 and today_commits == prev_peak_commits
    new_peak_tokens = today_tokens > 0 and today_tokens > prev_peak_tokens
    tied_peak_tokens = today_tokens > 0 and today_tokens == prev_peak_tokens
    new_peak_weekly_gacs = week_gacs > 0 and week_gacs > prev_peak_weekly_gacs
    tied_peak_weekly_gacs = week_gacs > 0 and week_gacs == prev_peak_weekly_gacs
    new_peak_weekly_commits = week_commits > 0 and week_commits > prev_peak_weekly_commits
    tied_peak_weekly_commits = week_commits > 0 and week_commits == prev_peak_weekly_commits
    new_peak_weekly_tokens = week_tokens > 0 and week_tokens > prev_peak_weekly_tokens
    tied_peak_weekly_tokens = week_tokens > 0 and week_tokens == prev_peak_weekly_tokens
    new_streak_record = streak > 0 and streak > prev_longest
    tied_streak_record = streak > 0 and streak == prev_longest

    # Detect if today set a new biggest-gac record
    new_biggest_gac = biggest_gac_tokens > 0 and biggest_gac_date == today_str

    console.print()

    # Format the gac'd message (handles pluralization)
    if total_gacs == 1:
        gac_message = "You've gac'd [bold cyan]1[/bold cyan] time"
    else:
        gac_message = f"You've gac'd [bold cyan]{total_gacs}[/bold cyan] times"

    # Add commits info
    if total_commits == 1:
        commit_message = "creating [bold cyan]1[/bold cyan] commit"
    else:
        commit_message = f"creating [bold cyan]{total_commits}[/bold cyan] commits"

    console.print(
        Panel.fit(
            f"{gac_message}, {commit_message}!",
            title="🚀 GAC Stats",
            border_style="green",
        )
    )

    # Details table
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="bold magenta")
    table.add_column("Value", style="bold")

    first_used = "[dim]/[/]".join(f"[bold cyan]{p}[/bold cyan]" for p in summary["first_used"].split("-"))
    last_used = "[dim]/[/]".join(f"[bold cyan]{p}[/bold cyan]" for p in summary["last_used"].split("-"))
    table.add_row("First gac", first_used)
    table.add_row("Last gac", last_used)
    if biggest_gac_tokens > 0:
        token_part = f"[bold cyan]{_format_tokens(biggest_gac_tokens)}[/bold cyan] [cyan]tokens[/cyan]"
        if biggest_gac_date:
            date_part = "[dim]/[/]".join(f"[bold cyan]{p}[/bold cyan]" for p in biggest_gac_date.split("-"))
            display = f"{token_part}  ({date_part})"
        else:
            display = f"{token_part}"
        table.add_row("Biggest gac", display)
    streak_emoji = (
        " 🔥🏆" if new_streak_record and streak >= 5 else " 🏆" if new_streak_record else " 🔥" if streak >= 5 else ""
    )
    table.add_row(
        "Current streak",
        f"[bold cyan]{streak}[/bold cyan] [cyan]day{'s' if streak != 1 else ''}[/cyan]{streak_emoji}",
    )
    table.add_row(
        "Longest streak",
        f"[bold cyan]{longest_streak}[/bold cyan] [cyan]day{'s' if longest_streak != 1 else ''}[/cyan]",
    )

    console.print(table)

    # Activity summary table (today vs peak)
    console.print()
    console.print("[bold]Activity Summary:[/bold]")
    activity_table = Table(show_header=True, box=None)
    activity_table.add_column("Period", style="bold magenta")
    activity_table.add_column("Gacs", style="bold cyan", justify="right")
    activity_table.add_column("Commits", style="bold cyan", justify="right")
    activity_table.add_column("Tokens", style="bold cyan", justify="right")

    activity_table.add_row("Today", str(today_gacs), str(today_commits), _format_tokens(today_tokens))
    activity_table.add_row("Peak Day", str(peak_daily_gacs), str(peak_daily_commits), _format_tokens(peak_daily_tokens))
    activity_table.add_row("This Week", str(week_gacs), str(week_commits), _format_tokens(week_tokens))
    activity_table.add_row(
        "Peak Week", str(peak_weekly_gacs), str(peak_weekly_commits), _format_tokens(peak_weekly_tokens)
    )

    console.print(activity_table)

    # Top projects
    stats_data = load_stats()
    projects = stats_data.get("projects", {})
    if projects:
        console.print()
        console.print("[bold]Top Projects:[/bold]")
        projects_table = Table(show_header=True, box=None)
        projects_table.add_column("Project", style="bold magenta")
        projects_table.add_column("Gacs", style="bold cyan", justify="right")
        projects_table.add_column("Commits", style="bold cyan", justify="right")
        projects_table.add_column("Tokens", style="bold cyan", justify="right")

        sorted_projects = sorted(projects.items(), key=project_activity, reverse=True)

        # Show top 5 projects
        for project, data in sorted_projects[:5]:
            gacs = data.get("gacs", 0)
            commits = data.get("commits", 0)
            tokens = int(data.get("prompt_tokens", 0)) + int(data.get("completion_tokens", 0))
            projects_table.add_row(project, str(gacs), str(commits), _format_tokens(tokens))

        console.print(projects_table)
        console.print()

    # Top models (from summary which includes computed avg_tps)
    top_models = summary.get("top_models", [])
    if top_models:
        console.print("[bold]Top Models:[/bold]")
        models_table = Table(show_header=True, box=None)
        models_table.add_column("Model", style="bold magenta")
        models_table.add_column("Gacs", style="bold cyan", justify="right")
        models_table.add_column("Speed", style="bold cyan", justify="right")
        models_table.add_column("Prompt", style="bold cyan", justify="right")
        models_table.add_column("Completion", style="bold cyan", justify="right")
        models_table.add_column("Reasoning", style="bold cyan", justify="right")
        models_table.add_column("Total", style="bold cyan", justify="right")

        for model_name, data in top_models[:5]:
            gacs = data.get("gacs", 0)
            prompt_t = int(data.get("prompt_tokens", 0))
            completion_t = int(data.get("completion_tokens", 0))
            reasoning_t = int(data.get("reasoning_tokens", 0))
            total_t = prompt_t + completion_t + reasoning_t
            avg_tps = data.get("avg_tps")
            speed_str = f"{avg_tps} tps" if avg_tps is not None else "\u2014"
            reasoning_str = _format_tokens(reasoning_t) if reasoning_t > 0 else "\u2014"
            models_table.add_row(
                model_name,
                str(gacs),
                speed_str,
                _format_tokens(prompt_t),
                _format_tokens(completion_t),
                reasoning_str,
                _format_tokens(total_t),
            )

        console.print(models_table)
        console.print()

    # Celebration and encouragement messages
    any_trophy = (
        new_peak_gacs
        or new_peak_commits
        or new_peak_tokens
        or new_peak_weekly_gacs
        or new_peak_weekly_commits
        or new_peak_weekly_tokens
        or new_streak_record
        or new_biggest_gac
    )
    any_tie = (
        tied_peak_gacs
        or tied_peak_commits
        or tied_peak_tokens
        or tied_peak_weekly_gacs
        or tied_peak_weekly_commits
        or tied_peak_weekly_tokens
        or tied_streak_record
    )

    if today_gacs > 0 or any_trophy or any_tie:
        if new_biggest_gac:
            console.print("[bold yellow]🏆 New biggest gac record![/bold yellow]")
        if new_streak_record:
            console.print("[bold yellow]🏆 New longest streak record![/bold yellow]")
        elif tied_streak_record:
            console.print("[yellow]🥈 Tied your longest streak record![/yellow]")
        if new_peak_gacs:
            console.print("[bold yellow]🏆 New daily high score for gacs![/bold yellow]")
        elif tied_peak_gacs:
            console.print("[yellow]🥈 Tied your daily high score for gacs![/yellow]")
        if new_peak_commits:
            console.print("[bold yellow]🏆 New daily high score for commits![/bold yellow]")
        elif tied_peak_commits:
            console.print("[yellow]🥈 Tied your daily high score for commits![/yellow]")
        if new_peak_tokens:
            console.print("[bold yellow]🏆 New daily high score for tokens![/bold yellow]")
        elif tied_peak_tokens:
            console.print("[yellow]🥈 Tied your daily high score for tokens![/yellow]")
        if new_peak_weekly_gacs:
            console.print("[bold yellow]🏆 New weekly high score for gacs![/bold yellow]")
        elif tied_peak_weekly_gacs:
            console.print("[yellow]🥈 Tied your weekly high score for gacs![/yellow]")
        if new_peak_weekly_commits:
            console.print("[bold yellow]🏆 New weekly high score for commits![/bold yellow]")
        elif tied_peak_weekly_commits:
            console.print("[yellow]🥈 Tied your weekly high score for commits![/yellow]")
        if new_peak_weekly_tokens:
            console.print("[bold yellow]🏆 New weekly high score for tokens![/bold yellow]")
        elif tied_peak_weekly_tokens:
            console.print("[yellow]🥈 Tied your weekly high score for tokens![/yellow]")
        if not (any_trophy or any_tie):
            if today_commits >= 5:
                console.print("[green]🔥 You're on fire today! Keep those commits flowing![/green]")
            elif streak >= 7:
                console.print("[green]🚀 Wow, a week-long streak! You're a gac machine![/green]")
            else:
                console.print("[green]✨ Nice work today! Every gac counts![/green]")
    elif streak > 0:
        console.print("[yellow]💪 Don't break that streak! Time for a gac![/yellow]")

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


@stats.command()
def project() -> None:
    """Show stats for the current project only."""
    project_name = get_current_project_name()
    if not project_name:
        console.print("[red]Error: Not in a git repository.[/red]")
        return

    stats = load_stats()
    projects = stats.get("projects", {})

    project_data = projects.get(project_name, {})

    has_activity = bool(project_data) and any(
        int(project_data.get(field, 0)) > 0 for field in ("gacs", "commits", "prompt_tokens", "completion_tokens")
    )
    if not has_activity:
        console.print(f"[yellow]No gacs yet for project '{project_name}'![/yellow]")
        console.print("[dim]Run 'gac' or 'uvx gac' in this repository to start tracking.[/dim]")
        return

    gacs = project_data.get("gacs", 0)
    commits = project_data.get("commits", 0)
    prompt_t = int(project_data.get("prompt_tokens", 0))
    completion_t = int(project_data.get("completion_tokens", 0))
    total_t = prompt_t + completion_t

    console.print()

    # Format message
    if gacs == 1:
        gac_msg = "You've gac'd [bold cyan]1[/bold cyan] time"
    else:
        gac_msg = f"You've gac'd [bold cyan]{gacs}[/bold cyan] times"

    if commits == 1:
        commit_msg = "created [bold cyan]1[/bold cyan] commit"
    else:
        commit_msg = f"created [bold cyan]{commits}[/bold cyan] commits"

    console.print(
        Panel.fit(
            f"{gac_msg} and {commit_msg} in this project!",
            title=f"🚀 {project_name}",
            border_style="green",
        )
    )

    if total_t > 0:
        console.print()
        token_table = Table(show_header=False, box=None)
        token_table.add_column("Metric", style="bold magenta")
        token_table.add_column("Value", style="bold cyan", justify="right")
        token_table.add_row("Prompt tokens", _format_tokens(prompt_t))
        token_table.add_row("Completion tokens", _format_tokens(completion_t))
        token_table.add_row("Total tokens", _format_tokens(total_t))
        console.print(token_table)

    console.print()
