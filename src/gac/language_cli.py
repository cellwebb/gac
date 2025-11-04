"""CLI for selecting commit message language interactively."""

import os
import unicodedata
from pathlib import Path

import click
import questionary
from dotenv import load_dotenv, set_key

from gac.constants import Languages

GAC_ENV_PATH = Path.home() / ".gac.env"


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
    import unicodedata

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


def show_rtl_warning(language_name: str) -> bool:
    """Show RTL language warning and ask for confirmation.

    Args:
        language_name: Name of the RTL language

    Returns:
        True if user wants to proceed, False if they cancel
    """
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
        set_key(str(GAC_ENV_PATH), "GAC_RTL_CONFIRMED", "true")
        click.echo("✓ RTL preference saved - you won't see this warning again")
    return proceed if proceed is not None else False


@click.command()
def language() -> None:
    """Set the language for commit messages interactively."""
    click.echo("Select a language for your commit messages:\n")

    display_names = [lang[0] for lang in Languages.LANGUAGES]
    selection = questionary.select(
        "Choose your language:", choices=display_names, use_shortcuts=True, use_arrow_keys=True, use_jk_keys=False
    ).ask()

    if not selection:
        click.echo("Language selection cancelled.")
        return

    # Ensure .gac.env exists
    if not GAC_ENV_PATH.exists():
        GAC_ENV_PATH.touch()
        click.echo(f"Created {GAC_ENV_PATH}")

    # Handle English - set explicitly
    if selection == "English":
        set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", "English")
        set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "false")
        click.echo("✓ Set language to English")
        click.echo("  GAC_LANGUAGE=English")
        click.echo("  GAC_TRANSLATE_PREFIXES=false")
        click.echo(f"\n  Configuration saved to {GAC_ENV_PATH}")
        return

    # Handle custom input
    if selection == "Custom":
        custom_language = questionary.text("Enter the language name (e.g., 'Spanish', 'Français', '日本語'):").ask()
        if not custom_language or not custom_language.strip():
            click.echo("No language entered. Cancelled.")
            return
        language_value = custom_language.strip()

        # Check if the custom language appears to be RTL
        if is_rtl_text(language_value):
            if not should_show_rtl_warning():
                click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
            else:
                if not show_rtl_warning(language_value):
                    click.echo("Language selection cancelled.")
                    return

    else:
        # Find the English name for the selected language
        language_value = next(lang[1] for lang in Languages.LANGUAGES if lang[0] == selection)

        # Check if predefined language is RTL
        if is_rtl_text(language_value):
            if not should_show_rtl_warning():
                click.echo(f"\nℹ️  Using RTL language {language_value} (RTL warning previously confirmed)")
            else:
                if not show_rtl_warning(language_value):
                    click.echo("Language selection cancelled.")
                    return

    # Ask about prefix translation
    click.echo()  # Blank line for spacing
    prefix_choice = questionary.select(
        "How should conventional commit prefixes be handled?",
        choices=[
            "Keep prefixes in English (feat:, fix:, etc.)",
            f"Translate prefixes into {language_value}",
        ],
    ).ask()

    if not prefix_choice:
        click.echo("Prefix translation selection cancelled.")
        return

    translate_prefixes = prefix_choice.startswith("Translate prefixes")

    # Set the language and prefix translation preference in .gac.env
    set_key(str(GAC_ENV_PATH), "GAC_LANGUAGE", language_value)
    set_key(str(GAC_ENV_PATH), "GAC_TRANSLATE_PREFIXES", "true" if translate_prefixes else "false")

    click.echo(f"\n✓ Set language to {selection}")
    click.echo(f"  GAC_LANGUAGE={language_value}")
    if translate_prefixes:
        click.echo("  GAC_TRANSLATE_PREFIXES=true")
        click.echo("\n  Prefixes will be translated (e.g., 'corrección:' instead of 'fix:')")
    else:
        click.echo("  GAC_TRANSLATE_PREFIXES=false")
        click.echo(f"\n  Prefixes will remain in English (e.g., 'fix: <{language_value} description>')")
    click.echo(f"\n  Configuration saved to {GAC_ENV_PATH}")
