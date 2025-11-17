# GAC MCP Server

GAC (Git Auto Commit) now provides an MCP (Model Context Protocol) server that allows AI coding agents to generate commit messages, stage files, commit changes, and push to remotes.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for connecting AI systems with external tools and data sources. It allows AI agents like Claude Desktop, Cline, and other MCP clients to interact with your development tools in a secure, standardized way.

## Installation

First, install gac with MCP support:

```bash
pip install gac
```

Or if you're developing from source:

```bash
pip install -e .
```

The MCP SDK dependency (`mcp>=1.0.0`) is automatically installed with gac.

## Configuration

### Claude Desktop

To use gac as an MCP server with Claude Desktop, add the following to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac-mcp",
      "args": []
    }
  }
}
```

If you installed gac in a virtual environment, use the full path to the executable:

```json
{
  "mcpServers": {
    "gac": {
      "command": "/path/to/venv/bin/gac-mcp",
      "args": []
    }
  }
}
```

### Other MCP Clients

For other MCP clients (Cline, Zed, etc.), refer to their documentation on how to configure MCP servers. Generally, you'll need to specify:

- **Command**: `gac-mcp` (or the full path to the executable)
- **Transport**: stdio (standard input/output)

## Available Tools

The gac MCP server exposes the following tools:

### Core Workflow Tools

#### `generate_commit_message`

Generate a commit message for currently staged changes.

**Parameters:**
- `hint` (optional): Context to guide message generation
- `one_liner` (optional): Generate a one-line message
- `verbose` (optional): Generate a detailed multi-paragraph message
- `model` (optional): Model to use (format: `provider:model`)
- `language` (optional): Language for the message (e.g., 'en', 'es', 'fr')
- `infer_scope` (optional): Automatically infer conventional commit scope

**Returns:**
```json
{
  "success": true,
  "message": "feat: add user authentication system",
  "staged_files": ["src/auth.py", "tests/test_auth.py"],
  "model_used": "anthropic:claude-haiku-4-5"
}
```

#### `generate_and_commit`

Generate a commit message and commit in one step.

**Parameters:**
- Same as `generate_commit_message`, plus:
- `no_verify` (optional): Skip pre-commit hooks
- `auto_push` (optional): Automatically push after committing

**Returns:**
```json
{
  "success": true,
  "message": "feat: add user authentication system",
  "commit_hash": "a1b2c3d4",
  "model_used": "anthropic:claude-haiku-4-5",
  "pushed": true,
  "branch": "main"
}
```

### Git Operations

#### `stage_files`

Stage specific files for commit.

**Parameters:**
- `file_paths`: List of file paths to stage

**Returns:**
```json
{
  "success": true,
  "staged_files": ["src/auth.py", "tests/test_auth.py"],
  "message": "Staged 2 file(s)"
}
```

#### `stage_all_changes`

Stage all changes in the repository.

**Returns:**
```json
{
  "success": true,
  "staged_files": ["src/auth.py", "src/utils.py", "tests/test_auth.py"],
  "message": "Staged all changes (3 file(s))"
}
```

#### `unstage_files`

Unstage specific files.

**Parameters:**
- `file_paths`: List of file paths to unstage

#### `commit_changes`

Commit staged changes with a message.

**Parameters:**
- `message`: The commit message
- `no_verify` (optional): Skip pre-commit hooks

**Returns:**
```json
{
  "success": true,
  "commit_hash": "a1b2c3d4",
  "message": "Changes committed successfully"
}
```

#### `push_to_remote`

Push commits to the remote repository.

**Returns:**
```json
{
  "success": true,
  "branch": "main",
  "message": "Successfully pushed to remote branch 'main'"
}
```

### Inspection Tools

#### `get_git_status`

Get the status of staged and unstaged files.

**Returns:**
```json
{
  "success": true,
  "staged_status": "M  src/auth.py\nA  tests/test_auth.py",
  "staged_files": ["src/auth.py", "tests/test_auth.py"],
  "branch": "main",
  "repo_root": "/path/to/repo"
}
```

#### `get_staged_diff_content`

Get the diff of staged changes.

**Parameters:**
- `color` (optional): Include ANSI color codes

**Returns:**
```json
{
  "success": true,
  "diff": "diff --git a/src/auth.py...",
  "staged_files": ["src/auth.py"]
}
```

#### `scan_staged_for_secrets`

Scan staged changes for potential secrets (API keys, passwords, etc.).

**Returns:**
```json
{
  "success": true,
  "secrets_found": true,
  "secrets": [
    {
      "type": "API Key",
      "file": "config.py",
      "line": 42,
      "matched_text": "api_key = 'sk-...'"
    }
  ],
  "message": "Scan complete. Found 1 potential secret(s)."
}
```

## Available Resources

Resources provide read-only access to git state:

### `git://status`

Get current git status as JSON.

### `git://diff/staged`

Get the staged diff content.

### `git://branch`

Get the current branch name.

## Usage Examples

### With Claude Desktop

Once configured, you can ask Claude to help with git operations:

> "Can you stage all the Python files I changed and generate a commit message?"

Claude will use the MCP tools to:
1. List changed Python files
2. Stage them with `stage_files`
3. Generate a commit message with `generate_commit_message`
4. Show you the message for approval

> "Review my staged changes and commit them with an appropriate message"

Claude will:
1. Get the staged diff with `get_staged_diff_content`
2. Analyze the changes
3. Generate and commit with `generate_and_commit`

> "Check if there are any secrets in my staged changes"

Claude will use `scan_staged_for_secrets` to check for potential security issues.

### Common Workflows

#### Complete Commit Workflow

```
User: "Stage all my changes, check for secrets, and commit with a good message"

AI Agent:
1. Calls stage_all_changes()
2. Calls scan_staged_for_secrets()
3. If no secrets found, calls generate_and_commit()
4. Reports the commit hash and message
```

#### Safe Commit with Review

```
User: "Show me what I'm about to commit and generate a message"

AI Agent:
1. Calls get_staged_diff_content()
2. Shows you the diff
3. Calls generate_commit_message()
4. Shows you the proposed message
5. After your approval, calls commit_changes()
```

## Configuration

The MCP server uses your existing gac configuration from `~/.gac.env` and `.gac.env`. Make sure you've run `gac init` to set up your API keys and preferences:

```bash
gac init
```

This will configure:
- Your preferred AI provider and model
- API keys
- Default language and format preferences
- Token limits and retry settings

## Running the Server Manually

For testing or debugging, you can run the MCP server directly:

```bash
gac-mcp
```

The server communicates via stdio (standard input/output), so it will wait for MCP protocol messages.

## Troubleshooting

### Server Not Starting

1. **Check installation**: Verify gac-mcp is in your PATH:
   ```bash
   which gac-mcp
   ```

2. **Check configuration**: Make sure you've run `gac init`:
   ```bash
   gac init
   ```

3. **Check logs**: Claude Desktop logs are typically in:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### Tools Not Working

1. **Check you're in a git repository**: All tools require a valid git repository.

2. **Check API keys**: Make sure your AI provider API keys are configured:
   ```bash
   gac config list
   ```

3. **Check staged files**: Many tools require staged files. Stage some files first:
   ```bash
   git add <files>
   ```

### Permission Issues

If you get permission errors when pushing:
- Make sure you have push access to the remote repository
- Check that your git credentials are configured correctly
- Try pushing manually first to verify: `git push`

## Security Considerations

- The MCP server has access to your git repository and can stage, commit, and push changes
- It uses your configured API keys to call AI providers
- The `scan_staged_for_secrets` tool helps prevent accidental secret commits
- Consider using `no_verify=false` (the default) to ensure pre-commit hooks run

## Development

To modify the MCP server, edit `/src/gac/mcp_server.py`. The server uses the FastMCP framework from the official MCP Python SDK.

### Adding New Tools

```python
@mcp.tool()
def my_new_tool(param: str) -> dict[str, Any]:
    """Tool description for AI agents.

    Args:
        param: Parameter description

    Returns:
        Dictionary with success status and results
    """
    # Implementation
    return {"success": True, "result": "..."}
```

### Adding New Resources

```python
@mcp.resource("git://my-resource")
def my_resource() -> str:
    """Resource description."""
    return "resource content"
```

## Learn More

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/model-context-protocol)
- [GAC Documentation](https://github.com/cellwebb/gac)

## Support

If you encounter issues with the MCP server:

1. Check the [troubleshooting section](#troubleshooting) above
2. Open an issue on [GitHub](https://github.com/cellwebb/gac/issues)
3. Include:
   - Your gac version: `pip show gac`
   - Your MCP client (Claude Desktop, Cline, etc.)
   - Error messages from logs
   - Steps to reproduce the issue
