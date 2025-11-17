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

### Managing Vendor YANG Model Repositories

The server includes a vendor management system to automatically pull and process YANG models from public vendor repositories. This makes it easy to keep vendor models up-to-date.

#### Quick Start

```bash
# Sync all vendor repositories and process YANG files
./sync_vendors.sh

# Or use the Python script directly
python manage_vendors.py --sync --process
```

#### Vendor Configuration

Vendors are configured in the `vendors.yaml` file. The default configuration includes Nokia:

```yaml
vendors:
  nokia:
    name: "Nokia"
    repo_url: "https://github.com/nokia/7x50_YangModels.git"
    description: "Nokia 7x50 YANG Models"
    yang_paths:
      - "latest_sros_23.10/**/*.yang"
      - "latest_sros_24.3/**/*.yang"
    branch: "master"
    enabled: true
```

#### Adding New Vendors

To add a new vendor, edit `vendors.yaml` and add a new vendor entry:

```yaml
vendors:
  cisco:
    name: "Cisco"
    repo_url: "https://github.com/YangModels/yang.git"
    description: "Cisco YANG Models"
    yang_paths:
      - "vendor/cisco/**/*.yang"
    branch: "main"
    enabled: true
```

#### Vendor Management Commands

```bash
# List all configured vendors
python manage_vendors.py --list

# Sync only a specific vendor
python manage_vendors.py --sync --vendor nokia

# Process YANG files without syncing
python manage_vendors.py --process

# Clean and re-sync all vendors
python manage_vendors.py --clean --sync --process

# Full help
python manage_vendors.py --help
```

#### Workflow

1. **Sync vendor repositories**: `./sync_vendors.sh --sync`
   - Clones vendor repos to `vendors/` directory
   - Updates existing repos with latest changes

2. **Process YANG files**: `./sync_vendors.sh --process`
   - Copies YANG files from vendor repos to `yang/<vendor>/`
   - Preserves directory structure

3. **Parse into database**: `./process_files.sh`
   - Parses all YANG files and stores in SQLite database

4. **Query via MCP server**: `./start_server.sh`
   - Access parsed YANG models through MCP tools

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

## License

ISC