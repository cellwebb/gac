# Installation Guide for Git Auto Commit (GAC)

## Overview

Git Auto Commit (GAC) is a powerful CLI tool that uses AI to generate meaningful commit messages based on your staged
changes. This guide will walk you through installation, configuration, and getting started.

## Supported Platforms

- macOS, Linux, and Windows (WSL recommended for Windows; native Windows support is available—see
  [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md))

## Prerequisites

- Python 3.10+
- pip or pipx
- Git 2.x
- An API key from a supported AI provider (optional, can be set up interactively with `gac init`)

## Installation Methods

### For Users

Install the latest release system-wide using pipx from the GitHub repository:

```sh
pipx install git+https://github.com/criteria-dev/gac.git
```

To install a specific version (tag, branch, or commit), use:

```sh
pipx install git+https://github.com/criteria-dev/gac.git@<TAG_OR_COMMIT>
```

Replace `<TAG_OR_COMMIT>` with your desired release tag (e.g. `v0.9.1`) or commit hash.

**NOTE:** You can install pipx with:

```sh
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### For Developers

Clone the repository and install in editable mode with development dependencies:

```sh
git clone https://github.com/criteria-dev/gac.git
cd gac
uv pip install -e ".[dev]"
```

This setup is recommended if you want to contribute or run tests locally. For Windows-specific setup, see
[docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md).

## Verifying Installation

After installation, verify that GAC is available:

```sh
gac --version
```

You should see the installed version printed.

## Quick Start

1. **Initialize configuration (recommended):**

```sh
gac init
# Follow the prompts to select provider, model, and enter API keys
```

2. **Stage your changes:**

```sh
git add .
```

3. **Generate a commit message:**

```sh
gac
```

- Generate a one-line commit message: `gac -o`
- Add a hint for the AI: `gac -h "Fix the authentication bug"`
- Add all, auto-confirm commit and push as a one-liner with a hint: `gac -aypo -h "update for release"`

For a full list of CLI flags and advanced usage, see [USAGE.md](USAGE.md).

## Configuration

### Recommended: Interactive Setup

Run `gac init` and follow the prompts to interactively select your provider, model, and securely enter API keys for both
main and backup models if desired. This will create or update your `$HOME/.gac.env` file.

Example `.gac.env` output:

```env
GAC_MODEL='groq:meta-llama/llama-4-scout-17b-16e-instruct'
GROQ_API_KEY='your_groq_key_here'
GAC_BACKUP_MODEL='anthropic:claude-3-5-haiku-latest'
ANTHROPIC_API_KEY='your_anthropic_key_here'
```

You may also set these as environment variables if preferred.

### Manual Provider Setup (Advanced)

GAC supports multiple AI providers. Register for API access at the following links:

- **Groq:** [console.groq.com](https://console.groq.com/) — Set `GAC_MODEL` and `GROQ_API_KEY`
- **Anthropic:** [console.anthropic.com](https://console.anthropic.com/) — Set `GAC_MODEL` and `ANTHROPIC_API_KEY`
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — Set `GAC_MODEL` and
  `OPENAI_API_KEY`
- **OpenRouter:** [openrouter.ai](https://openrouter.ai/) — Set `GAC_MODEL` and `OPENROUTER_API_KEY`

For backup models, set `GAC_BACKUP_MODEL` and the corresponding API key as above.

### Best Practices

- Use a project-level `.gac.env` for project-specific configuration
- Use a user-level `$HOME/.gac.env` for your personal default settings
- Keep sensitive information like API keys out of version control

### Troubleshooting

- Use `gac --verbose` to see detailed configuration loading information
- Check that configuration files have correct permissions
- Ensure configuration files are valid and follow the correct format

## Where to Get Help

- For troubleshooting and advanced tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For usage and CLI options, see [USAGE.md](USAGE.md)
- To contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For Windows setup, see [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md)
- License information: [LICENSE](LICENSE)
