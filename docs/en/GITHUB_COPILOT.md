# Using GitHub Copilot with GAC

**English** | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | [Français](../fr/GITHUB_COPILOT.md) | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC supports authentication via GitHub Copilot, allowing you to use your Copilot subscription to access models from OpenAI, Anthropic, Google, and more — all included with your GitHub Copilot plan.

## What is GitHub Copilot OAuth?

GitHub Copilot OAuth uses the **Device Flow** — a secure, browser-based authentication method that doesn't require a local callback server. You visit a URL, enter a one-time code, and authorize GAC to use your Copilot access. Behind the scenes, GAC exchanges your long-lived GitHub OAuth token for short-lived Copilot session tokens (~30 min) that grant access to the Copilot API.

This gives you access to models from multiple providers through a single subscription:

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Benefits

- **Multi-provider access**: Use models from OpenAI, Anthropic, and Google through a single subscription
- **Cost effective**: Use your existing Copilot subscription instead of paying for separate API keys
- **No API key management**: Device Flow authentication — no keys to rotate or store
- **GitHub Enterprise support**: Works with GHE instances via the `--host` flag

## Setup

### Option 1: During Initial Setup (Recommended)

When running `gac init`, simply select "Copilot" as your provider:

```bash
gac init
```

The wizard will:

1. Ask you to select "Copilot" from the provider list
2. Display a one-time code and open your browser for Device Flow authentication
3. Save your OAuth token to `~/.gac/oauth/copilot.json`
4. Set the default model

### Option 2: Switch to Copilot Later

If you already have GAC configured with another provider:

```bash
gac model
```

Then select "Copilot" from the provider list and authenticate.

### Option 3: Direct Login

Authenticate directly without changing your default model:

```bash
gac auth copilot login
```

### Use GAC Normally

Once authenticated, use GAC as usual:

```bash
# Stage your changes
git add .

# Generate and commit with Copilot
gac

# Or override the model for a single commit
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Available Models

Copilot provides access to models from multiple providers. Current models include:

| Provider  | Models                                                                                         |
| --------- | ---------------------------------------------------------------------------------------------- |
| OpenAI    | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google    | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Note:** The model list shown after login is informational and may go stale as GitHub adds new models. Check the [GitHub Copilot documentation](https://docs.github.com/en/copilot) for the latest available models.

## GitHub Enterprise

To authenticate with a GitHub Enterprise instance:

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC will automatically use the correct Device Flow and API endpoints for your GHE instance. The session token is cached per host, so different GHE instances are handled independently.

## CLI Commands

GAC provides dedicated CLI commands for Copilot authentication management:

### Login

Authenticate or re-authenticate with GitHub Copilot:

```bash
gac auth copilot login
```

Your browser will open to a Device Flow page where you enter a one-time code. If you're already authenticated, this will ask if you want to re-authenticate.

For GitHub Enterprise:

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Logout

Remove stored Copilot tokens:

```bash
gac auth copilot logout
```

This deletes the stored token file at `~/.gac/oauth/copilot.json` and the session cache.

### Status

Check your current Copilot authentication status:

```bash
gac auth copilot status
```

Or check all providers at once:

```bash
gac auth
```

## How It Works

The Copilot authentication flow differs from ChatGPT and Claude Code OAuth:

1. **Device Flow** — GAC requests a device code from GitHub and displays it
2. **Browser authorization** — You visit the URL and enter the code
3. **Token polling** — GAC polls GitHub until you complete authorization
4. **Session token exchange** — The GitHub OAuth token is exchanged for a short-lived Copilot session token
5. **Auto-refresh** — Session tokens (~30 min) are automatically refreshed from the cached OAuth token

Unlike PKCE-based OAuth (ChatGPT/Claude Code), the Device Flow doesn't require a local callback server or port management.

## Troubleshooting

### "Copilot authentication not found"

Run the login command to authenticate:

```bash
gac auth copilot login
```

### "Could not obtain Copilot session token"

This means GAC got a GitHub OAuth token but couldn't exchange it for a Copilot session token. Usually this means:

1. **No Copilot subscription** — Your GitHub account doesn't have an active Copilot subscription
2. **Token revoked** — The OAuth token was revoked; re-authenticate with `gac auth copilot login`

### Session token expired

Session tokens expire after ~30 minutes. GAC automatically refreshes them from the cached OAuth token, so you shouldn't need to re-authenticate frequently. If auto-refresh fails:

```bash
gac auth copilot login
```

### "Invalid or unsafe hostname"

The `--host` flag validates hostnames strictly to prevent SSRF attacks. If you see this error:

- Make sure the hostname doesn't include ports (e.g., use `ghe.company.com` not `ghe.company.com:8080`)
- Don't include protocols or paths (e.g., use `ghe.company.com` not `https://ghe.company.com/api`)
- Private IP addresses and `localhost` are blocked for security

### GitHub Enterprise issues

If GHE authentication fails:

1. Verify your GHE instance has Copilot enabled
2. Check that your GHE hostname is accessible from your machine
3. Ensure your GHE account has a Copilot license
4. Try with the `--host` flag explicitly: `gac auth copilot login --host ghe.mycompany.com`

## Differences from Other OAuth Providers

| Feature         | ChatGPT OAuth             | Claude Code             | Copilot                                      |
| --------------- | ------------------------- | ----------------------- | -------------------------------------------- |
| Auth method     | PKCE (browser callback)   | PKCE (browser callback) | Device Flow (one-time code)                  |
| Callback server | Ports 1455-1465           | Ports 8765-8795         | Not needed                                   |
| Token lifetime  | Long-lived (auto-refresh) | Expiring (re-auth)      | Session ~30 min (auto-refresh)               |
| Models          | Codex-optimized OpenAI    | Claude family           | Multi-provider (OpenAI + Anthropic + Google) |
| GHE support     | No                        | No                      | Yes (`--host` flag)                          |

## Security Notes

- **Never commit your OAuth token** to version control
- GAC stores OAuth tokens in `~/.gac/oauth/copilot.json` (outside your project directory)
- Session tokens are cached in `~/.gac/oauth/copilot_session.json` with `0o600` permissions
- Hostnames are strictly validated to prevent SSRF and URL injection attacks
- Private IP addresses, loopback addresses, and `localhost` are blocked as hostnames
- The Device Flow doesn't expose any local ports, reducing the attack surface

## See Also

- [Main Documentation](USAGE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [ChatGPT OAuth Guide](CHATGPT_OAUTH.md)
- [Claude Code Guide](CLAUDE_CODE.md)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
