"""ChatGPT OAuth configuration and constants.

Matches OpenAI's Codex CLI auth flow (same client_id, PKCE, callback port).
"""

from typing import Any

# OAuth endpoints, client, and Codex API settings
CHATGPT_OAUTH_CONFIG: dict[str, Any] = {
    "issuer": "https://auth.openai.com",
    "auth_url": "https://auth.openai.com/oauth/authorize",
    "token_url": "https://auth.openai.com/oauth/token",
    "api_base_url": "https://chatgpt.com/backend-api/codex",
    "client_id": "app_EMoamEEZ73f0CkXaXp7hrann",
    "scope": "openid profile email offline_access",
    "redirect_host": "http://localhost",
    "redirect_path": "auth/callback",
    # Preferred port is 1455 (matching Codex CLI), but we try a range if occupied
    "callback_port_range": (1455, 1465),
    "callback_timeout": 120,
    "provider_key": "chatgpt-oauth",
    "api_key_env_var": "CHATGPT_OAUTH_API_KEY",
    "client_version": "0.72.0",
    "originator": "codex_cli_rs",
}

# Known Codex-compatible models
DEFAULT_CODEX_MODELS: list[str] = [
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.3-instant",
    "gpt-5.3-codex-spark",
    "gpt-5.3-codex",
    "gpt-5.2-codex",
    "gpt-5.2",
]
