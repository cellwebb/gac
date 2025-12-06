"""CLI for selecting commit message language interactively."""

import os
import unicodedata
from pathlib import Path

import click
import questionary
from dotenv import load_dotenv, set_key

from gac.constants import Languages

GAC_ENV_PATH = Path.home() / ".gac.env"


def configure_language_init_workflow(existing_env_path: Path | str) -> bool:
    """Configure language as part of init workflow.

    This is used by init_cli.py to handle language configuration
    when the init command is run.

    Args:
        existing_env_path: Path to the environment file

    Returns:
        True if language configuration succeeded, False if cancelled
    """
    try:
        # Use the provided path instead of our default GAC_ENV_PATH
        temp_env_path = Path(existing_env_path) if isinstance(existing_env_path, str) else existing_env_path

        # If no env file, create it and proceed directly to language selection
        if not temp_env_path.exists():
            language_value = _run_language_selection_flow(temp_env_path)
            return language_value is not None

        # Clear any existing environ state to avoid cross-test contamination
        env_keys_to_clear = [k for k in os.environ.keys() if k.startswith("GAC_")]
        for key in env_keys_to_clear:
            del os.environ[key]

        # File exists - check for existing language
        load_dotenv(temp_env_path)
        existing_language = os.getenv("GAC_LANGUAGE")

        if existing_language:
            # Language already exists - ask what to do
            preserve_action = questionary.select(
                f"Found existing language: {existing_language}. How would you like to proceed?",
                choices=[
                    f"Keep existing language ({existing_language})",
                    "Select new language",
                ],
                use_shortcuts=True,
                use_arrow_keys=True,
                use_jk_keys=False,
            ).ask()

            if not preserve_action:
                click.echo("Language configuration cancelled. Proceeding with init...")
                return True  # Continue with init, just skip language part

            if preserve_action.startswith("Keep existing language"):
                click.echo(f"Keeping existing language: {existing_language}")
                return True

            # User wants to select new language
            language_value = _run_language_selection_flow(temp_env_path)
            if language_value is None:
                click.echo("Language selection cancelled. Proceeding with init...")
                return True  # Continue with init, just skip language part
            return True
        else:
            # No existing language
            language_value = _run_language_selection_flow(temp_env_path)
            return language_value is not None

    except Exception as e:
        click.echo(f"Language configuration error: {e}")
        return False


def _run_language_selection_flow(env_path: Path) -> str | None:
    """Run the language selection flow and return the selected language.

    Args:
        env_path: Path to the environment file

    Returns:
        Selected language value, or None if cancelled
    """
    display_names = [lang[0] for lang in Languages.LANGUAGES]
    language_selection = questionary.select(
        "Select a language for commit messages:",
        choices=display_names,
        use_shortcuts=True,
        use_arrow_keys=True,
        use_jk_keys=False,
    ).ask()

    if not language_selection:
        return None

    # Handle English - set explicitly
    if language_selection == "English":
        set_key(str(env_path), "GAC_LANGUAGE", "English")
        set_key(str(env_path), "GAC_TRANSLATE_PREFIXES", "false")
        click.echo("Set GAC_LANGUAGE='English'")
        click.echo("Set GAC_TRANSLATE_PREFIXES='false'")
        return "English"

    # Handle custom input
    if language_selection == "Custom":
        language_value = _handle_custom_language_input()
    else:
        # Find the English name for the selected language
        language_value = next(lang[1] for lang in Languages.LANGUAGES if lang[0] == language_selection)

    if language_value is None:
        return None

    # Check if language is RTL and handle warning
    if is_rtl_text(language_value):
        if not should_show_rtl_warning():
            click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
        else:
            if not show_rtl_warning(language_value, env_path):
                return None  # User cancelled

    # Ask about prefix translation
    translate_prefixes = _ask_about_prefix_translation(language_value)
    if translate_prefixes is None:
        return None  # User cancelled

    # Set the language and prefix translation preference
    set_key(str(env_path), "GAC_LANGUAGE", language_value)
    set_key(str(env_path), "GAC_TRANSLATE_PREFIXES", "true" if translate_prefixes else "false")
    click.echo(f"Set GAC_LANGUAGE='{language_value}'")
    click.echo(f"Set GAC_TRANSLATE_PREFIXES={'true' if translate_prefixes else 'false'}")

    return language_value


def _handle_custom_language_input() -> str | None:
    """Handle custom language input from user.

    Returns:
        Custom language value, or None if cancelled/empty
    """
    custom_language: str | None = questionary.text(
        "Enter the language name (e.g., 'Spanish', 'Français', '日本語'):",
        use_shortcuts=True,
        use_arrow_keys=True,
        use_jk_keys=False,
    ).ask()

    if not custom_language or not custom_language.strip():
        return None
    return custom_language.strip()


def _ask_about_prefix_translation(language_value: str) -> bool | None:
    """Ask user about prefix translation preference.

    Args:
        language_value: The selected language

    Returns:
        True if translate prefixes, False if keep English, None if cancelled
    """
    prefix_choice: str | None = questionary.select(
        "How should conventional commit prefixes be handled?",
        choices=[
            "Keep prefixes in English (feat:, fix:, etc.)",
            f"Translate prefixes into {language_value}",
        ],
        use_shortcuts=True,
        use_arrow_keys=True,
        use_jk_keys=False,
    ).ask()

    if not prefix_choice:
        return None
    return prefix_choice.startswith("Translate prefixes")


def should_show_rtl_warning() -> bool:
    """Check if RTL warning should be shown based on saved preference.

    Returns:
        True if warning should be shown, False if user previously confirmed
    """
    # Load the current config to check RTL confirmation
    if GAC_ENV_PATH.exists():
        load_dotenv(GAC_ENV_PATH)
        rtl_confirmed = os.getenv("GAC_RTL_CONFIRMED", "false").lower() in ("true", "1", "yes", "on")
        return not rtl_confirmed
    return True  # Show warning if no config exists


def is_rtl_text(text: str) -> bool:
    """Detect if text contains RTL characters or is a known RTL language.

    Args:
        text: Text to analyze

    Returns:
        True if text contains RTL script characters or is RTL language
    """
    # Known RTL language names (case insensitive)
    rtl_languages = {
        "arabic",
        "ar",
        "العربية",
        "hebrew",
        "he",
        "עברית",
        "persian",
        "farsi",
        "fa",
        "urdu",
        "ur",
        "اردو",
        "pashto",
        "ps",
        "kurdish",
        "ku",
        "کوردی",
        "yiddish",
        "yi",
        "ייִדיש",
    }

    # Check if it's a known RTL language name or code (case insensitive)
    if text.lower().strip() in rtl_languages:
        return True

    rtl_scripts = {"Arabic", "Hebrew", "Thaana", "Nko", "Syriac", "Mandeic", "Samaritan", "Mongolian", "Phags-Pa"}

    for char in text:
        if unicodedata.name(char, "").startswith(("ARABIC", "HEBREW")):
            return True
        script = unicodedata.name(char, "").split()[0] if unicodedata.name(char, "") else ""
        if script in rtl_scripts:
            return True
    return False


def center_text(text: str, width: int = 80) -> str:
    """Center text within specified width, handling display width properly.

    Args:
        text: Text to center
        width: Terminal width to center within (default 80)

    Returns:
        Centered text with proper padding
    """

    def get_display_width(s: str) -> int:
        """Get the display width of a string, accounting for wide characters."""
        width = 0
        for char in s:
            # East Asian characters are typically 2 columns wide
            if unicodedata.east_asian_width(char) in ("W", "F"):
                width += 2
            else:
                width += 1
        return width

    # Handle multi-line text
    lines = text.split("\n")
    centered_lines = []

    for line in lines:
        # Strip existing whitespace to avoid double padding
        stripped_line = line.strip()
        if stripped_line:
            # Calculate padding using display width for accurate centering
            display_width = get_display_width(stripped_line)
            padding = max(0, (width - display_width) // 2)
            centered_line = " " * padding + stripped_line
            centered_lines.append(centered_line)
        else:
            centered_lines.append("")

    return "\n".join(centered_lines)


def get_terminal_width() -> int:
    """Get the current terminal width.

    Returns:
        Terminal width in characters, or default if can't be determined
    """
    try:
        import shutil

        return shutil.get_terminal_size().columns
    except (OSError, AttributeError):
        return 80  # Fallback to 80 columns


def show_rtl_warning(language_name: str, env_path: Path | None = None) -> bool:
    """Show RTL language warning and ask for confirmation.

    Args:
        language_name: Name of the RTL language
        env_path: Path to environment file (defaults to GAC_ENV_PATH)

    Returns:
        True if user wants to proceed, False if they cancel
    """
    if env_path is None:
        env_path = GAC_ENV_PATH
    terminal_width = get_terminal_width()

    # Center just the title
    title = center_text("⚠️  RTL Language Detected", terminal_width)

    click.echo()
    click.echo(click.style(title, fg="yellow", bold=True))
    click.echo()
    click.echo("Right-to-left (RTL) languages may not display correctly in gac due to terminal limitations.")
    click.echo("However, the commit messages will work fine and should be readable in Git clients")
    click.echo("that properly support RTL text (like most web interfaces and modern tools).\n")

    proceed = questionary.confirm("Do you want to proceed anyway?").ask()
    if proceed:
        # Remember that user has confirmed RTL acceptance
        set_key(str(env_path), "GAC_RTL_CONFIRMED", "true")
        click.echo("✓ RTL preference saved - you won't see this warning again")
    return proceed if proceed is not None else False


@click.command()
def language() -> None:
    """Set the language for commit messages interactively."""
    click.echo("Select a language for your commit messages:\n")

    # Ensure .gac.env exists
    if not GAC_ENV_PATH.exists():
        GAC_ENV_PATH.touch()
        click.echo(f"Created {GAC_ENV_PATH}")

    language_value = _run_language_selection_flow(GAC_ENV_PATH)

    if language_value is None:
        click.echo("Language selection cancelled.")
        return

    # Find the display name for output
    try:
        display_name = next(lang[0] for lang in Languages.LANGUAGES if lang[1] == language_value)
    except StopIteration:
        display_name = language_value  # Custom language

        # If custom language, check if it appears to be RTL for display purposes
    if display_name == language_value and is_rtl_text(language_value):
        # This is a custom RTL language that was handled in _run_language_selection_flow
        if not should_show_rtl_warning():
            click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")

    click.echo(f"\n✓ Set language to {display_name}")
    click.echo(f"  GAC_LANGUAGE={language_value}")

    # Check prefix translation setting
    load_dotenv(GAC_ENV_PATH)
    translate_prefixes = os.getenv("GAC_TRANSLATE_PREFIXES", "false").lower() in ("true", "1", "yes", "on")
    if translate_prefixes:
        click.echo("  GAC_TRANSLATE_PREFIXES=true")
        click.echo("\n  Prefixes will be translated (e.g., 'corrección:' instead of 'fix:')")
    else:
        click.echo("  GAC_TRANSLATE_PREFIXES=false")
        click.echo(f"\n  Prefixes will remain in English (e.g., 'fix: <{language_value} description>')")

    click.echo(f"\n  Configuration saved to {GAC_ENV_PATH}")
