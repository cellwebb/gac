"""CLI for weekly gac activity reports."""

from datetime import datetime, timedelta
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gac.stats import load_stats, stats_enabled

console = Console()

# Unicode block characters for bar charts (8 sub-levels per cell)
_BAR_BLOCKS = " ▏▎▍▌▋▊▉█"


def _bar(value: float, max_value: float, width: int = 20) -> str:
    """Render a Unicode bar chart segment.

    Returns a Rich-formatted string with cyan coloring.
    """
    if max_value <= 0:
        return "[dim]─" * width + "[/dim]"
    ratio = min(value / max_value, 1.0)
    total_units = width * 8  # 8 sub-levels per character
    filled = round(ratio * total_units)
    full_chars = filled // 8
    remainder = filled % 8
    bar = "█" * full_chars
    if remainder:
        bar += _BAR_BLOCKS[remainder]
    # Pad with spaces
    bar = bar.ljust(width)
    return f"[cyan]{bar}[/cyan]"


def _fmt(n: int) -> str:
    """Format a number with thousands separators."""
    return f"{n:,}"


def _day_name(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to a short day name like 'Mon'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%a")
    except ValueError:
        return "???"


@click.command()
@click.option("--weeks", default=1, type=click.IntRange(min=1), help="Number of weeks to report on.", show_default=True)
def report(weeks: int) -> None:
    """Show a weekly activity report with visual charts."""
    if not stats_enabled():
        console.print("[dim]Stats tracking is currently disabled.[/dim]")
        return

    stats = load_stats()
    daily_gacs: dict[str, int] = stats.get("daily_gacs", {})
    daily_commits: dict[str, int] = stats.get("daily_commits", {})
    daily_total_tokens: dict[str, int] = {}

    daily_prompt = stats.get("daily_prompt_tokens", {})
    daily_completion = stats.get("daily_completion_tokens", {})
    daily_reasoning = stats.get("daily_reasoning_tokens", {})
    # completion_tokens excludes reasoning (normalized at provider parse time),
    # so total = prompt + completion + reasoning (three distinct numbers).
    for day_key in set(daily_prompt) | set(daily_completion) | set(daily_reasoning):
        daily_total_tokens[day_key] = (
            daily_prompt.get(day_key, 0) + daily_completion.get(day_key, 0) + daily_reasoning.get(day_key, 0)
        )

    if not daily_gacs and not daily_commits and not daily_total_tokens:
        console.print("[yellow]No activity yet! Time to start gaccing! 🚀[/yellow]")
        return

    today = datetime.now()
    # Build the date range: last N*7 days ending today
    num_days = weeks * 7
    start_date = today - timedelta(days=num_days - 1)

    # Collect daily data for the range
    days: list[str] = []
    gacs_list: list[int] = []
    commits_list: list[int] = []
    tokens_list: list[int] = []

    for i in range(num_days):
        d = start_date + timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        days.append(key)
        gacs_list.append(daily_gacs.get(key, 0))
        commits_list.append(daily_commits.get(key, 0))
        tokens_list.append(daily_total_tokens.get(key, 0))

    max_gacs = max(gacs_list) if gacs_list else 0
    max_commits = max(commits_list) if commits_list else 0
    max_tokens = max(tokens_list) if tokens_list else 0

    # ── Header ──────────────────────────────────────────────────────
    start_fmt = start_date.strftime("%b %d")
    end_fmt = today.strftime("%b %d")
    total_gacs = sum(gacs_list)
    total_commits = sum(commits_list)
    total_tokens = sum(tokens_list)

    console.print()
    console.print(
        Panel.fit(
            f"{start_fmt} → {end_fmt}: "
            f"[bold cyan]{total_gacs}[/bold cyan] gacs, "
            f"[bold cyan]{total_commits}[/bold cyan] commits, "
            f"[bold cyan]{_fmt(total_tokens)}[/bold cyan] tokens",
            title="📊 GAC Report",
            border_style="green",
        )
    )

    # ── Daily activity chart ────────────────────────────────────────
    console.print()
    console.print("[bold]Daily Activity[/bold]")
    chart = Table(show_header=True, box=None, padding=(0, 1))
    chart.add_column("Day", style="bold magenta", width=3)
    chart.add_column("Date", style="dim", width=10)
    chart.add_column("Gacs", style="bold cyan", justify="right", width=5)
    chart.add_column("Gac Bar", width=22)
    chart.add_column("Commits", style="bold cyan", justify="right", width=7)
    chart.add_column("Commit Bar", width=22)

    for i, key in enumerate(days):
        day_abbr = _day_name(key)
        # Highlight today
        is_today = key == today.strftime("%Y-%m-%d")
        day_style = "[bold]" if is_today else ""
        day_close = "[/bold]" if is_today else ""

        g = gacs_list[i]
        c = commits_list[i]
        g_bar = _bar(g, max_gacs, width=20)
        c_bar = _bar(c, max_commits, width=20)

        date_display = "[dim]/[/]".join(f"[bold cyan]{p}[/bold cyan]" for p in key.split("-"))

        chart.add_row(
            f"{day_style}{day_abbr}{day_close}",
            date_display,
            str(g),
            g_bar,
            str(c),
            c_bar,
        )

    console.print(chart)

    # ── Token heatmap row ────────────────────────────────────────────
    console.print()
    console.print("[bold]Token Usage[/bold]")
    token_chart = Table(show_header=True, box=None, padding=(0, 1))
    token_chart.add_column("Day", style="bold magenta", width=3)
    token_chart.add_column("Date", style="dim", width=10)
    token_chart.add_column("Tokens", style="bold cyan", justify="right", width=12)
    token_chart.add_column("Token Bar", width=42)

    for i, key in enumerate(days):
        day_abbr = _day_name(key)
        is_today = key == today.strftime("%Y-%m-%d")
        day_style = "[bold]" if is_today else ""
        day_close = "[/bold]" if is_today else ""

        t = tokens_list[i]
        t_bar = _bar(t, max_tokens, width=40)

        date_display = "[dim]/[/]".join(f"[bold cyan]{p}[/bold cyan]" for p in key.split("-"))

        token_chart.add_row(
            f"{day_style}{day_abbr}{day_close}",
            date_display,
            _fmt(t),
            t_bar,
        )

    console.print(token_chart)

    # ── Week-over-week comparison (only for multi-week reports) ──────
    if weeks > 1:
        console.print()
        console.print("[bold]Weekly Breakdown[/bold]")
        week_table = Table(show_header=True, box=None, padding=(0, 1))
        week_table.add_column("Week", style="bold magenta")
        week_table.add_column("Gacs", style="bold cyan", justify="right")
        week_table.add_column("Commits", style="bold cyan", justify="right")
        week_table.add_column("Tokens", style="bold cyan", justify="right")
        week_table.add_column("Δ Gacs", justify="right")
        week_table.add_column("Δ Tokens", justify="right")

        # Compute weekly totals FROM the daily data in the report window
        # (not from stored weekly_* aggregates, which span full ISO weeks
        # and can include activity outside the visible date range)
        window_weekly: dict[str, dict[str, int]] = {}  # week_key -> {gacs, commits, tokens}
        for i, _key in enumerate(days):
            iso = (start_date + timedelta(days=i)).isocalendar()
            wk_key = f"{iso[0]}-W{iso[1]:02d}"
            if wk_key not in window_weekly:
                window_weekly[wk_key] = {"gacs": 0, "commits": 0, "tokens": 0}
            window_weekly[wk_key]["gacs"] += gacs_list[i]
            window_weekly[wk_key]["commits"] += commits_list[i]
            window_weekly[wk_key]["tokens"] += tokens_list[i]

        # Preserve insertion order (chronological)
        iso_weeks = list(window_weekly.keys())

        prev_gacs = None
        prev_tokens = None
        for wk_key in iso_weeks:
            wk = window_weekly[wk_key]
            wg = wk["gacs"]
            wc = wk["commits"]
            wt = wk["tokens"]

            # Compute deltas
            if prev_gacs is not None:
                dg = wg - prev_gacs
                dt_val = wt - (prev_tokens or 0)
                dg_str = f"[green]+{dg}[/green]" if dg > 0 else f"[red]{dg}[/red]" if dg < 0 else "[dim]0[/dim]"
                dt_str = (
                    f"[green]+{_fmt(dt_val)}[/green]"
                    if dt_val > 0
                    else f"[red]{_fmt(dt_val)}[/red]"
                    if dt_val < 0
                    else "[dim]0[/dim]"
                )
            else:
                dg_str = "[dim]—[/dim]"
                dt_str = "[dim]—[/dim]"

            week_table.add_row(wk_key, str(wg), str(wc), _fmt(wt), dg_str, dt_str)
            prev_gacs = wg
            prev_tokens = wt

        console.print(week_table)

    # ── Top projects this period ─────────────────────────────────────
    projects = stats.get("projects", {})
    if projects:
        # Filter projects with activity in the period
        active_projects: list[tuple[str, dict[str, Any]]] = []
        for name, data in projects.items():
            g = int(data.get("gacs", 0))
            c = int(data.get("commits", 0))
            if g > 0 or c > 0:
                active_projects.append((name, data))

        if active_projects:
            console.print()
            console.print("[bold]Top Projects [dim](all-time)[/dim][/bold]")
            proj_table = Table(show_header=True, box=None, padding=(0, 1))
            proj_table.add_column("Project", style="bold magenta")
            proj_table.add_column("Gacs", style="bold cyan", justify="right")
            proj_table.add_column("Commits", style="bold cyan", justify="right")
            proj_table.add_column("Tokens", style="bold cyan", justify="right")

            from gac.stats import project_activity

            for name, data in sorted(active_projects, key=project_activity, reverse=True)[:5]:
                g = int(data.get("gacs", 0))
                c = int(data.get("commits", 0))
                t = (
                    int(data.get("prompt_tokens", 0))
                    + int(data.get("completion_tokens", 0))
                    + int(data.get("reasoning_tokens", 0))
                )
                proj_table.add_row(name, str(g), str(c), _fmt(t))

            console.print(proj_table)

    # ── Top models this period ───────────────────────────────────────
    models = stats.get("models", {})
    if models:
        active_models: list[tuple[str, dict[str, Any]]] = []
        for name, data in models.items():
            if int(data.get("gacs", 0)) > 0:
                active_models.append((name, data))

        if active_models:
            console.print()
            console.print("[bold]Top Models [dim](all-time)[/dim][/bold]")
            model_table = Table(show_header=True, box=None, padding=(0, 1))
            model_table.add_column("Model", style="bold magenta")
            model_table.add_column("Gacs", style="bold cyan", justify="right")
            model_table.add_column("Avg Speed", style="bold cyan", justify="right")
            model_table.add_column("Tokens", style="bold cyan", justify="right")

            from gac.stats import model_activity

            for name, data in sorted(active_models, key=model_activity, reverse=True)[:5]:
                g = int(data.get("gacs", 0))
                pt = int(data.get("prompt_tokens", 0))
                ct = int(data.get("completion_tokens", 0))
                rt = int(data.get("reasoning_tokens", 0))
                total = pt + ct + rt
                dur = int(data.get("total_duration_ms", 0))
                dur_count = int(data.get("duration_count", 0))
                timed_ct = int(data.get("timed_completion_tokens", 0))
                if dur > 0 and dur_count > 0:
                    avg_tps = round(timed_ct * 1000 / dur)
                    speed = f"{avg_tps} tps"
                else:
                    speed = "—"
                model_table.add_row(name, str(g), speed, _fmt(total))

            console.print(model_table)

    # ── Fun footer ───────────────────────────────────────────────────
    console.print()
    avg_gacs = total_gacs / num_days if num_days > 0 else 0
    if avg_gacs >= 5:
        console.print("[green]🔥 Absolute gac machine this week![/green]")
    elif avg_gacs >= 2:
        console.print("[green]🚀 Solid productivity! Keep it up![/green]")
    elif avg_gacs >= 1:
        console.print("[green]✨ Nice consistency — every day counts![/green]")
    elif total_gacs > 0:
        console.print("[yellow]💪 A quiet week, but you showed up![/yellow]")
    elif total_tokens > 0:
        console.print("[yellow]💭 Some exploration this week — time to commit![/yellow]")
    else:
        console.print("[dim]😴 No activity this period. Time to gac![/dim]")
    console.print()
