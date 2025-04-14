# Installation Guide for Git Auto Commit (GAC)

## Overview

Git Auto Commit (GAC) is a powerful CLI tool that uses AI to generate meaningful commit messages based on your staged
changes. This guide will walk you through installation, configuration, and getting started.

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

Replace `<TAG_OR_COMMIT>` with your desired release tag (e.g. `v1.2.3`) or commit hash.

If you don't have pipx, install it with:

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

This setup is recommended if you want to contribute or run tests locally.

## Quick Start

1. Stage your changes:

```sh
git add .
```

2. Generate a commit message:

```sh
gac
```

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
