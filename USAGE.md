# GAC Command-Line Usage

This document describes all available flags and options for the `gac` CLI tool.

## Basic Usage

```sh
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

See [INSTALLATION.md](INSTALLATION.md) for setup, and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for help. Return to
[README.md](README.md) for a project overview.
