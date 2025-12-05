# Using Qwen.ai with GAC

**English** | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | [Français](../fr/QWEN.md) | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

GAC supports authentication via Qwen.ai OAuth, allowing you to use your Qwen.ai account for commit message generation. This uses OAuth device flow authentication for a seamless login experience.

## What is Qwen.ai?

Qwen.ai is Alibaba Cloud's AI platform that provides access to the Qwen family of large language models. GAC supports OAuth-based authentication, allowing you to use your Qwen.ai account without needing to manage API keys manually.

## Benefits

- **Easy authentication**: OAuth device flow - just log in with your browser
- **No API key management**: Authentication is handled automatically
- **Access to Qwen models**: Use powerful Qwen models for commit message generation

## Setup

GAC includes built-in OAuth authentication for Qwen.ai using the device flow. The setup process will display a code and open your browser for authentication.

### Option 1: During Initial Setup (Recommended)

When running `gac init`, simply select "Qwen.ai (OAuth)" as your provider:

```bash
gac init
```

The wizard will:

1. Ask you to select "Qwen.ai (OAuth)" from the provider list
2. Display a device code and open your browser
3. You'll authenticate on Qwen.ai and enter the code
4. Save your access token securely
5. Set the default model

### Option 2: Switch to Qwen.ai Later

If you already have GAC configured with another provider and want to switch to Qwen.ai:

```bash
gac model
```

Then:

1. Select "Qwen.ai (OAuth)" from the provider list
2. Follow the device code authentication flow
3. Token saved securely to `~/.gac/oauth/qwen.json`
4. Model configured automatically

### Option 3: Direct Login

You can also authenticate directly using:

```bash
gac auth qwen login
```

This will:

1. Display a device code
2. Open your browser to the Qwen.ai authentication page
3. After you authenticate, the token is saved automatically

### Use GAC Normally

Once authenticated, use GAC as usual:

```bash
# Stage your changes
git add .

# Generate and commit with Qwen.ai
gac

# Or override the model for a single commit
gac -m qwen:qwen3-coder-plus
```

## Available Models

The Qwen.ai OAuth integration uses:

- `qwen3-coder-plus` - Optimized for coding tasks (default)

This is the model available through the portal.qwen.ai OAuth endpoint. For other Qwen models, consider using the OpenRouter provider which offers additional Qwen model options.

## Authentication Commands

GAC provides several commands for managing Qwen.ai authentication:

```bash
# Login to Qwen.ai
gac auth qwen login

# Check authentication status
gac auth qwen status

# Logout and remove stored token
gac auth qwen logout

# Check all OAuth providers status
gac auth
```

### Login Options

```bash
# Standard login (opens browser automatically)
gac auth qwen login

# Login without opening browser (displays URL to visit manually)
gac auth qwen login --no-browser

# Quiet mode (minimal output)
gac auth qwen login --quiet
```

## Troubleshooting

### Token Expired

If you see authentication errors, your token may have expired. Re-authenticate by running:

```bash
gac auth qwen login
```

The device code flow will start, and your browser will open for re-authentication.

### Check Authentication Status

To check if you're currently authenticated:

```bash
gac auth qwen status
```

Or check all providers at once:

```bash
gac auth
```

### Logout

To remove your stored token:

```bash
gac auth qwen logout
```

### "Qwen authentication not found"

This means GAC can't find your access token. Authenticate by running:

```bash
gac auth qwen login
```

Or run `gac model` and select "Qwen.ai (OAuth)" from the provider list.

### "Authentication failed"

If OAuth authentication fails:

1. Make sure you have a Qwen.ai account
2. Check that your browser opens correctly
3. Verify you entered the device code correctly
4. Try a different browser if issues persist
5. Verify network connectivity to `qwen.ai`

### Device Code Not Working

If the device code authentication isn't working:

1. Make sure the code hasn't expired (codes are valid for a limited time)
2. Try running `gac auth qwen login` again for a fresh code
3. Use `--no-browser` flag and manually visit the URL if browser opening fails

## Security Notes

- **Never commit your access token** to version control
- GAC automatically stores tokens in `~/.gac/oauth/qwen.json` (outside your project directory)
- Token files have restricted permissions (readable only by owner)
- Tokens may expire and will require re-authentication
- The OAuth device flow is designed for secure authentication on headless systems

## See Also

- [Main Documentation](USAGE.md)
- [Claude Code Setup](CLAUDE_CODE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Qwen.ai Documentation](https://qwen.ai)
