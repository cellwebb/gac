# Using ChatGPT OAuth with GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC supports authentication via ChatGPT OAuth, allowing you to use your ChatGPT subscription to access OpenAI's Codex API instead of paying for OpenAI API keys separately. This mirrors the same OAuth flow used by OpenAI's Codex CLI.

> ⚠️ **Heads up — unsanctioned use:** This uses the same OAuth flow as OpenAI's Codex CLI, and while it currently works, OpenAI may restrict third-party token usage at any time. GAC is small enough that it has flown under the radar so far, but using ChatGPT OAuth here is **not officially sanctioned** for third-party tools and could stop working at any time. If you need reliable commit-message generation, use a direct API provider (`openai`, etc.) instead. See [OpenAI's Codex documentation](https://openai.com/codex) for the current policy.

## What is ChatGPT OAuth?

ChatGPT OAuth lets you leverage your existing ChatGPT Plus or Pro subscription to access the Codex API for generating commit messages. Instead of managing API keys and per-token billing, you authenticate once via your browser and GAC handles the token lifecycle automatically.

## Benefits

- **Cost effective**: Use your existing ChatGPT Plus/Pro subscription instead of paying separately for API access
- **Same models**: Access Codex-optimized models (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **No API key management**: Browser-based OAuth means no API keys to rotate or store
- **Separate billing**: ChatGPT OAuth usage is separate from direct OpenAI API billing

## Setup

GAC includes built-in OAuth authentication for ChatGPT. The setup process is fully automated and will open your browser for authentication.

### Option 1: During Initial Setup (Recommended)

When running `gac init`, simply select "ChatGPT OAuth" as your provider:

```bash
gac init
```

The wizard will:

1. Ask you to select "ChatGPT OAuth" from the provider list
2. Automatically open your browser for OAuth authentication
3. Save your access token to `~/.gac/oauth/chatgpt-oauth.json`
4. Set the default model

### Option 2: Switch to ChatGPT OAuth Later

If you already have GAC configured with another provider and want to switch to ChatGPT OAuth:

```bash
gac model
```

Then:

1. Select "ChatGPT OAuth" from the provider list
2. Your browser will open automatically for OAuth authentication
3. Token saved to `~/.gac/oauth/chatgpt-oauth.json`
4. Model configured automatically

### Use GAC Normally

Once authenticated, use GAC as usual:

```bash
# Stage your changes
git add .

# Generate and commit with ChatGPT OAuth
gac

# Or override the model for a single commit
gac -m chatgpt-oauth:gpt-5.4
```

## Available Models

ChatGPT OAuth provides access to Codex-optimized models. Current models include:

- `gpt-5.5` — Latest and most capable Codex model
- `gpt-5.4` — Previous generation Codex model
- `gpt-5.3-codex` — Third generation Codex model

Check the [OpenAI documentation](https://platform.openai.com/docs/models) for the full list of available models.

## CLI Commands

GAC provides dedicated CLI commands for ChatGPT OAuth management:

### Login

Authenticate or re-authenticate with ChatGPT OAuth:

```bash
gac auth chatgpt login
```

Your browser will open automatically to complete the OAuth flow. If you're already authenticated, this will refresh your tokens.

### Logout

Remove stored ChatGPT OAuth tokens:

```bash
gac auth chatgpt logout
```

This deletes the stored token file at `~/.gac/oauth/chatgpt-oauth.json`.

### Status

Check your current ChatGPT OAuth authentication status:

```bash
gac auth chatgpt status
```

Or check all providers at once:

```bash
gac auth
```

## Troubleshooting

### Token Expired

If you see authentication errors, your token may have expired. Re-authenticate by running:

```bash
gac auth chatgpt login
```

Your browser will open automatically for fresh OAuth authentication. GAC automatically uses refresh tokens to renew access without re-authentication when possible.

### Check Authentication Status

To check if you're currently authenticated:

```bash
gac auth chatgpt status
```

Or check all providers at once:

```bash
gac auth
```

### Logout

To remove your stored token:

```bash
gac auth chatgpt logout
```

### "ChatGPT OAuth token not found"

This means GAC can't find your access token. Authenticate by running:

```bash
gac model
```

Then select "ChatGPT OAuth" from the provider list. The OAuth flow will start automatically.

### "Authentication failed"

If OAuth authentication fails:

1. Make sure you have an active ChatGPT Plus or Pro subscription
2. Check that your browser opens correctly
3. Try a different browser if issues persist
4. Verify network connectivity to `auth.openai.com`
5. Check that ports 1455-1465 are available for the local callback server

### Port Already in Use

The OAuth callback server tries ports 1455-1465 automatically. If all ports are occupied:

```bash
# On macOS/Linux:
lsof -ti:1455-1465 | xargs kill -9

# On Windows (PowerShell):
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Then re-run `gac auth chatgpt login`.

## Differences from OpenAI Provider

| Feature          | OpenAI (`openai:`)         | ChatGPT OAuth (`chatgpt-oauth:`)                 |
| ---------------- | -------------------------- | ------------------------------------------------ |
| Authentication   | API Key (`OPENAI_API_KEY`) | OAuth (automated browser flow)                   |
| Billing          | Per-token API billing      | Subscription-based (ChatGPT Plus/Pro)            |
| Setup            | Manual API key entry       | Automatic OAuth via `gac init` or `gac model`    |
| Token Management | Long-lived API keys        | OAuth tokens (auto-refresh using refresh tokens) |
| Models           | All OpenAI models          | Codex-optimized models                           |

## Security Notes

- **Never commit your access token** to version control
- GAC stores OAuth tokens in `~/.gac/oauth/chatgpt-oauth.json` (outside your project directory)
- OAuth flow uses PKCE (Proof Key for Code Exchange) for enhanced security
- Local callback server runs on localhost only (ports 1455-1465)
- Refresh tokens are used to automatically renew access without re-authentication

## See Also

- [Main Documentation](USAGE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [OpenAI's Codex Documentation](https://openai.com/codex)
