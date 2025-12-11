"""CLI for managing custom system prompts."""

import logging
import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()

GAC_CONFIG_DIR = Path.home() / ".config" / "gac"
CUSTOM_PROMPT_FILE = GAC_CONFIG_DIR / "custom_system_prompt.txt"


def get_active_custom_prompt() -> tuple[str | None, str | None]:
    """Return (content, source) for active custom prompt, or (None, None) if none.

    Returns:
        Tuple of (content, source) where:
        - content: The custom prompt text, or None if using default
        - source: Human-readable description of where the prompt came from, or None if using default
    """
    # Check GAC_SYSTEM_PROMPT_PATH env var first (highest precedence)
    env_path = os.getenv("GAC_SYSTEM_PROMPT_PATH")
    if env_path:
        env_file = Path(env_path)
        if env_file.exists():
            try:
                content = env_file.read_text(encoding="utf-8")
                return content, f"GAC_SYSTEM_PROMPT_PATH={env_path}"
            except OSError:
                pass

    # Check stored custom prompt file
    if CUSTOM_PROMPT_FILE.exists():
        try:
            content = CUSTOM_PROMPT_FILE.read_text(encoding="utf-8")
            return content, str(CUSTOM_PROMPT_FILE)
        except OSError:
            pass

    # No custom prompt configured
    return None, None


@click.group()
def prompt() -> None:
    """Manage custom system prompts."""
    pass


@prompt.command()
def show() -> None:
    """Show the active custom system prompt."""
    from gac.prompt import _load_default_system_template

    content, source = get_active_custom_prompt()

    if content is None:
        console.print("[dim]No custom prompt configured. Showing default:[/dim]\n")
        default_template = _load_default_system_template()
        console.print(Panel(default_template.strip(), title="Default System Prompt", border_style="green"))
        return

    # Determine title based on source
    if source and source.startswith("GAC_SYSTEM_PROMPT_PATH="):
        title = f"Custom System Prompt (from {source})"
    else:
        title = f"Custom System Prompt ({source})"

    console.print(Panel(content.strip(), title=title, border_style="green"))


def _edit_text_interactive(initial_text: str) -> str | None:
    """Edit text interactively using prompt_toolkit.

    Returns edited text, or None if cancelled.
    """
    from prompt_toolkit import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
    from prompt_toolkit.layout import HSplit, Layout, Window
    from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
    from prompt_toolkit.layout.margins import ScrollbarMargin
    from prompt_toolkit.styles import Style

    try:
        import shutil

        console.print("\n[bold]Edit your custom system prompt:[/bold]")
        console.print("[dim]Esc+Enter or Ctrl+S to save | Ctrl+C to cancel[/dim]\n")

        # Create buffer for text editing
        text_buffer = Buffer(
            document=Document(text=initial_text, cursor_position=0),
            multiline=True,
            enable_history_search=False,
        )

        # Track state
        cancelled = {"value": False}
        submitted = {"value": False}

        # Get terminal size and calculate appropriate height
        term_size = shutil.get_terminal_size((80, 24))
        # Reserve 6 lines for header, hint bar, and margins
        available_height = max(5, term_size.lines - 6)
        content_height = initial_text.count("\n") + 3
        editor_height = min(available_height, max(5, content_height))

        # Create text editor window - adapt to terminal size
        text_window = Window(
            content=BufferControl(buffer=text_buffer, focus_on_click=True),
            height=editor_height,
            wrap_lines=True,
            right_margins=[ScrollbarMargin()],
        )

        # Create hint window
        hint_window = Window(
            content=FormattedTextControl(text=[("class:hint", " Esc+Enter or Ctrl+S to save | Ctrl+C to cancel ")]),
            height=1,
            dont_extend_height=True,
        )

        # Create layout
        root_container = HSplit([text_window, hint_window])
        layout = Layout(root_container, focused_element=text_window)

        # Create key bindings
        kb = KeyBindings()

        @kb.add("c-s")
        def _(event: KeyPressEvent) -> None:
            submitted["value"] = True
            event.app.exit()

        @kb.add("c-c")
        def _(event: KeyPressEvent) -> None:
            cancelled["value"] = True
            event.app.exit()

        @kb.add("escape", "enter")
        def _(event: KeyPressEvent) -> None:
            submitted["value"] = True
            event.app.exit()

        # Create and run application
        custom_style = Style.from_dict({"hint": "#888888"})

        app: Application[None] = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
            mouse_support=False,
            editing_mode=EditingMode.VI,
            style=custom_style,
        )

        app.run()

        if cancelled["value"]:
            return None

        if submitted["value"]:
            return text_buffer.text.strip()

        return None

    except (EOFError, KeyboardInterrupt):
        return None
    except Exception as e:
        logger.error(f"Error during interactive editing: {e}")
        console.print(f"[red]Failed to open editor: {e}[/red]")
        return None


def _get_prompt_file_to_edit() -> tuple[Path, str]:
    """Get the file path to edit and its current content.

    Returns the env var path if set, otherwise the default stored path.
    """
    env_path = os.getenv("GAC_SYSTEM_PROMPT_PATH")
    if env_path:
        target_file = Path(env_path)
        content = ""
        if target_file.exists():
            try:
                content = target_file.read_text(encoding="utf-8")
            except OSError:
                pass
        return target_file, content

    # Default to stored config file
    content = ""
    if CUSTOM_PROMPT_FILE.exists():
        try:
            content = CUSTOM_PROMPT_FILE.read_text(encoding="utf-8")
        except OSError:
            pass
    return CUSTOM_PROMPT_FILE, content


@prompt.command()
@click.option("--edit", "-e", is_flag=True, help="Edit prompt interactively in terminal")
@click.option("--file", "file_path", type=click.Path(exists=True), help="Copy prompt from file")
def set(edit: bool, file_path: str | None) -> None:
    """Set custom system prompt via interactive editor or file."""
    # Require exactly one of --edit or --file
    if edit and file_path:
        console.print("[red]Error: --edit and --file are mutually exclusive[/red]")
        raise click.Abort()

    if not edit and not file_path:
        console.print("[red]Error: either --edit or --file must be specified[/red]")
        raise click.Abort()

    if edit:
        # Get the target file and its current content
        target_file, initial_content = _get_prompt_file_to_edit()

        # Create parent directory if needed
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Open interactive editor
        result = _edit_text_interactive(initial_content)

        if result is None:
            console.print("\n[yellow]Edit cancelled, no changes made.[/yellow]")
            return

        if not result:
            console.print("\n[yellow]Empty prompt not saved.[/yellow]")
            return

        # Save result
        target_file.write_text(result, encoding="utf-8")
        console.print(f"\n[green]Custom prompt saved to {target_file}[/green]")

    elif file_path:
        # Copy file content
        source_file = Path(file_path)
        try:
            content = source_file.read_text(encoding="utf-8")
            # Create parent directory if needed
            CUSTOM_PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
            CUSTOM_PROMPT_FILE.write_text(content, encoding="utf-8")
            console.print(f"Custom prompt copied from {file_path} to {CUSTOM_PROMPT_FILE}")
        except OSError as e:
            console.print(f"[red]Error reading file {file_path}: {e}[/red]")
            raise click.Abort() from e


@prompt.command()
def clear() -> None:
    """Clear custom system prompt (revert to default)."""
    if CUSTOM_PROMPT_FILE.exists():
        CUSTOM_PROMPT_FILE.unlink()
        console.print(f"Custom prompt deleted: {CUSTOM_PROMPT_FILE}")
    else:
        console.print("No custom prompt file to delete.")
