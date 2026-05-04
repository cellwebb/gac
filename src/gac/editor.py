"""Commit message editing for gac.

Provides two editing modes:
- In-place: prompt_toolkit TUI with vi/emacs bindings
- External: opens $EDITOR (vim, nano, etc.)
"""

import logging
import os
import shlex
import subprocess
import tempfile
from typing import Any

from gac.utils import console

logger = logging.getLogger(__name__)


def _split_editor_command(editor: str) -> list[str]:
    """Split an editor command string into argv.

    We avoid `shell=True` for safety, so we need to tokenize strings like:
    - code --wait
    - "C:\\Program Files\\Vim\\gvim.exe" --nofork

    Notes:
    - On Unix, `shlex.split(..., posix=True)` strips quotes and handles escapes.
    - On Windows, `shlex.split(..., posix=False)` preserves backslashes, but
      *also preserves surrounding quotes*, so we strip simple surrounding quotes
      post-split to get a runnable argv.
    """
    posix = os.name != "nt"
    parts = shlex.split(editor, posix=posix)
    if not posix:
        parts = [p[1:-1] if len(p) >= 2 and p[0] == p[-1] and p[0] in ('"', "'") else p for p in parts]
    return parts


def _run_git_var_editor() -> str | None:
    """Query git for the resolved editor via `git var GIT_EDITOR`.

    This respects the full Git precedence: $GIT_EDITOR → core.editor →
    $VISUAL → $EDITOR → compiled-in default.

    Returns:
        The editor string from git, or None if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "var", "GIT_EDITOR"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _resolve_editor() -> str:
    """Resolve the editor command using gac/Git/standard resolution.

    Precedence (highest first):
    1. $GAC_EDITOR          — gac-specific override
    2. git var GIT_EDITOR   — includes core.editor, $GIT_EDITOR, $VISUAL, $EDITOR
    3. $GIT_EDITOR          — standard git env var
    4. $VISUAL              — traditional visual editor
    5. $EDITOR              — standard editor
    6. vi                   — compiled-in fallback

    Returns:
        The editor command string (may contain args, e.g. 'code --wait')
    """
    return (
        os.environ.get("GAC_EDITOR")
        or _run_git_var_editor()
        or os.environ.get("GIT_EDITOR")
        or os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or "vi"
    )


_WAIT_FLAGS = {"--wait", "-w"}

# Editors whose CLIs are known to return immediately unless a wait flag is used.
# Maps binary name (lowercase, without extension) → preferred wait flag.
_FORKING_EDITORS: dict[str, str] = {
    # VS Code CLI (`-w`/`--wait`) - https://code.visualstudio.com/docs/editor/command-line
    "code": "--wait",
    "code-insiders": "--wait",
    "codium": "--wait",
    "code-oss": "--wait",
    # Cursor CLI (`-w`/`--wait`) - https://docs.cursor.com/tools/cli
    "cursor": "--wait",
    # Zed CLI (`-w`/`--wait`) - https://zed.dev/docs/reference/cli.html
    "zed": "--wait",
    # Sublime Text CLI (`-w`/`--wait`) - https://www.sublimetext.com/docs/command_line.html
    "subl": "-w",
}


def _maybe_add_wait_flag(editor_argv: list[str]) -> tuple[list[str], bool]:
    """Ensure known forking GUI editors block until the file is closed.

    If the editor is recognized as a forking GUI editor and no wait flag is
    present, we add the appropriate wait flag so commit-message editing works.
    """
    if not editor_argv:
        return editor_argv, False

    binary = os.path.basename(editor_argv[0]).lower()
    binary = os.path.splitext(binary)[0]
    wait_flag = _FORKING_EDITORS.get(binary)
    if not wait_flag:
        return editor_argv, False

    if any(flag in editor_argv for flag in _WAIT_FLAGS):
        return editor_argv, False

    # Insert right after the binary for predictability.
    return [editor_argv[0], wait_flag, *editor_argv[1:]], True


def edit_commit_message_in_editor(message: str) -> str | None:
    """Edit commit message using the user's preferred editor.

    Resolves the editor via `git var GIT_EDITOR` (which includes core.editor),
    falling back to env-var resolution if git is unavailable.
    Supports editors with arguments (e.g. 'code --wait', 'vim -u ~/.vimrc').

    Writes the message to a temporary file, opens the editor for editing,
    and reads the result back. For known GUI editors that otherwise return
    immediately (e.g. VS Code), a wait flag is added automatically.

    Args:
        message: The initial commit message

    Returns:
        The edited commit message, or None if editing was cancelled / no changes made

    Example:
        >>> edited = edit_commit_message_in_editor("feat: add feature")
        >>> # Editor opens, user edits and saves
    """
    editor = _resolve_editor()
    tmp_path: str | None = None

    try:
        editor_argv = _split_editor_command(editor)
        editor_argv, _ = _maybe_add_wait_flag(editor_argv)

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".commitmsg",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(message)
            tmp_path = tmp.name

        if not editor_argv:
            console.print("[error]No editor configured (empty editor command).[/error]")
            return None

        editor_cmd = editor_argv + [tmp_path]
        console.print(f"\n[info]Opening {editor}...[/info]")

        result = subprocess.run(
            editor_cmd,
            check=False,
        )

        if result.returncode != 0:
            console.print(f"[yellow]Editor exited with code {result.returncode}. Edit cancelled.[/yellow]")
            return None

        with open(tmp_path, encoding="utf-8") as f:
            edited_message = f.read().strip()

        if not edited_message:
            console.print("[yellow]Commit message cannot be empty. Edit cancelled.[/yellow]")
            return None

        # If the message is unchanged, treat as "no edit".
        if edited_message == message.strip():
            console.print("[yellow]Commit message unchanged by editor.[/yellow]")
            return None

        return edited_message

    except FileNotFoundError:
        console.print(f"[error]Editor '{editor}' not found. Set $EDITOR to your preferred editor.[/error]")
        return None
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]Edit cancelled.[/yellow]")
        return None
    except Exception as e:
        logger.exception("Error during external editor editing")
        console.print(f"[error]Failed to edit commit message: {e}[/error]")
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def edit_commit_message_inplace(message: str) -> str | None:
    """Edit commit message in-place using prompt_toolkit TUI.

    Uses prompt_toolkit to provide a rich editing experience with:
    - Multi-line editing
    - Vi/Emacs key bindings
    - Line editing capabilities
    - Esc+Enter or Ctrl+S to submit
    - Ctrl+C to cancel

    For opening your actual $EDITOR (vim, nano, etc.), use
    edit_commit_message_in_editor() instead.

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
