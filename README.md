# gac (Git Auto Commit)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue.svg)](https://www.python.org/downloads/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)

## Features

- Generates clear, context-aware commit messages using AI
- Enriches commit messages with repository structure and recent history
- Simple CLI workflow, drop-in replacement for `git commit`

## Quick Start

1. **Install**

   See [INSTALLATION.md](INSTALLATION.md) for up-to-date installation instructions. Windows users: see also the Windows
   setup section in [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md).

2. **Configure**

   Create a `.gac.env` file in your project or $HOME directory (~ on Mac/Linux):

   ```sh
   GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
   GROQ_API_KEY=your_key_here
   ```

   Or set as environment variables:

   ```sh
   export GAC_MODEL=groq:meta-llama/llama-4-scout-17b-16e-instruct
   export GROQ_API_KEY=your_key_here
   ```

   For more configuration options, see [INSTALLATION.md](INSTALLATION.md).

3. **Use**

   ```sh
   git add .
   gac
   ```

   - Generate a one-line commit message: `gac -o`
   - Add a hint for the AI: `gac -h "Fix the authentication bug"`
   - Advanced Usage: Add all, auto-confirm commit and push a one-liner with a hint: `gac -aypo -h "update for release"`

   See [USAGE.md](USAGE.md) for a full list of CLI flags and advanced usage.

## How It Works

GAC analyzes your staged changes, repository structure, and recent commit history to generate high-quality commit
messages with the help of leading AI models.

## Best Practices

- Use project-level `.gac.env` for project-specific configuration
- Use user-level `~/.gac.env` for personal defaults
- Keep API keys out of version control
- For troubleshooting and advanced tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For Windows setup, see [docs/WINDOWS_COMPATIBILITY_PLAN.md](docs/WINDOWS_COMPATIBILITY_PLAN.md)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Community & Support

For questions, suggestions, or support, please open an issue or discussion on GitHub.
