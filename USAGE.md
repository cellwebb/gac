# gac Command-Line Usage

This document describes all available flags and options for the `gac` CLI tool.

## Table of Contents

- [gac Command-Line Usage](#gac-command-line-usage)
  - [Table of Contents](#table-of-contents)
  - [Basic Usage](#basic-usage)
  - [Core Workflow Flags](#core-workflow-flags)
  - [Message Customization](#message-customization)
  - [Output and Verbosity](#output-and-verbosity)
  - [Help and Version](#help-and-version)
  - [Example Workflows](#example-workflows)
  - [Advanced](#advanced)
    - [Skipping Pre-commit Hooks](#skipping-pre-commit-hooks)
  - [Configuration Notes](#configuration-notes)
    - [Configuration Subcommands](#configuration-subcommands)
  - [Getting Help](#getting-help)

## Basic Usage

```sh
gac init
# Then follow the prompts to configure your provider, model, and API keys interactively
gac
```

Generates an AI-powered commit message for staged changes and prompts for confirmation. The confirmation prompt accepts:

- `y` or `yes` - Proceed with the commit
- `n` or `no` - Cancel the commit
- `r` or `reroll` - Regenerate the commit message with the same context
- `r <feedback>` - Regenerate with specific feedback (e.g., `r make it shorter`, `r focus on performance`)

---

## Core Workflow Flags

| Flag / Option | Short | Description                                       |
| ------------- | ----- | ------------------------------------------------- |
| `--add-all`   | `-a`  | Stage all changes before committing               |
| `--push`      | `-p`  | Push changes to remote after committing           |
| `--yes`       | `-y`  | Automatically confirm commit without prompting    |
| `--dry-run`   |       | Show what would happen without making any changes |
| `--no-verify` |       | Skip pre-commit hooks when committing             |

## Message Customization

| Flag / Option     | Short | Description                                 |
| ----------------- | ----- | ------------------------------------------- |
| `--one-liner`     | `-o`  | Generate a single-line commit message       |
| `--hint <text>`   | `-h`  | Add a hint to guide the AI                  |
| `--model <model>` | `-m`  | Specify the model to use for this commit    |
| `--scope <scope>` | `-s`  | Specify the scope of changes for the commit |

**Note:** You can also provide feedback interactively during the reroll process by typing `r <feedback>` at the prompt.

## Output and Verbosity

| Flag / Option         | Short | Description                                            |
| --------------------- | ----- | ------------------------------------------------------ |
| `--quiet`             | `-q`  | Suppress all output except errors                      |
| `--log-level <level>` |       | Set log level (DEBUG, INFO, WARNING, ERROR)            |
| `--show-prompt`       |       | Print the AI prompt used for commit message generation |
| `--verbose`           | `-v`  | Increase output verbosity to INFO                      |

## Help and Version

| Flag / Option | Short | Description                |
| ------------- | ----- | -------------------------- |
| `--version`   |       | Show gac version and exit  |
| `--help`      |       | Show help message and exit |

---

## Example Workflows

- **Stage all changes and commit:**

  ```sh
  gac -a
  ```

- **Commit and push in one step:**

  ```sh
  gac -ap
  ```

- **Generate a one-line commit message:**

  ```sh
  gac -o
  ```

- **Add a hint for the AI:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **Specify the scope of changes:**

  ```sh
  gac -s "auth"
  ```

- **Use a specific model just for this commit:**

  ```sh
  gac -m anthropic:claude-3-5-haiku-latest
  ```

- **Dry run (see what would happen):**

  ```sh
  gac --dry-run
  ```

## Advanced

- Combine flags for more powerful workflows (e.g., `gac -ayp` to stage, auto-confirm, and push)
- Use `--show-prompt` to debug or review the prompt sent to the AI
- Adjust verbosity with `--log-level` or `--quiet`

### Skipping Pre-commit Hooks

The `--no-verify` flag allows you to skip any pre-commit hooks configured in your project:

```sh
gac --no-verify  # Skip all pre-commit hooks
```

**Use `--no-verify` when:**

- Pre-commit hooks are failing temporarily
- Working with time-consuming hooks
- Committing work-in-progress code that doesn't pass all checks yet

**Note:** Use with caution as pre-commit hooks maintain code quality standards.

## Configuration Notes

- The recommended way to set up gac is to run `gac init` and follow the interactive prompts.
- gac loads configuration in the following order of precedence:
  1. CLI flags
  2. Environment variables
  3. Project-level `.gac.env`
  4. User-level `~/.gac.env`

### Advanced Configuration Options

You can customize gac's behavior with these optional environment variables:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Automatically infer and include scope in commit messages (e.g., `feat(auth):` vs `feat:`)
- `GAC_TEMPERATURE=0.7` - Control AI creativity (0.0-1.0, lower = more focused)
- `GAC_MAX_OUTPUT_TOKENS=512` - Maximum tokens for generated messages
- `GAC_WARNING_LIMIT_TOKENS=4096` - Warn when prompts exceed this token count

See `.gac.env.example` for a complete configuration template.

### Configuration Subcommands

The following subcommands manage configuration of your `$HOME/.gac.env` file:

- `gac config show` — Show current configuration
- `gac config set KEY VALUE` — Set a config key (value is always stored as a string)
- `gac config get KEY` — Get a config value
- `gac config unset KEY` — Remove a config key

## Getting Help

- For troubleshooting and advanced tips, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- For installation and configuration, see [README.md#installation-and-configuration](README.md#installation-and-configuration)
- To contribute, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- License information: [LICENSE](LICENSE)
