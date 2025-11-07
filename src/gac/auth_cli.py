"""CLI for authenticating Claude Code OAuth tokens.

Provides a command to authenticate and re-authenticate Claude Code subscriptions.
"""

import logging

import click

from gac.oauth.claude_code import authenticate_and_save, load_stored_token
from gac.utils import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-error output",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], case_sensitive=False),
    help="Set log level (default: INFO)",
)
def auth(quiet: bool = False, log_level: str = "INFO") -> None:
    """Authenticate Claude Code OAuth token.

    This command allows you to authenticate or re-authenticate your
    Claude Code OAuth token when it expires or you want to refresh it.
    It opens a browser window for the OAuth flow and saves the token
    to ~/.gac.env.

    The token is used by the Claude Code provider to access your
    Claude Code subscription instead of requiring an Anthropic API key.
    """
    # Setup logging
    if quiet:
        effective_log_level = "ERROR"
    else:
        effective_log_level = log_level
    setup_logging(effective_log_level)

    # Check if there's an existing token
    existing_token = load_stored_token()
    if existing_token and not quiet:
        click.echo("✓ Found existing Claude Code access token.")
        click.echo()

    if not quiet:
        click.echo("🔐 Starting Claude Code OAuth authentication...")
        click.echo("   Your browser will open automatically")
        click.echo("   (Waiting up to 3 minutes for callback)")
        click.echo()

    # Perform OAuth authentication
    success = authenticate_and_save(quiet=quiet)

    if success:
        if not quiet:
            click.echo("✅ Claude Code authentication completed successfully!")
            click.echo("   Your new token has been saved and is ready to use.")
    else:
        click.echo("❌ Claude Code authentication failed.")
        click.echo("   Please try again or check your network connection.")
        raise click.ClickException("Claude Code authentication failed")
