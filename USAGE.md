# FastMCP Usage Guide for NetData MCP

This guide explains how to use the NetData MCP server with FastMCP.

## What is FastMCP?

FastMCP is a Python framework for building Model Context Protocol (MCP) servers. It provides a simple way to create tools and resources that can be accessed by AI assistants and other MCP clients.

## Server Architecture

The NetData MCP server uses FastMCP to expose tools for querying YANG and SNMP MIB data. The server runs as a process that communicates using the MCP protocol over stdio or HTTP.

## Running the Server

### Standard MCP Mode (stdio)

The default way to run the server is in stdio mode, which is the standard MCP protocol:

```bash
cd /home/runner/work/netdatamcp/netdatamcp
PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python src/main.py
```

This starts the FastMCP server in stdio mode, where it communicates via standard input/output.

### Development Mode

For development and testing, you can use FastMCP's built-in HTTP server:

```bash
cd /home/runner/work/netdatamcp/netdatamcp
PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python -m fastmcp dev src/netdatamcp/server.py:mcp
```

This will start a development server with a web UI at http://localhost:8000.

## Available MCP Tools

The server exposes the following tools:

### 1. query_data

Query parsed YANG/SNMP data from the database.

**Parameters:**
- `type` (optional, string): Filter by type ("yang" or "snmp")
- `name` (optional, string): Search by name (supports partial matching)
- `version` (optional, string): Filter by specific version

**Example usage in an MCP client:**
```python
result = client.call_tool("query_data", {
    "type": "yang",
    "name": "ietf-interfaces"
})
```

### 2. list_all_data

List all parsed data entries in the database.

**Parameters:** None

**Example usage:**
```python
result = client.call_tool("list_all_data", {})
```

### 3. get_versions

Get all available versions for a specific module/MIB name.

**Parameters:**
- `name` (required, string): Name of the module/MIB

**Example usage:**
```python
result = client.call_tool("get_versions", {
    "name": "ietf-interfaces"
})
```

### 4. get_statistics

Get database statistics including counts of YANG and SNMP entries.

**Parameters:** None

**Example usage:**
```python
result = client.call_tool("get_statistics", {})
```

## Available MCP Resources

The server also exposes resources:

### 1. db://all

Get all database data as a resource.

**Example usage:**
```python
result = client.read_resource("db://all")
```

### 2. db://stats

Get database statistics as a resource.

**Example usage:**
```python
result = client.read_resource("db://stats")
```

## Processing Files

To process YANG and SNMP MIB files, use the processor:

```bash
cd /home/runner/work/netdatamcp/netdatamcp
PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python -m netdatamcp.processor
```

This will:
1. Scan the `yang/` directory for `.yang` files
2. Scan the `mibs/` directory for `.mib` and `.txt` files
3. Parse each file and extract metadata
4. Store the parsed data in the SQLite database with version information

## Configuration

The server can be configured using environment variables:

- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: 3000)

Example:
```bash
HOST=0.0.0.0 PORT=8080 PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python src/main.py
```

## Integration with AI Assistants

To use this server with an AI assistant like Claude or GPT-4:

1. Start the server in stdio mode
2. Configure your AI assistant to connect to the MCP server
3. The assistant can now query network data using natural language, which gets translated into tool calls

Example conversation:
- User: "Show me all YANG modules"
- Assistant calls: `query_data(type="yang")`
- User: "What versions of ietf-interfaces are available?"
- Assistant calls: `get_versions(name="ietf-interfaces")`

## Troubleshooting

### Module not found error

If you get a "ModuleNotFoundError: No module named 'netdatamcp'", make sure to set the PYTHONPATH:

```bash
export PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src
```

### Database locked error

If you get a database locked error, make sure only one instance of the server or processor is running at a time.

### Empty results

If queries return empty results, make sure you've processed files first using the processor script.

## Testing

To test the server functionality, run:

```bash
cd /home/runner/work/netdatamcp/netdatamcp
python test_server.py
```

This will test all database operations and verify that the parsers are working correctly.
