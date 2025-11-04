"""Utility functions for gac."""

import locale
import logging
import subprocess
import sys

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


def get_safe_encodings() -> list[str]:
    """Get a list of safe encodings to try for subprocess calls, in order of preference.

    Returns:
        List of encoding strings to try, with UTF-8 first
    """
    encodings = ["utf-8"]

    # Add locale encoding as fallback
    locale_encoding = locale.getpreferredencoding(False)
    if locale_encoding and locale_encoding not in encodings:
        encodings.append(locale_encoding)

    # Windows-specific fallbacks
    if sys.platform == "win32":
        windows_encodings = ["cp65001", "cp936", "cp1252"]  # UTF-8, GBK, Windows-1252
        for enc in windows_encodings:
            if enc not in encodings:
                encodings.append(enc)

    # Final fallback to system default
    if "utf-8" not in encodings:
        encodings.append("utf-8")

    return encodings


def run_subprocess_with_encoding(
    command: list[str],
    encoding: str,
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run subprocess with a specific encoding, handling encoding errors gracefully.

    Args:
        command: List of command arguments
        encoding: Specific encoding to use
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
        logger.debug(f"Running command: {' '.join(command)} (encoding: {encoding})")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            encoding=encoding,
            errors="replace",  # Replace problematic characters instead of crashing
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
    except UnicodeError as e:
        # This should be rare with errors="replace", but handle it just in case
        if not silent:
            logger.debug(f"Encoding error with {encoding}: {e}")
        raise
    except Exception as e:
        if not silent:
            logger.debug(f"Command error: {e}")
        if raise_on_error:
            # Convert generic exceptions to CalledProcessError for consistency
            raise subprocess.CalledProcessError(1, command, "", str(e)) from e
        return ""


def run_subprocess(
    command: list[str],
    silent: bool = False,
    timeout: int = 60,
    check: bool = True,
    strip_output: bool = True,
    raise_on_error: bool = True,
) -> str:
    """Run a subprocess command safely and return the output, trying multiple encodings.

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

    Note:
        Tries multiple encodings in order: utf-8, locale encoding, platform-specific fallbacks
        This prevents UnicodeDecodeError on systems with non-UTF-8 locales (e.g., Chinese Windows)
    """
    encodings = get_safe_encodings()
    last_exception = None

    for encoding in encodings:
        try:
            return run_subprocess_with_encoding(
                command=command,
                encoding=encoding,
                silent=silent,
                timeout=timeout,
                check=check,
                strip_output=strip_output,
                raise_on_error=raise_on_error,
            )
        except UnicodeError as e:
            last_exception = e
            if not silent:
                logger.debug(f"Failed to decode with {encoding}: {e}")
            continue
        except (subprocess.CalledProcessError, GacError, subprocess.TimeoutExpired):
            # These are not encoding-related errors, so don't retry with other encodings
            raise

    # If we get here, all encodings failed with UnicodeError
    if not silent:
        logger.error(f"Failed to decode command output with any encoding: {encodings}")

    # Raise the last UnicodeError we encountered
    if last_exception:
        raise subprocess.CalledProcessError(1, command, "", f"Encoding error: {last_exception}") from last_exception
    else:
        raise subprocess.CalledProcessError(1, command, "", "All encoding attempts failed")


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
