# GAC (Git Auto Commit)

AI-assisted git commit message generator.

## Features

- Generates clear, context-aware commit messages using AI
- Enriches commit messages with repository structure and recent history
- Simple CLI workflow, drop-in replacement for `git commit`

## Quick Start

1. **Install**

   See [INSTALLATION.md](INSTALLATION.md) for up-to-date installation instructions.

2. **Configure**

   Create a `.gac.env` file in your project or home directory:

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

   See [USAGE.md](USAGE.md) for a full list of CLI flags and advanced usage.

## How It Works

GAC analyzes your staged changes, repository structure, and recent commit history to generate high-quality commit
messages with the help of leading AI models.

## Best Practices

- Use project-level `.gac.env` for project-specific configuration
- Use user-level `~/.gac.env` for personal defaults
- Keep API keys out of version control
- For troubleshooting and advanced tips, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
