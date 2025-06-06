# Troubleshooting gac

This guide covers common issues and solutions for installing, configuring, and running gac.

## Table of Contents

- [Troubleshooting gac](#troubleshooting-gac)
  - [Table of Contents](#table-of-contents)
  - [1. Installation Problems](#1-installation-problems)
  - [2. Configuration Issues](#2-configuration-issues)
  - [3. Provider/API Errors](#3-providerapi-errors)
  - [4. Pre-commit Hook Issues](#4-pre-commit-hook-issues)
  - [5. General Debugging](#5-general-debugging)
  - [Still Stuck?](#still-stuck)
  - [Where to Get Further Help](#where-to-get-further-help)

## 1. Installation Problems

**Problem:** `gac` command not found after install

- Ensure you installed with `pipx` or in a directory on your `$PATH`
- If you used `pipx`, run `pipx ensurepath` and restart your terminal
- Verify installation with `pipx list`

**Problem:** Permission denied or cannot write files

- Check directory permissions
- Try running with appropriate privileges or change directory ownership

## 2. Configuration Issues

**Problem:** gac can't find your API key or model

- If you are new, run `gac init` to interactively set up your provider, model, and API keys
- Make sure your `.gac.env` or environment variables are set correctly
- Run `gac --verbose` to see which config files are loaded
- Check for typos in variable names (e.g., `GAC_GROQ_API_KEY`)

**Problem:** User-level `$HOME/.gac.env` changes are not picked up

- Make sure you are editing the correct file for your OS:
  - On macOS/Linux: `$HOME/.gac.env` (usually `/Users/<your-username>/.gac.env` or `/home/<your-username>/.gac.env`)
  - On Windows: `$HOME/.gac.env` (typically `C:\Users\<your-username>\.gac.env` or use `%USERPROFILE%`)
- Run `gac --verbose` to confirm the user-level config is loaded
- Restart your terminal or re-run your shell to reload environment variables
- If still not working, check for typos and file permissions

**Problem:** Project-level `.gac.env` changes are not picked up

- Ensure your project contains a `.gac.env` file in the root directory (next to your `.git` folder)
- Run `gac --verbose` to confirm the project-level config is loaded
- If you edit `.gac.env`, restart your terminal or re-run your shell to reload environment variables
- If still not working, check for typos and file permissions

## 3. Provider/API Errors

**Problem:** Authentication or API errors

- Ensure you have set the correct API keys for your chosen model (e.g., `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Double-check your API key and provider account status
- Ensure your key has sufficient quota and is not expired
- Check for provider outages

**Problem:** Model not available or unsupported

- Verify the model name is correct and supported by your provider
- Check provider documentation for available models

## 4. Pre-commit Hook Issues

**Problem:** Pre-commit hooks are failing and blocking commits

- Use `gac --no-verify` to skip all pre-commit hooks temporarily
- Fix the underlying issues causing the hooks to fail
- Consider adjusting your pre-commit configuration if hooks are too strict

**Problem:** Pre-commit hooks take too long or are interfering with workflow

- Use `gac --no-verify` to skip all pre-commit hooks temporarily
- Consider configuring pre-commit hooks to be less aggressive for your workflow
- Review your `.pre-commit-config.yaml` to optimize hook performance

## 5. General Debugging

- Use `gac init` to reset or update your configuration interactively
- Use `gac --verbose` (increases output verbosity) or `gac --log-level=DEBUG` for more details
- Check logs for error messages and stack traces
- Review the [INSTALLATION.md](INSTALLATION.md) for setup steps
- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- See [USAGE.md](USAGE.md) for help with command-line flags and advanced usage

## Still Stuck?

- Search existing issues or open a new one on the [GitHub repository](https://github.com/criteria-dev/gac)
- Include details about your OS, Python version, gac version, provider, and error output
- The more detail you provide, the faster your issue can be resolved

## Where to Get Further Help

- For contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)
- For license information, see [LICENSE](LICENSE)
- For installation and usage, see [INSTALLATION.md](INSTALLATION.md) and [USAGE.md](USAGE.md)
