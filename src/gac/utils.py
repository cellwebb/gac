"""Utility functions for gac."""

import logging
import subprocess

from rich.console import Console
from rich.theme import Theme

from gac.constants import Logging
from gac.errors import GacError


def setup_logging(
    log_level: int | str = Logging.DEFAULT_LEVEL,
    quiet: bool = False,
    force: bool = False,
    suppress_noisy: bool = False,
) -> None:
    """Configure logging for the application.

    Args:
        log_level: Log level to use (DEBUG, INFO, WARNING, ERROR)
        quiet: If True, suppress all output except errors
        force: If True, force reconfiguration of logging
        suppress_noisy: If True, suppress noisy third-party loggers
    """
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.WARNING)

    if quiet:
        log_level = logging.ERROR

    kwargs = {"force": force} if force else {}

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        **kwargs,  # type: ignore[arg-type]
    )

    if suppress_noisy:
        for noisy_logger in ["requests", "urllib3"]:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    logger.info(f"Logging initialized with level: {logging.getLevelName(log_level)}")


theme = Theme(
    {
        "success": "green bold",
        "info": "blue",
        "warning": "yellow",
        "error": "red bold",
        "header": "magenta",
        "notification": "bright_cyan bold",
    }
)
console = Console(theme=theme)
logger = logging.getLogger(__name__)


def print_message(message: str, level: str = "info") -> None:
    """Print a styled message with the specified level."""
    console.print(message, style=level)


def run_subprocess(
    command: list[str],
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run a subprocess command safely and return the output.

    Args:
        command: List of command arguments
        silent: If True, suppress debug logging
        timeout: Command timeout in seconds
        check: Whether to check return code (for compatibility)
        strip_output: Whether to strip whitespace from output
        raise_on_error: Whether to raise an exception on error

    Returns:
        Command output as string

    Raises:
        GacError: If the command times out
        subprocess.CalledProcessError: If the command fails and raise_on_error is True
    """
    if not silent:
        logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        should_raise = result.returncode != 0 and (check or raise_on_error)

        if should_raise:
            if not silent:
                logger.debug(f"Command stderr: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)

        output = result.stdout
        if strip_output:
            output = output.strip()

        return output
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        raise GacError(f"Command timed out: {' '.join(command)}") from e
    except subprocess.CalledProcessError as e:
        if not silent:
            logger.error(f"Command failed: {e.stderr.strip() if e.stderr else str(e)}")
        if raise_on_error:
            raise
        return ""
    except Exception as e:
        if not silent:
            logger.debug(f"Command error: {e}")
        if raise_on_error:
            # Convert generic exceptions to CalledProcessError for consistency
            raise subprocess.CalledProcessError(1, command, "", str(e)) from e
        return ""


def edit_commit_message_inplace(message: str) -> str | None:
    """Edit commit message in-place using rich terminal editing.

    Uses prompt_toolkit to provide a rich editing experience with:
    - Multi-line editing
    - Vi/Emacs key bindings
    - Line editing capabilities
    - Esc+Enter or Ctrl+S to submit
    - Ctrl+C to cancel

    Args:
        message: The initial commit message

    Returns:
        The edited commit message, or None if editing was cancelled

    Example:
        >>> edited = edit_commit_message_inplace("feat: add feature")
        >>> # User can edit the message using vi/emacs key bindings
        >>> # Press Esc+Enter or Ctrl+S to submit
    """
    from prompt_toolkit import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import HSplit, Layout, Window
    from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
    from prompt_toolkit.layout.margins import ScrollbarMargin
    from prompt_toolkit.styles import Style

    try:
        console.print("\n[info]Edit commit message:[/info]")
        console.print()

        # Create buffer for text editing
        text_buffer = Buffer(
            document=Document(text=message, cursor_position=0),
            multiline=True,
            enable_history_search=False,
        )

        # Track submission state
        cancelled = {"value": False}
        submitted = {"value": False}

        # Create text editor window
        text_window = Window(
            content=BufferControl(
                buffer=text_buffer,
                focus_on_click=True,
            ),
            height=lambda: max(5, message.count("\n") + 3),
            wrap_lines=True,
            right_margins=[ScrollbarMargin()],
        )

        # Create hint window
        hint_window = Window(
            content=FormattedTextControl(
                text=[("class:hint", " Esc+Enter or Ctrl+S to submit | Ctrl+C to cancel ")],
            ),
            height=1,
            dont_extend_height=True,
        )

        # Create layout
        root_container = HSplit(
            [
                text_window,
                hint_window,
            ]
        )

        layout = Layout(root_container, focused_element=text_window)

        # Create key bindings
        kb = KeyBindings()

        @kb.add("c-s")
        def _(event):
            """Submit with Ctrl+S."""
            submitted["value"] = True
            event.app.exit()

        @kb.add("c-c")
        def _(event):
            """Cancel editing."""
            cancelled["value"] = True
            event.app.exit()

        @kb.add("escape", "enter")
        def _(event):
            """Submit with Esc+Enter."""
            submitted["value"] = True
            event.app.exit()

        # Create and run application
        custom_style = Style.from_dict(
            {
                "hint": "#888888",
            }
        )

        app: Application[None] = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,
            mouse_support=False,
            editing_mode=EditingMode.VI,  # Enable vi key bindings
            style=custom_style,
        )

        app.run()

        # Handle result
        if cancelled["value"]:
            console.print("\n[yellow]Edit cancelled.[/yellow]")
            return None

        if submitted["value"]:
            edited_message = text_buffer.text.strip()
            if not edited_message:
                console.print("[yellow]Commit message cannot be empty. Edit cancelled.[/yellow]")
                return None
            return edited_message

        return None

    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Edit cancelled.[/yellow]")
        return None
    except Exception as e:
        logger.error(f"Error during in-place editing: {e}")
        console.print(f"[error]Failed to edit commit message: {e}[/error]")
        return None
