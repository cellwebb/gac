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
pipx install \
  git+https://github.com/cellwebb/gac.git@<TAG_OR_COMMIT>
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

### Manual Configuration

You can configure GAC by setting environment variables or by creating a config file in your home or project directory.

### Option 1: Config File (Recommended)

Create a `.gac.env` or `.env` file in your project directory, or a `.gac.env` file in your home directory:

```sh
# Project-specific config (highest priority after env vars)
echo 'GAC_MODEL=anthropic:claude-3-5-haiku-latest' > .gac.env

# Or for all projects (user-wide)
echo 'GAC_MODEL=anthropic:claude-3-5-haiku-latest' > ~/.gac.env

# Add your API key
echo 'ANTHROPIC_API_KEY=your_key_here' >> ~/.gac.env
```

### Option 2: Environment Variables

Set variables directly in your shell (overrides config files):

```sh
export GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct  # Required
export GAC_BACKUP_MODEL=anthropic:claude-3-5-haiku-latest        # Optional
export ANTHROPIC_API_KEY=your_key_here               # API key
export GROQ_API_KEY=your_key_here               # API key
export GAC_USE_FORMATTING=true                       # Optional
export GAC_MAX_OUTPUT_TOKENS=512                     # Optional
export GAC_TEMPERATURE=0.7                           # Optional
```

### Configuration Locations

GAC loads configuration from multiple locations with the following precedence (highest to lowest):

1. **Environment variables** (set in your terminal session)
2. **Project config files** (`.env` then `.gac.env` in your current directory)
3. **User config file** (`~/.gac.env` in your home directory)
4. **Package config** (`_config.env` installed with the module)
5. **Built-in defaults**

This lets you:

- Set project-specific overrides (in your repo)
- Use personal defaults (in your home directory)
- Share team-wide settings (via package config)

### Configuration Resolution Example

```bash
# Command-line argument takes highest priority
gac -m anthropic:claude-3-5-haiku-latest

# Project .gac.env (highest priority after CLI)
# /path/to/project/.gac.env
GAC_MODEL=anthropic:claude-3-5-haiku-latest
ANTHROPIC_API_KEY=your_key_here
GAC_TEMPERATURE=0.7

# User-level ~/.gac.env
GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
GROQ_API_KEY=user_api_key

# Package-level config.env
GAC_MODEL=anthropic:claude-3-5-haiku-latest
```

In this example:

- The CLI argument `anthropic:claude-3-5-haiku-latest` would be used
- If no CLI model is specified, the project's `openai:gpt-4` would be used
- Without a project config, the user-level `groq:llama-3` would be used
- If no other configuration is found, the package-level default is used

### Best Practices

- Use project-level `.gac.env` for project-specific configurations
- Use user-level `~/.gac.env` for personal default settings
- Keep sensitive information like API keys out of version control
- Use environment variables for dynamic or sensitive configurations

### Troubleshooting

- Use `gac --verbose` to see detailed configuration loading information
- Check that configuration files have correct permissions
- Ensure configuration files are valid and follow the correct format

## Advanced Usage

### Local Model Support (Ollama)

1. Install [Ollama](https://ollama.com/)
2. Pull a model:

```bash
ollama pull llama3
```

3. Use with GAC:

```bash
gac -m ollama:llama3
```

### Command-Line Options

```bash
# Stage all changes and commit
gac -a

# Use a specific model
gac -m openai:gpt-4o-mini

# Generate one-line commit message
gac -o

# Provide context hint
gac -h "Fix authentication bug"
```

## Troubleshooting

### Common Issues

- **API Key Problems**: Verify your API key and provider configuration
- **Model Unavailability**: Check model support and accessibility
- **Formatting Errors**: Ensure required formatters are installed

### Debugging

```bash
# Enable debug logging
gac --log-level=DEBUG

# Show prompt sent to AI
gac --show-prompt
```

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for information on contributing to GAC.

## License

GAC is released under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.
