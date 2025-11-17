# NetData MCP

An HTTP-based Model Context Protocol (MCP) server for managing and querying YANG and SNMP MIB data with versioning support, built with FastMCP and Python.

## Features

- **HTTP-based MCP Server**: RESTful API using FastMCP for querying network data definitions
- **Multi-format Support**: Parse and store both YANG modules and SNMP MIBs
- **Version Management**: Store multiple versions of the same module/MIB
- **SQLite Database**: Local storage with efficient querying capabilities
- **Side Process**: Background processor for parsing files while server is running
- **Query Tools**: Rich query interface for LLM-based data retrieval

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Project Structure

```
netdatamcp/
├── src/
│   ├── netdatamcp/
│   │   ├── __init__.py
│   │   ├── server.py         # FastMCP server implementation
│   │   ├── database.py       # SQLite database manager
│   │   ├── yang_parser.py    # YANG file parser
│   │   ├── snmp_parser.py    # SNMP MIB parser
│   │   └── processor.py      # Side process for file processing
│   └── main.py               # Main entry point
├── yang/                     # Directory for YANG files
├── mibs/                     # Directory for SNMP MIB files
├── data/                     # Database storage (auto-created)
└── requirements.txt
```

## Usage

### Starting the Server

```bash
# Using the convenience script
./start_server.sh

# Or using Python directly
PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python src/main.py
```

The FastMCP server will start in stdio mode and communicate using the Model Context Protocol.

### Processing Files

While the server is running (or independently), you can process YANG and SNMP MIB files:

```bash
# Using the convenience script
./process_files.sh

# Or using Python directly
PYTHONPATH=/home/runner/work/netdatamcp/netdatamcp/src python -m netdatamcp.processor
```

Place your files in the appropriate directories:
- YANG files (`.yang` extension) in the `yang/` directory
- SNMP MIB files (`.mib` or `.txt` extension) in the `mibs/` directory

### MCP Protocol Usage

The server implements the Model Context Protocol (MCP) and can be used with any MCP-compatible client. It exposes the following tools:

## MCP Tools

### query_data
Query parsed YANG/SNMP data from the database.

**Parameters:**
- `type` (optional): Filter by type ("yang" or "snmp")
- `name` (optional): Search by name (supports partial matching)
- `version` (optional): Filter by specific version

**Example:**
```python
# Query all YANG modules
query_data(type="yang")

# Query specific module with version
query_data(name="ietf-interfaces", version="2018-02-20")

# Search by partial name
query_data(name="ietf")
```

### list_all_data
List all parsed data entries in the database.

**Example:**
```python
list_all_data()
```

### get_versions
Get all available versions for a specific module/MIB name.

**Parameters:**
- `name` (required): Name of the module/MIB

**Example:**
```python
get_versions(name="ietf-interfaces")
```

### get_statistics
Get database statistics including counts of YANG and SNMP entries.

**Example:**
```python
get_statistics()
```

## MCP Resources

The server also exposes resources:

- `db://all` - Get all database data
- `db://stats` - Get database statistics

## Database Schema

The SQLite database stores parsed data with the following schema:

```sql
CREATE TABLE parsed_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,              -- 'yang' or 'snmp'
  name TEXT NOT NULL,              -- Module/MIB name
  version TEXT NOT NULL,           -- Version identifier
  data TEXT NOT NULL,              -- Full file content
  metadata TEXT,                   -- JSON metadata
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(type, name, version)
);
```

## Development

### Running in Development Mode

```bash
# Start the server
python src/main.py

# Process files
python -m netdatamcp.processor
```

### Installing in Development Mode

```bash
pip install -e .
```

## Example YANG and SNMP Files

The repository includes example files in the `yang/` and `mibs/` directories:
- `yang/ietf-interfaces.yang` - Example YANG module
- `mibs/SNMPv2-MIB.mib` - Example SNMP MIB

## Integration with LLMs

This MCP server is designed to be used with Large Language Models (LLMs) through the Model Context Protocol. The server provides tools that allow LLMs to:

1. Query network device data models (YANG and SNMP MIBs)
2. Search for specific modules or MIBs by name
3. Retrieve specific versions of data models
4. Get statistics about available network data

---

## VSCode Client Installation

For users who want to access this MCP server from VSCode using Claude extensions, we provide an automated installation script.

**Public Server URL:** `https://netdata.0xp.dev/mcp`

### Quick Install for VSCode

Run the automated installation script to configure VSCode to use the NetData MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh | bash
```

Or download and run manually:

```bash
# Download the script
wget https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh

# Make it executable
chmod +x install-vscode-mcp.sh

# Run the installation
./install-vscode-mcp.sh
```

### What the Installation Script Does

The installation script will:

1. ✅ Detect your operating system (Linux/macOS)
2. ✅ Check and install required dependencies (jq)
3. ✅ Test connectivity to the MCP server
4. ✅ Configure VSCode settings for Claude
5. ✅ Configure Claude Code MCP settings
6. ✅ Configure Cline/Claude Dev extension (if installed)
7. ✅ Create backups of all modified configuration files
8. ✅ Make the server available to all Claude models

### Supported Platforms

- **Linux**: Ubuntu, Debian, Fedora, Arch, and other major distributions
- **macOS**: All recent versions with Homebrew support

### Supported VSCode Extensions

- Official Claude extension
- Claude Code
- Cline (formerly Claude Dev)

### Manual VSCode Configuration

If you prefer to configure manually, add the following to your VSCode settings:

#### VSCode Settings (`settings.json`)

```json
{
  "claude.mcpServers": {
    "netdata": {
      "url": "https://netdata.0xp.dev/mcp",
      "transport": "http",
      "description": "NetData MCP server for YANG and SNMP MIB data queries",
      "enabled": true
    }
  }
}
```

#### Claude Code MCP Settings (`~/.config/claude-code/mcp_settings.json`)

```json
{
  "mcpServers": {
    "netdata": {
      "url": "https://netdata.0xp.dev/mcp",
      "transport": "http",
      "description": "NetData MCP server for YANG and SNMP MIB data queries",
      "enabled": true,
      "availableToAllModels": true
    }
  }
}
```

### Verification

After installation:

1. **Restart VSCode** to apply the changes
2. Open a Claude conversation
3. The NetData MCP server should appear in the available tools
4. You can now ask Claude questions about YANG modules and SNMP MIBs

Example queries:
- "Query all YANG modules in the database"
- "Show me the ietf-interfaces module version 2018-02-20"
- "What SNMP MIBs are available?"
- "List all versions of the SNMPv2-MIB"
- "Get statistics about available network data models"

### Troubleshooting

For detailed troubleshooting and advanced configuration options, see [INSTALL.md](INSTALL.md).

**Quick fixes:**

1. Ensure you've restarted VSCode after installation
2. Check that the server URL is accessible: `curl https://netdata.0xp.dev/mcp`
3. Verify the configuration files were updated correctly
4. Check VSCode extension logs for any errors

---

## License

ISC
