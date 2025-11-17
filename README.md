# Netdata MCP Server

A Model Context Protocol (MCP) server that provides integration between Claude and Netdata monitoring system, enabling AI-powered monitoring, performance analysis, and infrastructure insights.

## Overview

This MCP server allows Claude to interact with Netdata's real-time performance and monitoring data, providing intelligent analysis and insights about your infrastructure.

**Server URL:** `https://netdata.0xp.dev/mcp`

## Features

- Real-time monitoring data access
- Performance metrics analysis
- Infrastructure health insights
- System resource monitoring
- Custom alerts and notifications

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
      "description": "Netdata monitoring and performance metrics MCP server",
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
      "description": "Netdata monitoring and performance metrics MCP server",
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
3. The Netdata MCP server should appear in the available tools
4. You can now ask Claude questions about your monitoring data

Example queries:
- "Show me the current system performance metrics"
- "What are the CPU usage trends over the last hour?"
- "Are there any performance anomalies in the infrastructure?"

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

## Uninstalling

To remove the Netdata MCP server from your VSCode configuration:

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

[Add your license information here]

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

---

**Note:** This MCP server requires an active Netdata instance to function properly. Ensure your Netdata instance is properly configured and accessible.