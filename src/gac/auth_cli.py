"""CLI for OAuth authentication with various providers.

Provides commands to authenticate and manage OAuth tokens for supported providers.
"""

import logging

import click

from gac.oauth import (
    TokenStore,
    authenticate_and_save,
    remove_token,
)
from gac.oauth.chatgpt import (
    DEFAULT_CODEX_MODELS,
)
from gac.oauth.chatgpt import (
    authenticate_and_save as chatgpt_authenticate_and_save,
)
from gac.oauth.chatgpt import (
    is_token_expired as chatgpt_is_token_expired,
)
from gac.oauth.chatgpt import (
    remove_token as chatgpt_remove_token,
)
from gac.oauth.copilot import (
    DEFAULT_COPILOT_MODELS,
    _normalize_host,
)
from gac.oauth.copilot import (
    authenticate_and_save as copilot_authenticate_and_save,
)
from gac.oauth.copilot import (
    refresh_token_if_expired as copilot_refresh_token_if_expired,
)
from gac.oauth.copilot import (
    remove_token as copilot_remove_token,
)
from gac.utils import setup_logging

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Manage OAuth authentication for AI providers.

    Supports authentication for:
    - claude-code: Claude Code subscription OAuth
    - chatgpt: ChatGPT Codex API OAuth
    - copilot: GitHub Copilot Device Flow

    Examples:
        gac auth                        # Show authentication status
        gac auth claude-code login      # Login to Claude Code
        gac auth claude-code logout     # Logout from Claude Code
        gac auth claude-code status     # Check Claude Code auth status
        gac auth chatgpt login          # Login to ChatGPT
        gac auth chatgpt logout         # Logout from ChatGPT
        gac auth chatgpt status         # Check ChatGPT auth status
        gac auth copilot login          # Login to GitHub Copilot
        gac auth copilot logout         # Logout from GitHub Copilot
        gac auth copilot status         # Check Copilot auth status
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

    chatgpt_token = token_store.get_token("chatgpt-oauth")
    if chatgpt_token:
        click.echo("ChatGPT:      ✓ Authenticated")
    else:
        click.echo("ChatGPT:      ✗ Not authenticated")
        click.echo("             Run 'gac auth chatgpt login' to login")

    copilot_token = token_store.get_token("copilot")
    if copilot_token:
        click.echo("Copilot:      ✓ Authenticated")
    else:
        click.echo("Copilot:      ✗ Not authenticated")
        click.echo("             Run 'gac auth copilot login' to login")


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
        click.echo(
            "⚠️  Note: Anthropic has been cracking down on third-party tools using Claude Code "
            "OAuth tokens; this use of gac is unsanctioned and could stop working at any time. "
            "For reliable use, prefer a direct API provider (anthropic, openai, etc.). "
            "See https://support.claude.com/en/articles/11145838-using-claude-code-with-your-claude-subscription"
        )
        click.echo()
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


# ---------------------------------------------------------------------------
# ChatGPT OAuth commands
# ---------------------------------------------------------------------------


@auth.group("chatgpt")
def chatgpt() -> None:
    """Manage ChatGPT OAuth authentication.

    Use browser-based authentication to log in to ChatGPT and access
    the Codex API with your ChatGPT subscription.
    """
    pass


@chatgpt.command("login")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def chatgpt_login(quiet: bool = False) -> None:
    """Login to ChatGPT using OAuth.

    Opens a browser to authenticate with ChatGPT. The token is stored
    securely in ~/.gac/oauth/chatgpt-oauth.json.

    After authentication, you can use ChatGPT Codex models like:
        gac -m chatgpt-oauth:gpt-5.4
    """
    if not quiet:
        setup_logging("INFO")

    token_store = TokenStore()
    existing_token = token_store.get_token("chatgpt-oauth")
    if existing_token:
        if not quiet:
            click.echo("✓ Already authenticated with ChatGPT.")
            if not click.confirm("Re-authenticate?"):
                return

    if not quiet:
        click.echo()
        click.echo("🔐 Starting ChatGPT OAuth authentication...")
        click.echo("   Your browser will open automatically")
        click.echo("   (Waiting up to 2 minutes for callback)")
        click.echo()

    success = chatgpt_authenticate_and_save(quiet=quiet)

    if success:
        if not quiet:
            click.echo()
            click.echo("✅ ChatGPT authentication completed successfully!")
            click.echo(f"   Available models: {', '.join(DEFAULT_CODEX_MODELS[:4])}")
            click.echo("   Use: gac -m chatgpt-oauth:gpt-5.4")
    else:
        click.echo("❌ ChatGPT authentication failed.")
        click.echo("   Please try again or check your network connection.")
        raise click.ClickException("ChatGPT authentication failed")


@chatgpt.command("logout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def chatgpt_logout(quiet: bool = False) -> None:
    """Logout from ChatGPT and remove stored tokens."""
    token_store = TokenStore()
    existing_token = token_store.get_token("chatgpt-oauth")

    if not existing_token:
        if not quiet:
            click.echo("Not currently authenticated with ChatGPT.")
        return

    try:
        chatgpt_remove_token()
        if not quiet:
            click.echo("✅ Successfully logged out from ChatGPT.")
    except Exception as e:
        click.echo("❌ Failed to remove ChatGPT token.")
        raise click.ClickException("ChatGPT logout failed") from e


@chatgpt.command("status")
def chatgpt_status() -> None:
    """Check ChatGPT authentication status."""
    token_store = TokenStore()
    token = token_store.get_token("chatgpt-oauth")

    if token:
        expired = chatgpt_is_token_expired()
        if expired:
            click.echo("ChatGPT Authentication Status: ⚠️ Token expired")
            click.echo("Run 'gac auth chatgpt login' to re-authenticate.")
        else:
            click.echo("ChatGPT Authentication Status: ✓ Authenticated")
    else:
        click.echo("ChatGPT Authentication Status: ✗ Not authenticated")
        click.echo("Run 'gac auth chatgpt login' to authenticate.")


# ---------------------------------------------------------------------------
# GitHub Copilot commands
# ---------------------------------------------------------------------------


@auth.group("copilot")
def copilot() -> None:
    """Manage GitHub Copilot authentication.

    Use the GitHub Device Flow to authenticate with GitHub Copilot.
    Supports GitHub.com and GitHub Enterprise.
    """
    pass


@copilot.command("login")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.option("--host", default="github.com", help="GitHub hostname (default: github.com)")
def copilot_login(quiet: bool = False, host: str = "github.com") -> None:
    """Login to GitHub Copilot using Device Flow.

    Opens a browser for you to authorize with GitHub. Supports GitHub Enterprise
    via the --host flag (e.g. --host ghe.mycompany.com).

    After authentication, you can use Copilot models like:
        gac -m copilot:gpt-4.1
    """
    if not quiet:
        setup_logging("INFO")

    # Validate hostname before any network calls
    validated = _normalize_host(host)
    if validated is None:
        raise click.ClickException(f"Invalid or unsafe hostname: {host!r}")
    host = validated

    token_store = TokenStore()
    existing_token = token_store.get_token("copilot")
    if existing_token:
        if not quiet:
            click.echo("✓ Already authenticated with Copilot.")
            if not click.confirm("Re-authenticate?"):
                return

    if not quiet:
        click.echo()
        click.echo("🔐 Starting GitHub Copilot Device Flow authentication…")
        click.echo(f"   Host: {host}")
        click.echo()

    success = copilot_authenticate_and_save(host=host, quiet=quiet)

    if success:
        if not quiet:
            click.echo()
            click.echo("✅ Copilot authentication completed successfully!")
            click.echo(f"   Available models: {', '.join(DEFAULT_COPILOT_MODELS[:5])}")
            click.echo("   Use: gac -m copilot:gpt-4.1")
    else:
        click.echo("❌ Copilot authentication failed.")
        click.echo("   Ensure your GitHub account has Copilot access.")
        raise click.ClickException("Copilot authentication failed")


@copilot.command("logout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
def copilot_logout(quiet: bool = False) -> None:
    """Logout from GitHub Copilot and remove stored tokens."""
    token_store = TokenStore()
    existing_token = token_store.get_token("copilot")

    if not existing_token:
        if not quiet:
            click.echo("Not currently authenticated with Copilot.")
        return

    try:
        copilot_remove_token()
        if not quiet:
            click.echo("✅ Successfully logged out from Copilot.")
    except Exception as e:
        click.echo("❌ Failed to remove Copilot token.")
        raise click.ClickException("Copilot logout failed") from e


@copilot.command("status")
def copilot_status() -> None:
    """Check GitHub Copilot authentication status."""
    token_store = TokenStore()
    token = token_store.get_token("copilot")

    if not token:
        click.echo("Copilot Authentication Status: ✗ Not authenticated")
        click.echo("Run 'gac auth copilot login' to authenticate.")
        return

    # Try to verify the session token is still valid
    valid = copilot_refresh_token_if_expired(quiet=True)
    if valid:
        click.echo("Copilot Authentication Status: ✓ Authenticated")
    else:
        click.echo("Copilot Authentication Status: ⚠️ Token may be expired or revoked")
        click.echo("Run 'gac auth copilot login' to re-authenticate.")
