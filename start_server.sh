#!/bin/bash
# Start NetData MCP Server

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src"

echo "Starting NetData MCP Server..."
python src/main.py
