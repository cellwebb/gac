# gac (Git Auto Commit)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue.svg)](https://www.python.org/downloads/)
[![CLA assistant](https://cla-assistant.io/readme/badge/criteria-dev/gac)](https://cla-assistant.io/criteria-dev/gac)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/CONTRIBUTING.md)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Status](https://github.com/criteria-dev/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/criteria-dev/gac/actions)
[![codecov](https://codecov.io/gh/criteria-dev/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/criteria-dev/gac)

## Features

- Generates clear, context-aware commit messages using AI
- Enriches commit messages with repository structure and recent history
- Simple CLI workflow, drop-in replacement for `git commit`
- Easily manage configuration with `gac config` subcommands

## How It Works

GAC analyzes your staged changes, repository structure, and recent commit history to generate high-quality commit
messages with the help of leading AI models.

## How to Use

```sh
git add .
gac
```

![Simple GAC Usage](assets/gac-simple-usage.png)

### Basic Commands

- Generate a commit message: `gac`
- Generate a one-line commit message: `gac -o`
- Add a hint for the AI: `gac -h "Fix the authentication bug"`
- Advanced usage: Add all, auto-confirm, push a one-liner with a hint: `gac -aypo -h "update for release"`

### Configuration Commands

- **Initialize interactively**: `gac init` (recommended for new users)
- **Manage configuration**: Use `gac config` commands to view, set, or unset config values:
  - Show config: `gac config show`
  - Set a value: `gac config set GAC_MODEL groq:meta-llama/llama-4-scout-17b-16e-instruct`
  - Get a value: `gac config get GAC_MODEL`
  - Unset a value: `gac config unset GAC_MODEL`

See [docs/USAGE.md](docs/USAGE.md) for a full list of CLI flags and advanced usage.

## Quick Start

1. **Install**

   ```sh
   # Install pipx if you don't have it
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath

   # Install gac
   pipx install git+https://github.com/criteria-dev/gac.git
   ```

   Verify installation:

   ```sh
   gac --version
   ```

   Windows users: see the Windows setup section in
   [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md).

   For more installation options, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

2. **Configure**

   Create a `$HOME/.gac.env` file (user-level config) with the interactive setup command:

   ```sh
   gac init
   ```

   This will guide you to select a provider, model, and securely enter API keys.

   Example `.gac.env` output:

   ```env
   GAC_MODEL=anthropic:claude-3-5-haiku-latest
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

   Or set as environment variables:

   ```sh
   export GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
   export GROQ_API_KEY=your_groq_key_here
   ```

   For more configuration options, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

3. **Verify**

   Test that GAC is working properly:

   ```sh
   # Make a change to a file
   echo "# Test change" >> README.md
   git add README.md
   gac -o # Generate a one-line commit message
   ```

## Best Practices

- GAC loads configuration from two locations (in order of precedence):
  1. User-level `$HOME/.gac.env` (applies to all projects for the user)
  2. Project-level `.env` (in the project root, overrides user config if present) Environment variables always take
     final precedence over both files.
- Keep API keys out of version control
- For troubleshooting and advanced tips, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- For Windows setup, see [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md)

## Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Community & Support

For questions, suggestions, or support, please open an issue or discussion on GitHub.
