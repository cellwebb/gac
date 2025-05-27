# GAC Command-Line Usage

This document describes all available flags and options for the `gac` CLI tool.

## Table of Contents

- [GAC Command-Line Usage](#gac-command-line-usage)
  - [Table of Contents](#table-of-contents)
  - [Basic Usage](#basic-usage)
  - [Core Workflow Flags](#core-workflow-flags)
  - [Message Customization](#message-customization)
  - [Output and Verbosity](#output-and-verbosity)
  - [Help and Version](#help-and-version)
  - [Example Workflows](#example-workflows)
  - [Advanced](#advanced)
  - [Configuration Notes](#configuration-notes)
    - [Configuration Subcommands](#configuration-subcommands)
  - [Getting Help](#getting-help)

## Basic Usage

```sh
gac init
# Then follow the prompts to configure your provider, model, and API keys interactively
gac
```

Generates an AI-powered commit message for staged changes and opens an editor for confirmation.

---

## Core Workflow Flags

| Flag / Option | Short | Description                                       |
| ------------- | ----- | ------------------------------------------------- |
| `--add-all`   | `-a`  | Stage all changes before committing               |
| `--push`      | `-p`  | Push changes to remote after committing           |
| `--yes`       | `-y`  | Automatically confirm commit without prompting    |
| `--dry-run`   |       | Show what would happen without making any changes |

## Message Customization

| Flag / Option     | Short | Description                              |
| ----------------- | ----- | ---------------------------------------- |
| `--one-liner`     | `-o`  | Generate a single-line commit message    |
| `--hint <text>`   | `-h`  | Add a hint to guide the AI               |
| `--model <model>` | `-m`  | Specify the model to use for this commit |

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
| `--version`   |       | Show GAC version and exit  |
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

## Configuration Notes

- The recommended way to set up GAC is to run `gac init` and follow the interactive prompts.
- GAC loads configuration in the following order of precedence:
  1. CLI flags
  2. Environment variables
  3. Project-level `.gac.env`
  4. User-level `~/.gac.env`

### Configuration Subcommands

The following subcommands manage configuration of your `$HOME/.gac.env` file:

- `gac config show` — Show current configuration
- `gac config set KEY VALUE` — Set a config key (value is always stored as a string)
- `gac config get KEY` — Get a config value
- `gac config unset KEY` — Remove a config key

## Getting Help

- For troubleshooting and advanced tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For installation and configuration, see [INSTALLATION.md](INSTALLATION.md)
- For Windows setup, see [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md)
- To contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
- License information: [LICENSE](LICENSE)
