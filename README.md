# GAC (Git Auto Commit)

AI-assisted git commit message generator.

## Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed installation instructions.

## Configuration

### Configuration File Precedence

GAC uses a sophisticated, multi-level configuration system to provide flexible and intuitive configuration management.
The configuration is loaded in the following order of precedence (from highest to lowest):

1. **Command-line Arguments** (Highest Priority)

   - Directly passed arguments override all other configuration sources
   - Example: `gac -m anthropic:claude-3-5-haiku-latest`

2. **Project-level Configuration** (`.gac.env`)

   - Located in the current project's root directory
   - Applies only to the specific project
   - Overrides user-level and package-level configurations

3. **User-level Configuration** (`~/.gac.env`)

   - Located in the user's home directory
   - Applies to all projects for the current user
   - Overrides package-level configurations

4. **Package-level Configuration** (`config.env`)

   - Included with the GAC package installation
   - Provides default fallback configurations
   - Lowest priority configuration source

5. **Built-in Default Values** (Lowest Priority)
   - Hardcoded default settings within the application
   - Used only if no other configuration is specified

#### Configuration Resolution Example

```bash
# Command-line argument (highest priority)
gac -m anthropic:claude-3-5-haiku-latest

# Project .gac.env
GAC_MODEL=openai:gpt-4
GAC_TEMPERATURE=0.7

# User-level ~/.gac.env
GAC_MODEL=groq:llama-3
GAC_API_KEY=user_api_key

# Package-level config.env
GAC_MODEL=anthropic:claude-3-5-haiku-latest
```

In this example:

- The CLI argument `anthropic:claude-3-5-haiku-latest` would be used
- If no CLI model is specified, the project's `openai:gpt-4` would be used
- Without a project config, the user-level `groq:llama-3` would be used
- If no other configuration is found, the package-level default is used

### Markdown Linting

This project uses `markdownlint-cli2` for Markdown linting. The configuration is in `.markdownlint-cli2.yaml`.

> **Note**: The `.markdownlint.yaml` file is now deprecated and can be removed.

## Usage

More details coming soon.

## Best Practices

- Use project-level `.gac.env` for project-specific configurations
- Use user-level `~/.gac.env` for personal default settings
- Keep sensitive information like API keys out of version control
- Use environment variables for dynamic or sensitive configurations

## Troubleshooting

- Use `gac --verbose` to see detailed configuration loading information
- Check that configuration files have correct permissions
- Ensure configuration files are valid and follow the correct format
