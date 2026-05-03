"""In-place commit message editing for gac."""

import logging
from typing import Any

from gac.utils import console

logger = logging.getLogger(__name__)


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
        def _(event: Any) -> None:
            """Submit with Ctrl+S."""
            submitted["value"] = True
            event.app.exit()

        @kb.add("c-c")
        def _(event: Any) -> None:
            """Cancel editing."""
            cancelled["value"] = True
            event.app.exit()

        @kb.add("escape", "enter")
        def _(event: Any) -> None:
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
