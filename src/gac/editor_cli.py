"""CLI for selecting commit message editor interactively."""

import os
from pathlib import Path

import click
import questionary
from dotenv import load_dotenv, set_key, unset_key

GAC_ENV_PATH = Path.home() / ".gac.env"

# (display_name, env_value) — None means "unset GAC_EDITOR" (in-place TUI)
EDITOR_CHOICES: list[tuple[str, str | None]] = [
    ("In-place TUI (default)", None),
    ("VS Code", "code --wait"),
    ("Cursor", "cursor --wait"),
    ("Zed", "zed --wait"),
    ("Sublime Text", "subl -w"),
    ("Vim", "vim"),
    ("Neovim", "nvim"),
    ("Nano", "nano"),
    ("Emacs", "emacs"),
    ("Custom", "CUSTOM"),
]

_CUSTOM_SENTINEL = "CUSTOM"


def configure_editor_init_workflow(existing_env_path: Path | str) -> bool:
    """Configure editor as part of init workflow.

    If GAC_EDITOR is already set, offers to keep it or pick a new one
    so returning users don't need to re-answer.

    Args:
        existing_env_path: Path to the environment file

    Returns:
        True if editor configuration succeeded, False if cancelled
    """
    try:
        temp_env_path = Path(existing_env_path) if isinstance(existing_env_path, str) else existing_env_path

        # If no env file, create it and proceed directly to editor selection
        if not temp_env_path.exists():
            editor_value = _run_editor_selection_flow(temp_env_path)
            return editor_value is not None

        # Clear any existing GAC_ environ state to avoid stale values bleeding through
        env_keys_to_clear = [k for k in os.environ.keys() if k.startswith("GAC_")]
        for key in env_keys_to_clear:
            del os.environ[key]

        # File exists — check for existing editor
        load_dotenv(temp_env_path)
        existing_editor = os.getenv("GAC_EDITOR")

        if existing_editor:
            preserve_action = questionary.select(
                f"Found existing editor: {existing_editor}. How would you like to proceed?",
                choices=[
                    f"Keep existing editor ({existing_editor})",
                    "Select new editor",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if not preserve_action:
                click.echo("Editor configuration cancelled. Proceeding with init...")
                return True  # Continue with init, just skip editor part

            if preserve_action.startswith("Keep existing editor"):
                click.echo(f"Keeping existing editor: {existing_editor}")
                return True

            # User wants to select new editor
            editor_value = _run_editor_selection_flow(temp_env_path)
            if editor_value is None:
                click.echo("Editor selection cancelled. Proceeding with init...")
                return True  # Continue with init, just skip editor part
            return True
        else:
            # No existing editor
            editor_value = _run_editor_selection_flow(temp_env_path)
            return editor_value is not None

    except Exception as e:
        click.echo(f"Editor configuration error: {e}")
        return False


def _run_editor_selection_flow(env_path: Path) -> str | None:
    """Run the editor selection flow and return the selected editor value.

    Args:
        env_path: Path to the environment file

    Returns:
        Selected editor value, or None if cancelled
    """
    display_names = [choice[0] for choice in EDITOR_CHOICES]
    editor_selection = questionary.select(
        "Select an editor for commit messages:",
        choices=display_names,
        use_shortcuts=True,
        use_arrow_keys=True,
        use_jk_keys=False,
    ).ask()

    if not editor_selection:
        return None

    # Find the matching choice tuple
    choice = next(c for c in EDITOR_CHOICES if c[0] == editor_selection)
    display_name, env_value = choice

    if env_value is None:
        # In-place TUI — unset GAC_EDITOR
        unset_key(str(env_path), "GAC_EDITOR")
        os.environ.pop("GAC_EDITOR", None)
        click.echo("✓ Set editor to In-place TUI")
        click.echo("  GAC_EDITOR=(unset — in-place TUI is the default)")
        return "TUI"

    if env_value == _CUSTOM_SENTINEL:
        custom_value = _handle_custom_editor_input()
        if custom_value is None:
            return None
        set_key(str(env_path), "GAC_EDITOR", custom_value)
        os.environ["GAC_EDITOR"] = custom_value
        click.echo("✓ Set editor to Custom")
        click.echo(f"  GAC_EDITOR={custom_value}")
        return custom_value

    # Named editor choice
    set_key(str(env_path), "GAC_EDITOR", env_value)
    os.environ["GAC_EDITOR"] = env_value
    click.echo(f"✓ Set editor to {display_name}")
    click.echo(f"  GAC_EDITOR={env_value}")
    return env_value


def _handle_custom_editor_input() -> str | None:
    """Handle custom editor input from user.

    Returns:
        Custom editor command string, or None if cancelled/empty
    """
    custom_editor: str | None = questionary.text(
        "Enter editor command (e.g. 'code --wait', 'vim', 'nano'):",
    ).ask()

    if not custom_editor or not custom_editor.strip():
        return None
    return custom_editor.strip()


@click.command()
def editor() -> None:
    """Set the editor for commit messages interactively."""
    click.echo("Select an editor for your commit messages:\n")

    # Ensure .gac.env exists
    if not GAC_ENV_PATH.exists():
        GAC_ENV_PATH.touch()
        click.echo(f"Created {GAC_ENV_PATH}")

    editor_value = _run_editor_selection_flow(GAC_ENV_PATH)

    if editor_value is None:
        click.echo("Editor selection cancelled.")
        return

    click.echo(f"\n  Configuration saved to {GAC_ENV_PATH}")
