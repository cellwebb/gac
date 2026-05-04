"""OAuth authentication utilities for GAC.

Provider-specific imports should be made directly:

    from gac.oauth.claude_code import authenticate_and_save
    from gac.oauth.chatgpt import authenticate_and_save

The top-level names (authenticate_and_save, etc.) are kept for backward
compatibility and delegate to the Claude Code provider.
"""

from .claude_code import (
    authenticate_and_save,
    is_token_expired,
    load_stored_token,
    perform_oauth_flow,
    refresh_token_if_expired,
    remove_token,
    save_token,
)
from .token_store import OAuthToken, TokenStore

__all__ = [
    # Backward-compatible top-level names (Claude Code)
    "authenticate_and_save",
    "is_token_expired",
    "load_stored_token",
    "perform_oauth_flow",
    "refresh_token_if_expired",
    "remove_token",
    "save_token",
    # Shared
    "OAuthToken",
    "TokenStore",
]
