# Using Claude Code with GAC

**English** | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | [Français](../fr/CLAUDE_CODE.md) | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC supports authentication via Claude Code subscriptions, allowing you to use your Claude Code subscription instead of paying for the expensive Anthropic API. This is perfect for users who already have Claude Code access through their subscription.

## What is Claude Code?

Claude Code is Anthropic's subscription service that provides OAuth-based access to Claude models. Instead of using API keys (which are billed per-token), Claude Code uses OAuth tokens from your subscription.

## Benefits

- **Cost effective**: Use your existing Claude Code subscription instead of paying separately for API access
- **Same models**: Access the same Claude models (e.g., `claude-sonnet-4-5`)
- **Separate billing**: Claude Code usage is separate from Anthropic API billing

## Setup

GAC includes built-in OAuth authentication for Claude Code. The setup process is fully automated and will open your browser for authentication.

### Option 1: During Initial Setup (Recommended)

When running `gac init`, simply select "Claude Code" as your provider:

```bash
gac init
```

The wizard will:

1. Ask you to select "Claude Code" from the provider list
2. Automatically open your browser for OAuth authentication
3. Save your access token to `~/.gac.env`
4. Set the default model

### Option 2: Switch to Claude Code Later

If you already have GAC configured with another provider and want to switch to Claude Code:

```bash
gac model
```

Then:

1. Select "Claude Code" from the provider list
2. Your browser will open automatically for OAuth authentication
3. Token saved to `~/.gac.env`
4. Model configured automatically

### Use GAC Normally

Once authenticated, use GAC as usual:

```bash
# Stage your changes
git add .

# Generate and commit with Claude Code
gac

# Or override the model for a single commit
gac -m claude-code:claude-sonnet-4-5
```

## Available Models

Claude Code provides access to the same models as the Anthropic API. Current Claude 4.5 family models include:

- `claude-sonnet-4-5` - Latest and most intelligent Sonnet model, best for coding
- `claude-haiku-4-5` - Fast and efficient
- `claude-opus-4-1` - Most capable model for complex reasoning

Check the [Claude documentation](https://docs.claude.com/en/docs/about-claude/models/overview) for the full list of available models.

## Troubleshooting

### Token Expired

If you see authentication errors, your token may have expired. Re-authenticate by running:

```bash
gac model
```

Then select "Claude Code" and choose "Re-authenticate (get new token)". Your browser will open for fresh OAuth authentication.

### "CLAUDE_CODE_ACCESS_TOKEN not found"

This means GAC can't find your access token. Authenticate by running:

```bash
gac model
```

Then select "Claude Code" from the provider list. The OAuth flow will start automatically.

### "Authentication failed"

If OAuth authentication fails:

1. Make sure you have an active Claude Code subscription
2. Check that your browser opens correctly
3. Try a different browser if issues persist
4. Verify network connectivity to `claude.ai`
5. Check that ports 8765-8795 are available for the local callback server

## Differences from Anthropic Provider

| Feature          | Anthropic (`anthropic:`)      | Claude Code (`claude-code:`)                        |
| ---------------- | ----------------------------- | --------------------------------------------------- |
| Authentication   | API Key (`ANTHROPIC_API_KEY`) | OAuth (automated browser flow)                      |
| Billing          | Per-token API billing         | Subscription-based                                  |
| Setup            | Manual API key entry          | Automatic OAuth via `gac init` or `gac model`       |
| Token Management | Long-lived API keys           | OAuth tokens (can expire, easy re-auth via `model`) |
| Models           | Same models                   | Same models                                         |

## Security Notes

- **Never commit your access token** to version control
- GAC automatically stores tokens in `~/.gac.env` (outside your project directory)
- Tokens may expire and will require re-authentication via `gac model`
- The OAuth flow uses PKCE (Proof Key for Code Exchange) for enhanced security
- Local callback server runs on localhost only (ports 8765-8795)

## See Also

- [Main Documentation](USAGE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Claude Code Documentation](https://claude.ai/code)
