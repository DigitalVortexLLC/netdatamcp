#!/usr/bin/env python3
"""Main entry point for NetData MCP server."""
import sys
from netdatamcp.server import mcp


if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
