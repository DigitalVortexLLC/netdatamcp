# NetData MCP Server

A Model Context Protocol (MCP) server that provides integration between Claude and YANG/SNMP MIB data, enabling AI-powered network data model queries and analysis.

## Overview

This MCP server allows Claude to interact with YANG modules and SNMP MIB definitions, providing intelligent querying and analysis of network device data models with version management.

**Server URL:** `https://netdata.0xp.dev/mcp`

## Features

- YANG module data querying
- SNMP MIB definition access
- Version management for network data models
- Multi-format support (YANG and SNMP)
- LLM-powered network data model analysis
- SQLite-based efficient storage and retrieval

## Installation for VSCode

### Quick Install

Run the automated installation script to configure VSCode to use the Netdata MCP server:

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

### What the Script Does

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

## Manual Installation

If you prefer to configure manually, add the following to your VSCode settings:

### VSCode Settings (`settings.json`)

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

### Claude Code MCP Settings (`~/.config/claude-code/mcp_settings.json`)

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

## Verification

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

## Troubleshooting

### Server Not Appearing in Claude

1. Ensure you've restarted VSCode after installation
2. Check that the server URL is accessible: `curl https://netdata.0xp.dev/mcp`
3. Verify the configuration files were updated correctly
4. Check VSCode extension logs for any errors

### Configuration Not Working

1. Restore from backup:
   ```bash
   # Backups are created with timestamp: filename.backup.YYYYMMDD_HHMMSS
   # Find the backup file and restore it if needed
   ```

2. Run the installation script again
3. Try manual configuration (see above)

### Connectivity Issues

If the MCP server is not accessible:
- Check your internet connection
- Verify firewall settings
- Ensure the server URL is correct: `https://netdata.0xp.dev/mcp`

## Available MCP Tools

Once installed, the following tools will be available to Claude:

- **query_data**: Query YANG/SNMP data with filters for type, name, and version
- **list_all_data**: List all parsed data entries in the database
- **get_versions**: Get all available versions for a specific module/MIB
- **get_statistics**: Get database statistics

## Uninstalling

To remove the NetData MCP server from your VSCode configuration:

1. Open VSCode settings (`settings.json`)
2. Remove the `netdata` entry from `claude.mcpServers`
3. Remove the corresponding entries from Claude Code and Cline settings
4. Restart VSCode

Or restore from the backup files created during installation.

## Support

For issues, questions, or contributions:
- GitHub Issues: [https://github.com/DigitalVortexLLC/netdatamcp/issues](https://github.com/DigitalVortexLLC/netdatamcp/issues)
- Documentation: [https://github.com/DigitalVortexLLC/netdatamcp](https://github.com/DigitalVortexLLC/netdatamcp)

## License

ISC

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

---

**Note:** This MCP server provides access to YANG modules and SNMP MIB definitions for network device data model analysis. It's designed for network engineers and operations teams working with network automation and data models.