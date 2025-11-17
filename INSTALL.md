# Installation Guide - NetData MCP Server for VSCode

This guide provides detailed instructions for installing and configuring the NetData MCP server (YANG and SNMP MIB data queries) in VSCode.

## Prerequisites

- **VSCode** installed on your system
- One of the following VSCode extensions:
  - Official Claude extension
  - Claude Code extension
  - Cline (formerly Claude Dev) extension
- **Internet connection** to access the MCP server at `https://netdata.0xp.dev/mcp`

## Supported Operating Systems

- Linux (Ubuntu, Debian, Fedora, Arch, and other major distributions)
- macOS (all recent versions)

## Installation Methods

### Method 1: Automated Installation (Recommended)

#### One-Line Installation

The fastest way to install is using curl:

```bash
curl -fsSL https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh | bash
```

#### Manual Download and Install

If you prefer to review the script before running:

```bash
# Download the installation script
wget https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh

# Or using curl
curl -O https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh

# Make it executable
chmod +x install-vscode-mcp.sh

# Review the script (optional but recommended)
cat install-vscode-mcp.sh

# Run the installation
./install-vscode-mcp.sh
```

#### What Happens During Installation

The script will:

1. **Detect your OS** - Automatically identifies Linux or macOS
2. **Install dependencies** - Installs `jq` if not already present (requires sudo)
3. **Test connectivity** - Verifies the MCP server is accessible
4. **Backup existing configs** - Creates timestamped backups of all configuration files
5. **Update VSCode settings** - Adds MCP server configuration to `settings.json`
6. **Configure Claude Code** - Updates Claude Code MCP settings
7. **Configure Cline** - Updates Cline/Claude Dev settings if installed
8. **Display summary** - Shows what was configured and next steps

### Method 2: Manual Installation

If you prefer manual configuration or the automated script doesn't work:

#### Step 1: Locate Configuration Files

**Linux:**
- VSCode settings: `~/.config/Code/User/settings.json`
- Claude Code: `~/.config/claude-code/mcp_settings.json`
- Cline: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**macOS:**
- VSCode settings: `~/Library/Application Support/Code/User/settings.json`
- Claude Code: `~/Library/Application Support/claude-code/mcp_settings.json`
- Cline: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

#### Step 2: Update VSCode Settings

Edit `settings.json` and add the following configuration:

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

**Important:** If you already have other settings in your `settings.json`, merge this configuration with your existing settings. Don't replace the entire file.

#### Step 3: Update Claude Code MCP Settings

Create or edit the MCP settings file:

```bash
# Linux
mkdir -p ~/.config/claude-code
nano ~/.config/claude-code/mcp_settings.json

# macOS
mkdir -p ~/Library/Application\ Support/claude-code
nano ~/Library/Application\ Support/claude-code/mcp_settings.json
```

Add the following content:

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

#### Step 4: Update Cline Settings (if applicable)

If you're using Cline/Claude Dev, create or edit the Cline MCP settings:

```bash
# Linux
mkdir -p ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings
nano ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# macOS
mkdir -p ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings
nano ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

Add the following content:

```json
{
  "mcpServers": {
    "netdata": {
      "url": "https://netdata.0xp.dev/mcp",
      "transport": "http",
      "description": "NetData MCP server for YANG and SNMP MIB data queries",
      "enabled": true
    }
  }
}
```

## Post-Installation

### 1. Restart VSCode

After installation, completely close and restart VSCode:

```bash
# Close all VSCode windows, then reopen
code .
```

### 2. Verify Installation

1. Open VSCode
2. Start a new Claude conversation
3. Look for the NetData MCP server in the available tools
4. Try a test query: "Query all YANG modules" or "What SNMP MIBs are available?"

### 3. Test the MCP Server

You can verify the server is accessible from your terminal:

```bash
curl -I https://netdata.0xp.dev/mcp
```

You should see a successful HTTP response.

## Troubleshooting

### Issue: jq Installation Fails

**Symptoms:** The script fails to install `jq` automatically.

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y jq
```

**Fedora:**
```bash
sudo dnf install -y jq
```

**Arch Linux:**
```bash
sudo pacman -S jq
```

**macOS:**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install jq
brew install jq
```

Then run the installation script again.

### Issue: MCP Server Not Appearing

**Symptoms:** After installation, the NetData MCP server doesn't appear in Claude.

**Solutions:**

1. **Verify settings were updated:**
   ```bash
   # Linux
   cat ~/.config/Code/User/settings.json | jq '.["claude.mcpServers"]'

   # macOS
   cat ~/Library/Application\ Support/Code/User/settings.json | jq '.["claude.mcpServers"]'
   ```

2. **Check VSCode extension logs:**
   - Open VSCode
   - Go to View → Output
   - Select "Claude" or "Cline" from the dropdown
   - Look for any error messages

3. **Restart VSCode completely:**
   - Close all VSCode windows
   - On macOS, ensure VSCode is fully quit (Cmd+Q)
   - Reopen VSCode

4. **Clear VSCode cache:**
   ```bash
   # Linux
   rm -rf ~/.config/Code/Cache
   rm -rf ~/.config/Code/CachedData

   # macOS
   rm -rf ~/Library/Application\ Support/Code/Cache
   rm -rf ~/Library/Application\ Support/Code/CachedData
   ```

### Issue: Permission Denied

**Symptoms:** The script fails with permission errors when installing `jq`.

**Solution:** Run the script with sudo when prompted, or install jq manually first:

```bash
# Install jq manually
sudo apt-get install -y jq  # Ubuntu/Debian
# OR
sudo dnf install -y jq      # Fedora
# OR
brew install jq             # macOS

# Then run the installation script (without sudo)
./install-vscode-mcp.sh
```

### Issue: Cannot Connect to MCP Server

**Symptoms:** The installation completes but the server is unreachable.

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping -c 3 netdata.0xp.dev
   ```

2. **Test server accessibility:**
   ```bash
   curl -v https://netdata.0xp.dev/mcp
   ```

3. **Check firewall settings:**
   - Ensure your firewall allows outbound HTTPS connections
   - Check corporate proxy settings if applicable

4. **Verify DNS resolution:**
   ```bash
   nslookup netdata.0xp.dev
   ```

### Issue: Configuration Corrupted

**Symptoms:** VSCode behaves unexpectedly after installation.

**Solution:** Restore from backup:

```bash
# Find backup files (they have timestamps)
# Linux
ls -la ~/.config/Code/User/settings.json.backup.*

# macOS
ls -la ~/Library/Application\ Support/Code/User/settings.json.backup.*

# Restore the most recent backup
# Linux
cp ~/.config/Code/User/settings.json.backup.YYYYMMDD_HHMMSS \
   ~/.config/Code/User/settings.json

# macOS
cp ~/Library/Application\ Support/Code/User/settings.json.backup.YYYYMMDD_HHMMSS \
   ~/Library/Application\ Support/Code/User/settings.json
```

Replace `YYYYMMDD_HHMMSS` with the actual timestamp from your backup file.

## Available MCP Tools

After successful installation, Claude will have access to these tools:

- **query_data**: Query YANG/SNMP data with optional filters
  - Parameters: `type` (yang/snmp), `name`, `version`
- **list_all_data**: List all parsed data entries
- **get_versions**: Get all versions of a specific module/MIB
  - Parameters: `name` (required)
- **get_statistics**: Get database statistics

## Uninstalling

### Automated Removal

Edit your configuration files and remove the `netdata` entry:

```bash
# Linux
nano ~/.config/Code/User/settings.json
nano ~/.config/claude-code/mcp_settings.json

# macOS
nano ~/Library/Application\ Support/Code/User/settings.json
nano ~/Library/Application\ Support/claude-code/mcp_settings.json
```

Remove the entire `"netdata": { ... }` block from the `mcpServers` section.

### Complete Reset

To completely remove all MCP server configurations (this will remove ALL MCP servers, not just Netdata):

```bash
# Backup first!
# Linux
cp ~/.config/Code/User/settings.json ~/.config/Code/User/settings.json.backup
# Then edit and remove the entire "claude.mcpServers" section

# macOS
cp ~/Library/Application\ Support/Code/User/settings.json \
   ~/Library/Application\ Support/Code/User/settings.json.backup
# Then edit and remove the entire "claude.mcpServers" section
```

## Advanced Configuration

### Using a Different Server URL

If you're running your own Netdata MCP server, edit the script before running:

```bash
# Download the script
wget https://raw.githubusercontent.com/DigitalVortexLLC/netdatamcp/main/install-vscode-mcp.sh

# Edit the MCP_SERVER_URL variable
nano install-vscode-mcp.sh

# Change this line:
MCP_SERVER_URL="https://netdata.0xp.dev/mcp"
# To your server URL:
MCP_SERVER_URL="https://your-server.example.com/mcp"

# Save and run
./install-vscode-mcp.sh
```

### Restricting to Specific Models

To make the MCP server available to specific models only, manually edit the configuration:

```json
{
  "mcpServers": {
    "netdata": {
      "url": "https://netdata.0xp.dev/mcp",
      "transport": "http",
      "description": "Netdata monitoring and performance metrics MCP server",
      "enabled": true,
      "availableToAllModels": false,
      "allowedModels": ["claude-3-sonnet", "claude-3-opus"]
    }
  }
}
```

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/DigitalVortexLLC/netdatamcp/issues)
2. Review [VSCode MCP documentation](https://docs.claude.com/)
3. Create a new issue with:
   - Your OS and version
   - VSCode version
   - Claude extension version
   - Full error messages
   - Steps to reproduce

## Security Considerations

- The installation script requires sudo access only for installing `jq`
- Configuration files are modified with user permissions only
- Backups are created automatically before any changes
- The MCP server connection uses HTTPS for security
- Review the installation script before running if you have security concerns

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for usage examples
2. Explore YANG and SNMP MIB querying capabilities
3. Try example queries in Claude:
   - "Query all YANG modules"
   - "Show me ietf-interfaces versions"
   - "What SNMP MIBs are in the database?"
4. Review the main branch for full server documentation

---

**Last Updated:** 2025-11-17
**Version:** 1.0.0
