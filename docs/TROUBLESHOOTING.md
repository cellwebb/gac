# Troubleshooting gac

**English** | [简体中文](TROUBLESHOOTING.zh-CN.md) | [繁體中文](TROUBLESHOOTING.zh-TW.md) | [日本語](TROUBLESHOOTING.ja.md) | [Français](TROUBLESHOOTING.fr.md) | [Русский](TROUBLESHOOTING.ru.md) | [Español](TROUBLESHOOTING.es.md) | [Português](TROUBLESHOOTING.pt.md) | [हिन्दी](TROUBLESHOOTING.hi.md)

This guide covers common issues and solutions for installing, configuring, and running gac.

## Table of Contents

- [Troubleshooting gac](#troubleshooting-gac)
  - [Table of Contents](#table-of-contents)
  - [1. Installation Problems](#1-installation-problems)
  - [2. Configuration Issues](#2-configuration-issues)
  - [3. Provider/API Errors](#3-providerapi-errors)
  - [4. Commit Grouping Issues](#4-commit-grouping-issues)
  - [5. Security and Secret Detection](#5-security-and-secret-detection)
  - [6. Pre-commit and Lefthook Hook Issues](#6-pre-commit-and-lefthook-hook-issues)
  - [7. Common Workflow Issues](#7-common-workflow-issues)
  - [8. General Debugging](#8-general-debugging)
  - [Still Stuck?](#still-stuck)
  - [Where to Get Further Help](#where-to-get-further-help)

## 1. Installation Problems

**Problem:** `gac` command not found after install

- Ensure you installed with `uv tool install gac` or `uvx gac`
- If you used `uv tool install`, verify installation with `uv tool list`
- Make sure `uv` is installed and in your `$PATH`
- Restart your terminal after installation

**Problem:** Permission denied or cannot write files

- Check directory permissions
- Try running with appropriate privileges or change directory ownership

## 2. Configuration Issues

**Problem:** gac can't find your API key or model

- If you are new, run `gac init` to interactively set up your provider, model, and API keys
- Make sure your `.gac.env` or environment variables are set correctly
- Run `gac --log-level=debug` to see which config files are loaded and debug configuration issues
- Check for typos in variable names (e.g., `GAC_GROQ_API_KEY`)

**Problem:** User-level `$HOME/.gac.env` changes are not picked up

- Make sure you are editing the correct file for your OS:
  - On macOS/Linux: `$HOME/.gac.env` (usually `/Users/<your-username>/.gac.env` or `/home/<your-username>/.gac.env`)
  - On Windows: `$HOME/.gac.env` (typically `C:\Users\<your-username>\.gac.env` or use `%USERPROFILE%`)
- Run `gac --log-level=debug` to confirm the user-level config is loaded
- Restart your terminal or re-run your shell to reload environment variables
- If still not working, check for typos and file permissions

**Problem:** Project-level `.gac.env` changes are not picked up

- Ensure your project contains a `.gac.env` file in the root directory (next to your `.git` folder)
- Run `gac --log-level=debug` to confirm the project-level config is loaded
- If you edit `.gac.env`, restart your terminal or re-run your shell to reload environment variables
- If still not working, check for typos and file permissions

**Problem:** Cannot set or change language for commit messages

- Run `gac language` (or `gac lang`) to interactively select from 25+ supported languages
- Use `-l <language>` flag to override language for a single commit (e.g., `gac -l zh-CN`, `gac -l Spanish`)
- Check your config with `gac config show` to see current language setting
- Language setting is stored in `GAC_LANGUAGE` in your `.gac.env` file

## 3. Provider/API Errors

**Problem:** Authentication or API errors

- Ensure you have set the correct API keys for your chosen model (e.g., `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Double-check your API key and provider account status
- For Ollama and LM Studio, confirm the API URL matches your local instance. API keys are only needed if you enabled authentication.

**Problem:** Model not available or unsupported

- Streamlake uses inference endpoint IDs instead of model names. Make sure you supply the endpoint ID from their console.
- Verify the model name is correct and supported by your provider
- Check provider documentation for available models

## 4. Commit Grouping Issues

**Problem:** `--group` flag not working as expected

- The `--group` flag automatically analyzes staged changes and can create multiple logical commits
- The LLM may decide that a single commit makes sense for your set of staged changes, even with `--group`
- This is intentional behavior - the LLM groups changes based on logical relationships, not just quantity
- Ensure you have multiple unrelated changes staged (e.g., bug fix + feature addition) for best results
- Use `gac --show-prompt` to debug what the LLM is seeing

**Problem:** Commits grouped incorrectly or not grouped when expected

- The grouping is determined by the LLM's analysis of your changes
- The LLM may create a single commit if it determines the changes are logically related
- Try adding hints with `-h "hint"` to guide the grouping logic (e.g., `-h "separate bug fix from refactoring"`)
- Review the generated groups before confirming
- If grouping doesn't work well for your use case, commit changes separately instead

## 5. Security and Secret Detection

**Problem:** False positive: secret scan detects non-secrets

- The security scanner looks for patterns that resemble API keys, tokens, and passwords
- If you're committing example code, test fixtures, or documentation with placeholder keys, you may see false positives
- Use `--skip-secret-scan` to bypass the scan if you're certain the changes are safe
- Consider excluding test/example files from commits, or use clearly marked placeholders

**Problem:** Secret scan not detecting actual secrets

- The scanner uses pattern matching and may not catch all secret types
- Always review your staged changes with `git diff --staged` before committing
- Consider using additional security tools like `git-secrets` or `gitleaks` for comprehensive protection
- Report any missed patterns as issues to help improve detection

**Problem:** Need to disable secret scanning permanently

- Set `GAC_SKIP_SECRET_SCAN=true` in your `.gac.env` file
- Use `gac config set GAC_SKIP_SECRET_SCAN true`
- Note: Only disable if you have other security measures in place

## 6. Pre-commit and Lefthook Hook Issues

**Problem:** Pre-commit or lefthook hooks are failing and blocking commits

- Use `gac --no-verify` to skip all pre-commit and lefthook hooks temporarily
- Fix the underlying issues causing the hooks to fail
- Consider adjusting your pre-commit or lefthook configuration if hooks are too strict

**Problem:** Pre-commit or lefthook hooks take too long or are interfering with workflow

- Use `gac --no-verify` to skip all pre-commit and lefthook hooks temporarily
- Consider configuring pre-commit hooks in `.pre-commit-config.yaml` or lefthook hooks in `.lefthook.yml` to be less aggressive for your workflow
- Review your hook configuration to optimize performance

## 7. Common Workflow Issues

**Problem:** No changes to commit / nothing staged

- gac requires staged changes to generate a commit message
- Use `git add <files>` to stage changes, or use `gac -a` to stage all changes automatically
- Check `git status` to see what files have been modified
- Use `gac diff` to see a filtered view of your changes

**Problem:** Commit message not what I expected

- Use the interactive feedback system: type `r` to reroll, `e` to edit, or provide natural language feedback
- Add context with `-h "your hint"` to guide the LLM
- Use `-o` for simpler one-line messages or `-v` for more detailed messages
- Use `--show-prompt` to see what information the LLM is receiving

**Problem:** gac is too slow

- Use `gac -y` to skip the confirmation prompt
- Use `gac -q` for quiet mode with less output
- Consider using faster/cheaper models for routine commits
- Use `gac --no-verify` to skip hooks if they're slowing you down

**Problem:** Can't edit or provide feedback after message generation

- At the prompt, type `e` to enter edit mode (supports vi/emacs keybindings)
- Type `r` to regenerate without feedback
- Or simply type your feedback directly (e.g., "make it shorter", "focus on the bug fix")
- Press Enter on empty input to see the prompt again

## 8. General Debugging

- Use `gac init` to reset or update your configuration interactively
- Use `gac --log-level=debug` for detailed debug output and logging
- Use `gac --show-prompt` to see what prompt is being sent to the LLM
- Use `gac --help` to see all available command-line flags
- Use `gac config show` to see all current configuration values
- Check logs for error messages and stack traces
- Check the main [README.md](../README.md) for features, examples, and quick start instructions

## Still Stuck?

- Search existing issues or open a new one on the [GitHub repository](https://github.com/cellwebb/gac)
- Include details about your OS, Python version, gac version, provider, and error output
- The more detail you provide, the faster your issue can be resolved

## Where to Get Further Help

- For features and usage examples, see the main [README.md](../README.md)
- For custom system prompts, see [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- For contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For license information, see [../LICENSE](../LICENSE)
