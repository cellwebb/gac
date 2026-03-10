#!/bin/bash
# GAC MCP Server wrapper script
cd /home/swarm/Clover/gac
exec uv run gac-mcp "$@"
