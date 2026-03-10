"""MCP (Model Context Protocol) support for GAC.

This module exposes GAC's commit generation capabilities to AI agents
through the Model Context Protocol using FastMCP.

Available Tools:
    - gac_commit: Generate and execute git commits
    - gac_status: Get repository status and diff information
"""

from gac.mcp.models import CommitRequest, CommitResult, StatusRequest, StatusResult
from gac.mcp.server import main, mcp

__all__ = [
    "CommitRequest",
    "CommitResult",
    "StatusRequest",
    "StatusResult",
    "mcp",
    "main",
]
