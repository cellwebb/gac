# gac Command-Line Usage

**English** | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | [Français](../fr/USAGE.md) | [Русский](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

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
    - [Skipping Pre-commit and Lefthook Hooks](#skipping-pre-commit-and-lefthook-hooks)
  - [Configuration Notes](#configuration-notes)
    - [Advanced Configuration Options](#advanced-configuration-options)
    - [Configuration Subcommands](#configuration-subcommands)
  - [Getting Help](#getting-help)

## Basic Usage

```sh
gac init
# Then follow the prompts to configure your provider, model, and API keys interactively
gac
```

Generates an LLM-powered commit message for staged changes and prompts for confirmation. The confirmation prompt accepts:

- `y` or `yes` - Proceed with the commit
- `n` or `no` - Cancel the commit
- `r` or `reroll` - Regenerate the commit message with the same context
- `e` or `edit` - Edit the commit message in-place with rich terminal editing (vi/emacs keybindings)
- Any other text - Regenerate with that text as feedback (e.g., `make it shorter`, `focus on performance`)
- Empty input (just Enter) - Show the prompt again

---

## Core Workflow Flags

| Flag / Option        | Short | Description                                        |
| -------------------- | ----- | -------------------------------------------------- |
| `--add-all`          | `-a`  | Stage all changes before committing                |
| `--group`            | `-g`  | Group staged changes into multiple logical commits |
| `--push`             | `-p`  | Push changes to remote after committing            |
| `--yes`              | `-y`  | Automatically confirm commit without prompting     |
| `--dry-run`          |       | Show what would happen without making any changes  |
| `--no-verify`        |       | Skip pre-commit and lefthook hooks when committing |
| `--skip-secret-scan` |       | Skip security scan for secrets in staged changes   |

**Note:** Combine `-a` and `-g` (i.e., `-ag`) to stage ALL changes first, then group them into commits.

**Note:** When using `--group`, the max output tokens limit is automatically scaled based on the number of files being committed (2x for 1-9 files, 3x for 10-19 files, 4x for 20-29 files, 5x for 30+ files). This ensures the LLM has enough tokens to generate all grouped commits without truncation, even for large changesets.

## Message Customization

| Flag / Option       | Short | Description                                                               |
| ------------------- | ----- | ------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Generate a single-line commit message                                     |
| `--verbose`         | `-v`  | Generate detailed commit messages with motivation, architecture, & impact |
| `--hint <text>`     | `-h`  | Add a hint to guide the LLM                                               |
| `--model <model>`   | `-m`  | Specify the model to use for this commit                                  |
| `--language <lang>` | `-l`  | Override the language (name or code: 'Spanish', 'es', 'zh-CN', 'ja')      |
| `--scope`           | `-s`  | Infer an appropriate scope for the commit                                 |

**Note:** You can provide feedback interactively by simply typing it at the confirmation prompt - no need to prefix with 'r'. Type `r` for a simple reroll, `e` to edit in-place with vi/emacs keybindings, or type your feedback directly like `make it shorter`.

## Output and Verbosity

| Flag / Option         | Short | Description                                             |
| --------------------- | ----- | ------------------------------------------------------- |
| `--quiet`             | `-q`  | Suppress all output except errors                       |
| `--log-level <level>` |       | Set log level (debug, info, warning, error)             |
| `--show-prompt`       |       | Print the LLM prompt used for commit message generation |

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

- **Generate a detailed commit message with structured sections:**

  ```sh
  gac -v
  ```

- **Add a hint for the LLM:**

  ```sh
  gac -h "Refactor authentication logic"
  ```

- **Infer scope for the commit:**

  ```sh
  gac -s
  ```

- **Group staged changes into logical commits:**

  ```sh
  gac -g
  # Groups only the files you've already staged
  ```

- **Group all changes (staged + unstaged) and auto-confirm:**

  ```sh
  gac -agy
  # Stages everything, groups it, and auto-confirms
  ```

- **Use a specific model just for this commit:**

  ```sh
  gac -m anthropic:claude-3-5-haiku-latest
  ```

- **Generate commit message in a specific language:**

  ```sh
  # Using language codes (shorter)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Using full names
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Dry run (see what would happen):**

  ```sh
  gac --dry-run
  ```

## Advanced

- Combine flags for more powerful workflows (e.g., `gac -ayp` to stage, auto-confirm, and push)
- Use `--show-prompt` to debug or review the prompt sent to the LLM
- Adjust verbosity with `--log-level` or `--quiet`

### Skipping Pre-commit and Lefthook Hooks

The `--no-verify` flag allows you to skip any pre-commit or lefthook hooks configured in your project:

```sh
gac --no-verify  # Skip all pre-commit and lefthook hooks
```

**Use `--no-verify` when:**

- Pre-commit or lefthook hooks are failing temporarily
- Working with time-consuming hooks
- Committing work-in-progress code that doesn't pass all checks yet

**Note:** Use with caution as these hooks maintain code quality standards.

### Security Scanning

gac includes built-in security scanning that automatically detects potential secrets and API keys in your staged changes before committing. This helps prevent accidentally committing sensitive information.

**Skipping security scans:**

```sh
gac --skip-secret-scan  # Skip security scan for this commit
```

**To disable permanently:** Set `GAC_SKIP_SECRET_SCAN=true` in your `.gac.env` file.

**When to skip:**

- Committing example code with placeholder keys
- Working with test fixtures that contain dummy credentials
- When you've verified the changes are safe

**Note:** The scanner uses pattern matching to detect common secret formats. Always review your staged changes before committing.

## Configuration Notes

- The recommended way to set up gac is to run `gac init` and follow the interactive prompts.
- Already configured language and just need to switch providers or models? Run `gac model` to repeat the setup without language questions.
- gac loads configuration in the following order of precedence:
  1. CLI flags
  2. Environment variables
  3. Project-level `.gac.env`
  4. User-level `~/.gac.env`

### Advanced Configuration Options

You can customize gac's behavior with these optional environment variables:

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Automatically infer and include scope in commit messages (e.g., `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Generate detailed commit messages with motivation, architecture, and impact sections
- `GAC_TEMPERATURE=0.7` - Control LLM creativity (0.0-1.0, lower = more focused)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Maximum tokens for generated messages (automatically scaled 2-5x when using `--group` based on file count; override to go higher or lower)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Warn when prompts exceed this token count
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Use a custom system prompt for commit message generation
- `GAC_LANGUAGE=Spanish` - Generate commit messages in a specific language (e.g., Spanish, French, Japanese, German). Supports full names or ISO codes (es, fr, ja, de, zh-CN). Use `gac language` for interactive selection
- `GAC_TRANSLATE_PREFIXES=true` - Translate conventional commit prefixes (feat, fix, etc.) into the target language (default: false, keeps prefixes in English)
- `GAC_SKIP_SECRET_SCAN=true` - Disable automatic security scanning for secrets in staged changes (use with caution)

See `.gac.env.example` for a complete configuration template.

For detailed guidance on creating custom system prompts, see [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md).

### Configuration Subcommands

The following subcommands are available:

- `gac init` — Interactive setup wizard for provider, model, and language configuration
- `gac model` — Provider/model/API key setup without language prompts (ideal for quick switches)
- `gac config show` — Show current configuration
- `gac config set KEY VALUE` — Set a config key in `$HOME/.gac.env`
- `gac config get KEY` — Get a config value
- `gac config unset KEY` — Remove a config key from `$HOME/.gac.env`
- `gac language` (or `gac lang`) — Interactive language selector for commit messages (sets GAC_LANGUAGE)
- `gac diff` — Show filtered git diff with options for staged/unstaged changes, color, and truncation

## Getting Help

- For custom system prompts, see [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/CUSTOM_SYSTEM_PROMPTS.md)
- For troubleshooting and advanced tips, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- For installation and configuration, see [README.md#installation-and-configuration](README.md#installation-and-configuration)
- To contribute, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- License information: [LICENSE](LICENSE)
