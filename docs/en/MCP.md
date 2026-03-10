# Using GAC as an MCP Server

**English** | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | [Français](../fr/MCP.md) | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC can run as a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server, allowing AI agents and editors to generate commits through structured tool calls instead of shell commands.

## Table of Contents

- [Using GAC as an MCP Server](#using-gac-as-an-mcp-server)
  - [Table of Contents](#table-of-contents)
  - [What is MCP?](#what-is-mcp)
  - [Benefits](#benefits)
  - [Setup](#setup)
    - [Claude Code](#claude-code)
    - [Claude Desktop](#claude-desktop)
    - [Cursor](#cursor)
    - [Other MCP Clients](#other-mcp-clients)
  - [Available Tools](#available-tools)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Workflows](#workflows)
    - [Basic Commit](#basic-commit)
    - [Preview Before Committing](#preview-before-committing)
    - [Grouped Commits](#grouped-commits)
    - [Commit with Context](#commit-with-context)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)
  - [See Also](#see-also)

## What is MCP?

The Model Context Protocol is an open standard that lets AI applications call external tools through a structured interface. By running GAC as an MCP server, any MCP-compatible client can inspect repository state and create AI-powered commits without invoking shell commands directly.

## Benefits

- **Structured interaction**: Agents call typed tools with validated parameters instead of parsing shell output
- **Two-tool workflow**: `gac_status` to inspect, `gac_commit` to act — a natural fit for agent reasoning
- **Full GAC capabilities**: AI commit messages, grouped commits, secret scanning, and push — all available through MCP
- **Zero configuration**: The server uses your existing GAC configuration (`~/.gac.env`, provider settings, etc.)

## Setup

The MCP server is started with `gac serve` and communicates over stdio, the standard MCP transport.

### Claude Code

Add to your project's `.mcp.json` or global `~/.claude/claude_code_config.json`:

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

Or if you have GAC installed globally:

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Other MCP Clients

Any MCP-compatible client can use GAC. The server entry point is:

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

If you have GAC installed (via `uv tool install gac`), you can use `gac` directly instead of `uvx gac`.

## Available Tools

The server exposes two tools:

### gac_status

Inspect the repository state. Use this before committing to understand what will be committed.

**Parameters:**

| Parameter           | Type                                    | Default     | Description                          |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------ |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Output format                        |
| `include_diff`      | bool                                    | `false`     | Include full diff content            |
| `include_stats`     | bool                                    | `true`      | Include line change statistics       |
| `include_history`   | int                                     | `0`         | Number of recent commits to include  |
| `staged_only`       | bool                                    | `false`     | Only show staged changes             |
| `include_untracked` | bool                                    | `true`      | Include untracked files              |
| `max_diff_lines`    | int                                     | `500`       | Cap diff output size (0 = unlimited) |

**Returns:** Branch name, file status (staged/unstaged/untracked/conflicts), optional diff content, optional statistics, and optional commit history.

### gac_commit

Generate an AI-powered commit message and optionally execute the commit.

**Parameters:**

| Parameter          | Type           | Default | Description                                               |
| ------------------ | -------------- | ------- | --------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Stage all changes before committing (`git add -A`)        |
| `files`            | list[str]      | `[]`    | Specific files to stage                                   |
| `dry_run`          | bool           | `false` | Preview without executing                                 |
| `message_only`     | bool           | `false` | Generate message without committing                       |
| `push`             | bool           | `false` | Push to remote after commit                               |
| `group`            | bool           | `false` | Split changes into multiple logical commits               |
| `one_liner`        | bool           | `false` | Single-line commit message                                |
| `scope`            | string \| null | `null`  | Conventional commit scope (auto-detected if not provided) |
| `hint`             | string         | `""`    | Additional context for better messages                    |
| `model`            | string \| null | `null`  | Override AI model (`provider:model_name`)                 |
| `language`         | string \| null | `null`  | Override commit message language                          |
| `skip_secret_scan` | bool           | `false` | Skip security scan                                        |
| `no_verify`        | bool           | `false` | Skip pre-commit hooks                                     |
| `auto_confirm`     | bool           | `false` | Skip confirmation prompts (required for agents)           |

**Returns:** Success status, generated commit message, commit hash (if committed), list of changed files, and any warnings.

## Workflows

### Basic Commit

```text
1. gac_status()                              → See what's changed
2. gac_commit(stage_all=true, auto_confirm=true)  → Stage, generate message, and commit
```

### Preview Before Committing

```text
1. gac_status(include_diff=true, include_stats=true)  → Review changes in detail
2. gac_commit(stage_all=true, dry_run=true)            → Preview the commit message
3. gac_commit(stage_all=true, auto_confirm=true)       → Execute the commit
```

### Grouped Commits

```text
1. gac_status()                                           → See all changes
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Preview logical groupings
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Execute grouped commits
```

### Commit with Context

```text
1. gac_status(include_history=5)  → See recent commits for style reference
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configuration

The MCP server uses your existing GAC configuration. No additional setup is needed beyond:

1. **Provider and model**: Run `gac init` or `gac model` to configure your AI provider
2. **API keys**: Stored in `~/.gac.env` (set up during `gac init`)
3. **Optional settings**: All GAC environment variables apply (`GAC_LANGUAGE`, `GAC_VERBOSE`, etc.)

See the [main documentation](USAGE.md#configuration-notes) for all configuration options.

## Troubleshooting

### "No model configured"

Run `gac init` to set up your AI provider and model before using the MCP server.

### "No staged changes found"

Either stage files manually (`git add`) or use `stage_all=true` in the `gac_commit` call.

### Server not starting

Verify GAC is installed and accessible:

```bash
uvx gac --version
# or
gac --version
```

If using `uvx`, ensure `uv` is installed and on your PATH.

### Agent can't find the server

Make sure the MCP configuration file is in the correct location for your client and that the `command` path is accessible from your shell environment.

### Rich output corruption

The MCP server automatically redirects all Rich console output to stderr to prevent stdio protocol corruption. If you see garbled output, ensure you're running `gac serve` (not `gac` directly) when using MCP.

## See Also

- [Main Documentation](USAGE.md)
- [Claude Code OAuth Setup](CLAUDE_CODE.md)
- [Qwen.ai OAuth Setup](QWEN.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [MCP Specification](https://modelcontextprotocol.io/)
