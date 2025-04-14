# Troubleshooting GAC

This guide covers common issues and solutions for installing, configuring, and running GAC.

## 1. Installation Problems

**Problem:** `gac` command not found after install

- Ensure you installed with `pipx` or in a directory on your `$PATH`
- If you used `pipx`, run `pipx ensurepath` and restart your terminal
- Verify installation with `pipx list`

**Problem:** Permission denied or cannot write files

- Check directory permissions
- Try running with appropriate privileges or change directory ownership

## 2. Configuration Issues

**Problem:** GAC can't find your API key or model

- Make sure your `.gac.env` or environment variables are set correctly
- Run `gac --verbose` to see which config files are loaded
- Check for typos in variable names (e.g., `GROQ_API_KEY`)

**Problem:** Changes to `.gac.env` are not picked up

- Restart your terminal or source the file if you set variables in your shell
- Ensure the file is in your project directory or home directory

## 3. Provider/API Errors

**Problem:** Authentication or API errors

- Double-check your API key and provider account status
- Ensure your key has sufficient quota and is not expired
- Check for provider outages

**Problem:** Model not available or unsupported

- Verify the model name is correct and supported by your provider
- Check provider documentation for available models

## 4. General Debugging

- Use `gac --verbose` or `gac --log-level=DEBUG` for more details
- Check logs for error messages and stack traces
- Review the [INSTALLATION.md](INSTALLATION.md) for setup steps
- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Still Stuck?

- Search existing issues or open a new one on the [GitHub repository](https://github.com/cellwebb/gac)
- Include details about your OS, Python version, and error output
