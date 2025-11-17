# Juniper SNMP MIB Import Guide

This guide explains how to download and import Juniper SNMP MIBs into the NetData MCP server.

## Overview

The Juniper MIB management system allows you to:
- Download SNMP MIBs from Juniper's MIB Explorer
- Select specific Junos versions and product families
- Automatically organize MIBs by product and version
- Process MIBs into the MCP server database

## Quick Start

### 1. Interactive Mode (Recommended for First Time)

The easiest way to get started is using interactive mode:

```bash
./sync_juniper_mibs.sh --interactive
```

This will guide you through:
1. Selecting which product family to download (e.g., Junos OS)
2. Choosing which version(s) to download (e.g., 24.2R1, 23.4R1)
3. Confirming and downloading the MIBs

### 2. List Available Configurations

To see what's configured:

```bash
./sync_juniper_mibs.sh --list
```

### 3. Download All Configured MIBs

To download all products and versions configured in `juniper_mibs.yaml`:

```bash
./sync_juniper_mibs.sh --download
```

### 4. Process MIBs into Database

After downloading, process the MIBs:

```bash
./process_files.sh
```

### 5. Start the MCP Server

```bash
./start_server.sh
```

## Configuration

### Configuring Products and Versions

Edit `juniper_mibs.yaml` to configure which products and versions to download:

```yaml
juniper_mibs:
  junos:
    name: "Junos OS"
    description: "Juniper Junos Operating System MIBs"
    versions:
      - "24.2R1"      # Add or remove versions as needed
      - "23.4R1"
      - "24.1R1"
    download_url: "https://apps.juniper.net/mib-explorer/download/{version}/all"
    enabled: true
```

### Settings

You can customize the behavior in the `settings` section of `juniper_mibs.yaml`:

```yaml
settings:
  # Where to store downloaded archives
  download_dir: "downloads/juniper_mibs"

  # Where to extract MIBs
  target_dir: "mibs/juniper"

  # Organize by version (creates subdirectories per version)
  organize_by_version: true

  # File patterns to extract
  file_patterns:
    - "*.mib"
    - "*.txt"
    - "*.my"

  # Automatically suggest processing after download
  auto_process: true

  # Delete archives after successful extraction
  cleanup_archives: false
```

## Usage Examples

### Download Specific Product

```bash
./sync_juniper_mibs.sh --download --product junos
```

### Download Specific Version

```bash
./sync_juniper_mibs.sh --download --product junos --version 24.2R1
```

### Clean Downloaded Files

Remove all downloaded archives and extracted MIBs:

```bash
./sync_juniper_mibs.sh --clean
```

### Clean and Re-download

```bash
./sync_juniper_mibs.sh --clean
./sync_juniper_mibs.sh --download
```

## Advanced Usage

### Using Python Script Directly

For more control, use the Python script directly:

```bash
# Show all options
python3 manage_juniper_mibs.py --help

# Download with verbose output
python3 manage_juniper_mibs.py --download --verbose

# Clean specific product
python3 manage_juniper_mibs.py --clean --product junos
```

## Directory Structure

After downloading and processing, your directory structure will look like:

```
netdatamcp/
├── downloads/
│   └── juniper_mibs/          # Downloaded archives (temporary)
│       └── junos/
│           ├── junos_24.2R1_mibs.tar.gz
│           ├── junos_23.4R1_mibs.tar.gz
│           └── [version]/     # Extracted files
│
├── mibs/
│   └── juniper/               # Organized MIB files
│       └── junos/
│           ├── 24.2R1/        # MIBs for version 24.2R1
│           │   ├── JUNIPER-SMI.mib
│           │   ├── JUNIPER-CHASSIS-MIB.mib
│           │   └── ...
│           └── 23.4R1/        # MIBs for version 23.4R1
│               └── ...
│
├── data/
│   └── netdata.db             # Processed MIBs in database
│
├── juniper_mibs.yaml          # Configuration
├── manage_juniper_mibs.py     # Main script
└── sync_juniper_mibs.sh       # Wrapper script
```

## Finding Available Versions

To find available Junos versions and MIBs:

1. Visit the Juniper MIB Explorer: https://apps.juniper.net/mib-explorer/download
2. Browse available versions
3. Add desired versions to `juniper_mibs.yaml`

Common Junos versions:
- **24.2R1** - Latest major release
- **24.1R1** - Previous release
- **23.4R1** - Long-term support release
- **23.2R1** - Previous LTS release

## Querying MIBs via MCP

Once processed, you can query Juniper MIBs through the MCP server:

### Example: Query All Juniper MIBs

```python
# Using MCP client
result = mcp_client.call_tool("query_data", {
    "type": "snmp",
    "name": "JUNIPER"
})
```

### Example: Get Specific MIB

```python
result = mcp_client.call_tool("query_data", {
    "type": "snmp",
    "name": "JUNIPER-CHASSIS-MIB"
})
```

### Example: List All SNMP MIBs

```python
result = mcp_client.call_tool("query_data", {
    "type": "snmp"
})
```

## Troubleshooting

### Download Fails

If downloads fail, check:

1. **Internet connection**: Ensure you can reach `apps.juniper.net`
2. **Download URL**: Verify the URL format in `juniper_mibs.yaml` is correct
3. **Version availability**: Check if the version exists on Juniper's site

Try with verbose mode:
```bash
python3 manage_juniper_mibs.py --download --verbose
```

### No MIBs Found After Download

1. Check if archives were downloaded:
   ```bash
   ls -la downloads/juniper_mibs/
   ```

2. Check if MIBs were extracted:
   ```bash
   ls -la mibs/juniper/
   ```

3. Verify file patterns in `juniper_mibs.yaml` match the archive contents

### Import Errors

If MIBs don't appear in the database after running `./process_files.sh`:

1. Check the processor logs
2. Verify MIB files are valid (proper syntax)
3. Ensure MIB files are in the correct location

## Notes on Download URLs

**Important**: The download URLs in `juniper_mibs.yaml` are templates and may need adjustment based on the actual Juniper MIB Explorer structure.

If the default URLs don't work:

1. Visit https://apps.juniper.net/mib-explorer/download
2. Inspect the actual download links
3. Update the `download_url` template in `juniper_mibs.yaml`

Example patterns you might find:
- `https://apps.juniper.net/mib-explorer/download/{version}/all`
- `https://apps.juniper.net/mibs/download?version={version}`
- Direct links to tar.gz files

## Requirements

- Python 3.7+
- PyYAML: `pip install pyyaml`
- requests: `pip install requests`

## Integration with Vendor Management

This Juniper MIB system works alongside the vendor YANG management system:

- **YANG models**: Managed via `manage_vendors.py` / `sync_vendors.sh`
- **Juniper MIBs**: Managed via `manage_juniper_mibs.py` / `sync_juniper_mibs.sh`

Both feed into the same MCP server database, providing comprehensive network data model access.

## Next Steps

After setting up Juniper MIBs:

1. **Add other vendors**: Extend `juniper_mibs.yaml` with other product families
2. **Automate updates**: Set up cron jobs to sync latest versions
3. **Query via MCP**: Use the MCP server to access MIB data
4. **Integrate with tools**: Connect VSCode or other MCP clients

## Support

For issues related to:
- **NetData MCP**: Check the main [README.md](README.md)
- **Juniper MIBs**: Visit [Juniper MIB Explorer](https://apps.juniper.net/mib-explorer/)
- **Script bugs**: Open an issue in the repository

## License

This tool is part of the NetData MCP project. See [LICENSE](LICENSE) for details.
