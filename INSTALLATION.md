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
- An API key from a supported AI provider (optional)

## Installation Methods

### For Users

Install the latest release system-wide using pipx from the GitHub repository:

```sh
pipx install git+https://github.com/cellwebb/gac.git
```

To install a specific version (tag, branch, or commit), use:

```sh
pipx install git+https://github.com/cellwebb/gac.git@<TAG_OR_COMMIT>
```

Replace `<TAG_OR_COMMIT>` with your desired release tag (e.g. `v0.9.1`) or commit hash.

If you don't have pipx, you can install it with:

```sh
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### For Developers

Clone the repository and install in editable mode with development dependencies:

```sh
git clone https://github.com/cellwebb/gac.git
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

1. Stage your changes:

```sh
git add .
```

2. Generate a commit message:

```sh
gac
```

- Generate a one-line commit message: `gac -o`
- Add a hint for the AI: `gac -h "Fix the authentication bug"`
- Add all, auto-confirm commit and push with a one-liner with a hint: `gac -aypo -h "update for release"`

For a full list of CLI flags and advanced usage, see [USAGE.md](USAGE.md).

## Configuration

### AI Provider Setup

GAC supports multiple AI providers:

#### Groq (Recommended)

1. Register at [console.groq.com](https://console.groq.com/)
2. Create an API key
3. Set the environment variable:

```bash
export GROQ_API_KEY=your_key_here
```

#### Anthropic Claude (Recommended alternative)

1. Register at [console.anthropic.com](https://console.anthropic.com/)
2. Create an API key
3. Set the environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

#### Other Providers

- OpenAI: Set `OPENAI_API_KEY`
- Mistral: Set `MISTRAL_API_KEY`

### Basic Configuration Example

The minimum required configuration is to specify a model and provide an API key for your chosen provider. This can be
done in a config file or as environment variables.

**Example: `.gac.env` (recommended)**

```sh
GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
GROQ_API_KEY=your_key_here
```

**Or as environment variables:**

```sh
export GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
export GROQ_API_KEY=your_key_here
```

That's it! For most users, this is all you need to get started.

### Best Practices

- Use a project-level `.gac.env` for project-specific configuration
- Use a user-level `~/.gac.env` for your personal default settings
- Keep sensitive information like API keys out of version control
- Use environment variables for sensitive or temporary overrides

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
