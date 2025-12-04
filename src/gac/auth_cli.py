"""CLI for OAuth authentication with various providers.

Provides commands to authenticate and manage OAuth tokens for supported providers.
"""

import logging

import click

from gac.oauth import (
    QwenOAuthProvider,
    TokenStore,
    authenticate_and_save,
    remove_token,
)
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
        gac auth                        # Show authentication status
        gac auth claude-code login      # Login to Claude Code
        gac auth claude-code logout     # Logout from Claude Code
        gac auth claude-code status     # Check Claude Code auth status
        gac auth qwen login             # Login to Qwen
        gac auth qwen logout            # Logout from Qwen
        gac auth qwen status            # Check Qwen auth status
    """
    if ctx.invoked_subcommand is None:
        _show_auth_status()


def _show_auth_status() -> None:
    """Show authentication status for all providers."""
    click.echo("OAuth Authentication Status")
    click.echo("-" * 40)

    token_store = TokenStore()

    claude_token = token_store.get_token("claude-code")
    if claude_token:
        click.echo("Claude Code: ✓ Authenticated")
    else:
        click.echo("Claude Code: ✗ Not authenticated")
        click.echo("             Run 'gac auth claude-code login' to login")

    qwen_token = token_store.get_token("qwen")
    if qwen_token:
        click.echo("Qwen:        ✓ Authenticated")
    else:
        click.echo("Qwen:        ✗ Not authenticated")
        click.echo("             Run 'gac auth qwen login' to login")


# Claude Code commands
@auth.group("claude-code")
def claude_code() -> None:
    """Manage Claude Code OAuth authentication.

    Use browser-based authentication to log in to Claude Code.
    """
    pass


@claude_code.command("login")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def claude_code_login(quiet: bool = False) -> None:
    """Login to Claude Code using OAuth.

    Opens a browser to authenticate with Claude Code. The token is stored
    securely in ~/.gac/oauth/claude-code.json.
    """
    if not quiet:
        setup_logging("INFO")

    token_store = TokenStore()
    existing_token = token_store.get_token("claude-code")
    if existing_token:
        if not quiet:
            click.echo("✓ Already authenticated with Claude Code.")
            if not click.confirm("Re-authenticate?"):
                return

    if not quiet:
        click.echo("🔐 Starting Claude Code OAuth authentication...")
        click.echo("   Your browser will open automatically")
        click.echo("   (Waiting up to 3 minutes for callback)")
        click.echo()

    success = authenticate_and_save(quiet=quiet)

    if success:
        if not quiet:
            click.echo()
            click.echo("✅ Claude Code authentication completed successfully!")
    else:
        click.echo("❌ Claude Code authentication failed.")
        click.echo("   Please try again or check your network connection.")
        raise click.ClickException("Claude Code authentication failed")


@claude_code.command("logout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def claude_code_logout(quiet: bool = False) -> None:
    """Logout from Claude Code and remove stored tokens."""
    token_store = TokenStore()
    existing_token = token_store.get_token("claude-code")

    if not existing_token:
        if not quiet:
            click.echo("Not currently authenticated with Claude Code.")
        return

    try:
        remove_token()
        if not quiet:
            click.echo("✅ Successfully logged out from Claude Code.")
    except Exception as e:
        click.echo("❌ Failed to remove Claude Code token.")
        raise click.ClickException("Claude Code logout failed") from e


@claude_code.command("status")
def claude_code_status() -> None:
    """Check Claude Code authentication status."""
    token_store = TokenStore()
    token = token_store.get_token("claude-code")

    if token:
        click.echo("Claude Code Authentication Status: ✓ Authenticated")
    else:
        click.echo("Claude Code Authentication Status: ✗ Not authenticated")
        click.echo("Run 'gac auth claude-code login' to authenticate.")


# Qwen commands
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
