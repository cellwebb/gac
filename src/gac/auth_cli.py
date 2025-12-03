"""CLI for OAuth authentication with various providers.

Provides commands to authenticate and manage OAuth tokens for supported providers.
"""

import logging

import click

from gac.auth import QwenOAuthProvider, TokenStore
from gac.oauth.claude_code import authenticate_and_save, load_stored_token
from gac.utils import setup_logging

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Manage OAuth authentication for AI providers.

    Supports authentication for:
    - claude-code: Claude Code subscription OAuth
    - qwen: Qwen AI OAuth (device flow)

    Examples:
        gac auth                    # Show authentication status
        gac auth claude-code        # Authenticate with Claude Code
        gac auth qwen login         # Login to Qwen
        gac auth qwen logout        # Logout from Qwen
        gac auth qwen status        # Check Qwen auth status
    """
    if ctx.invoked_subcommand is None:
        _show_auth_status()


def _show_auth_status() -> None:
    """Show authentication status for all providers."""
    click.echo("OAuth Authentication Status")
    click.echo("-" * 40)

    claude_token = load_stored_token()
    if claude_token:
        click.echo("Claude Code: ✓ Authenticated")
    else:
        click.echo("Claude Code: ✗ Not authenticated")

    token_store = TokenStore()
    qwen_token = token_store.get_token("qwen")
    if qwen_token:
        click.echo("Qwen:        ✓ Authenticated")
    else:
        click.echo("Qwen:        ✗ Not authenticated")


@auth.command("claude-code")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], case_sensitive=False),
    help="Set log level (default: INFO)",
)
def auth_claude_code(quiet: bool = False, log_level: str = "INFO") -> None:
    """Authenticate with Claude Code OAuth.

    Opens a browser window for the OAuth flow and saves the token
    to ~/.gac.env. The token is used by the Claude Code provider
    to access your Claude Code subscription.
    """
    if quiet:
        effective_log_level = "ERROR"
    else:
        effective_log_level = log_level
    setup_logging(effective_log_level)

    existing_token = load_stored_token()
    if existing_token and not quiet:
        click.echo("✓ Found existing Claude Code access token.")
        click.echo()

    if not quiet:
        click.echo("🔐 Starting Claude Code OAuth authentication...")
        click.echo("   Your browser will open automatically")
        click.echo("   (Waiting up to 3 minutes for callback)")
        click.echo()

    success = authenticate_and_save(quiet=quiet)

    if success:
        if not quiet:
            click.echo("✅ Claude Code authentication completed successfully!")
            click.echo("   Your new token has been saved and is ready to use.")
    else:
        click.echo("❌ Claude Code authentication failed.")
        click.echo("   Please try again or check your network connection.")
        raise click.ClickException("Claude Code authentication failed")


@auth.group()
def qwen() -> None:
    """Manage Qwen OAuth authentication.

    Use device flow authentication to log in to Qwen AI.
    """
    pass


@qwen.command("login")
@click.option("--no-browser", is_flag=True, help="Don't automatically open browser")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def qwen_login(no_browser: bool = False, quiet: bool = False) -> None:
    """Login to Qwen using OAuth device flow.

    Opens a browser to authenticate with Qwen. The token is stored
    securely in ~/.gac/oauth/qwen.json.
    """
    if not quiet:
        setup_logging("INFO")

    provider = QwenOAuthProvider()

    if provider.is_authenticated():
        if not quiet:
            click.echo("✓ Already authenticated with Qwen.")
            if not click.confirm("Re-authenticate?"):
                return

    try:
        provider.initiate_auth(open_browser=not no_browser)
        if not quiet:
            click.echo()
            click.echo("✅ Qwen authentication completed successfully!")
    except Exception as e:
        click.echo(f"❌ Qwen authentication failed: {e}")
        raise click.ClickException("Qwen authentication failed") from None


@qwen.command("logout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def qwen_logout(quiet: bool = False) -> None:
    """Logout from Qwen and remove stored tokens."""
    provider = QwenOAuthProvider()

    if not provider.is_authenticated():
        if not quiet:
            click.echo("Not currently authenticated with Qwen.")
        return

    provider.logout()
    if not quiet:
        click.echo("✅ Successfully logged out from Qwen.")


@qwen.command("status")
def qwen_status() -> None:
    """Check Qwen authentication status."""
    provider = QwenOAuthProvider()
    token = provider.get_token()

    if token:
        click.echo("Qwen Authentication Status: ✓ Authenticated")
        if token.get("resource_url"):
            click.echo(f"API Endpoint: {token['resource_url']}")
    else:
        click.echo("Qwen Authentication Status: ✗ Not authenticated")
        click.echo("Run 'gac auth qwen login' to authenticate.")
