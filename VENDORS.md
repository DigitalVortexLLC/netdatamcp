# Vendor YANG Model Repository Management

This document provides detailed information about managing vendor YANG model repositories for the NetData MCP server.

## Overview

The vendor management system allows you to automatically pull YANG models from public vendor GitHub repositories and process them for use with the MCP server. This system:

- Supports multiple vendors with a simple YAML configuration
- Automatically clones and updates vendor repositories
- Processes YANG files into the server's `yang/` directory
- Preserves vendor directory structures
- Allows selective processing of specific YANG file paths

## Quick Start

```bash
# List configured vendors
python manage_vendors.py --list

# Sync and process all vendors
./sync_vendors.sh

# Sync only Nokia
./sync_vendors.sh --vendor nokia
```

## Configuration

### vendors.yaml Structure

The `vendors.yaml` file defines all vendor repositories. Each vendor entry includes:

```yaml
vendors:
  <vendor_id>:
    name: "Vendor Display Name"
    repo_url: "https://github.com/vendor/repo.git"
    description: "Brief description"
    yang_paths:
      - "path/to/yang/**/*.yang"
      - "another/path/**/*.yang"
    branch: "master"  # or "main", or specific tag
    enabled: true
```

### Configuration Fields

- **vendor_id**: Unique identifier for the vendor (e.g., `nokia`, `cisco`)
- **name**: Human-readable vendor name
- **repo_url**: Git URL for the vendor's YANG model repository
- **description**: Brief description of the models
- **yang_paths**: List of glob patterns for locating YANG files within the repo
  - Supports wildcards: `**/*.yang` (recursive), `*.yang` (single level)
  - Can specify multiple paths for different model sets
- **branch**: Git branch or tag to checkout (default: `master`)
- **enabled**: Boolean to enable/disable the vendor (default: `true`)

## Currently Configured Vendors

### Nokia

- **Repository**: https://github.com/nokia/7x50_YangModels
- **Models**: Nokia 7x50 SROS YANG models
- **Versions**: SROS 23.10 and 24.3 (latest releases)
- **YANG Files**: ~1,084 models across both versions

The Nokia repository contains YANG models for:
- SR OS network devices
- Service routers (7750, 7450, 7250, 7950)
- Multiple SROS versions from 19.5 to 24.10

## Adding New Vendors

### Example: Adding Cisco YANG Models

1. Edit `vendors.yaml` and add a new entry:

```yaml
vendors:
  cisco:
    name: "Cisco"
    repo_url: "https://github.com/YangModels/yang.git"
    description: "Cisco IOS XE/XR YANG Models"
    yang_paths:
      - "vendor/cisco/xe/**/*.yang"
      - "vendor/cisco/xr/**/*.yang"
    branch: "main"
    enabled: true
```

2. Sync the new vendor:

```bash
python manage_vendors.py --sync --vendor cisco
```

3. Process the YANG files:

```bash
python manage_vendors.py --process --vendor cisco
```

### Example: Adding Juniper YANG Models

```yaml
vendors:
  juniper:
    name: "Juniper Networks"
    repo_url: "https://github.com/Juniper/yang.git"
    description: "Juniper Junos YANG Models"
    yang_paths:
      - "**/*.yang"
    branch: "master"
    enabled: true
```

### Example: Adding OpenConfig Models

```yaml
vendors:
  openconfig:
    name: "OpenConfig"
    repo_url: "https://github.com/openconfig/public.git"
    description: "OpenConfig Vendor-Neutral YANG Models"
    yang_paths:
      - "release/models/**/*.yang"
    branch: "master"
    enabled: true
```

## Command Reference

### Python Script (manage_vendors.py)

```bash
# List all vendors
python manage_vendors.py --list

# Sync all enabled vendors
python manage_vendors.py --sync

# Sync specific vendor
python manage_vendors.py --sync --vendor nokia

# Process YANG files (after syncing)
python manage_vendors.py --process

# Process specific vendor
python manage_vendors.py --process --vendor cisco

# Sync and process together
python manage_vendors.py --sync --process

# Clean and re-sync
python manage_vendors.py --clean --sync --process

# Verbose output
python manage_vendors.py --sync --process --verbose
```

### Shell Script (sync_vendors.sh)

```bash
# Sync and process all (default)
./sync_vendors.sh

# Only sync
./sync_vendors.sh --sync

# Only process
./sync_vendors.sh --process

# Specific vendor
./sync_vendors.sh --vendor nokia

# Clean first
./sync_vendors.sh --clean --sync --process
```

## Directory Structure

```
netdatamcp/
├── vendors/              # Cloned vendor repositories (git ignored)
│   ├── nokia/           # Nokia repository clone
│   ├── cisco/           # Cisco repository clone (if added)
│   └── juniper/         # Juniper repository clone (if added)
│
├── yang/                # Processed YANG files
│   ├── nokia/           # Nokia YANG files
│   │   ├── latest_sros_23.10/
│   │   └── latest_sros_24.3/
│   ├── cisco/           # Cisco YANG files (if added)
│   └── ietf-interfaces.yang  # Example IETF file
│
├── vendors.yaml         # Vendor configuration
├── manage_vendors.py    # Management script
└── sync_vendors.sh      # Convenience wrapper
```

## Workflow

### Initial Setup

1. **Configure vendors** in `vendors.yaml`
2. **Sync repositories**: `./sync_vendors.sh --sync`
3. **Process YANG files**: `./sync_vendors.sh --process`
4. **Parse into database**: `./process_files.sh`
5. **Start MCP server**: `./start_server.sh`

### Regular Updates

To update vendor models with the latest versions:

```bash
# Update all vendors
./sync_vendors.sh

# Update specific vendor
./sync_vendors.sh --vendor nokia

# Then re-process into database
./process_files.sh
```

## Advanced Usage

### Custom YANG Paths

You can use complex glob patterns to selectively include YANG files:

```yaml
yang_paths:
  # Include all YANG files recursively
  - "**/*.yang"

  # Include specific directories
  - "release/models/**/*.yang"
  - "experimental/models/**/*.yang"

  # Include multiple versions
  - "latest_sros_23.*/**/*.yang"
  - "latest_sros_24.*/**/*.yang"

  # Include specific subdirectories
  - "vendor/cisco/xe/17*/**/*.yang"
```

### Selective Vendor Management

You can disable vendors without removing their configuration:

```yaml
vendors:
  cisco:
    name: "Cisco"
    repo_url: "https://github.com/YangModels/yang.git"
    enabled: false  # Temporarily disabled
```

### Branch and Version Control

Specify specific branches or tags:

```yaml
vendors:
  nokia:
    repo_url: "https://github.com/nokia/7x50_YangModels.git"
    branch: "master"  # or "v24.3" for a specific release
```

## Troubleshooting

### Repository Clone Fails

```bash
# Check network connectivity
curl -I https://github.com/nokia/7x50_YangModels

# Try manual clone
git clone https://github.com/nokia/7x50_YangModels.git test-clone
```

### No YANG Files Found

Check the `yang_paths` patterns:

```bash
# List files in the vendor repo
find vendors/nokia -name "*.yang" | head -20

# Update yang_paths in vendors.yaml to match actual structure
```

### Git Pull Errors

Clean and re-sync:

```bash
./sync_vendors.sh --clean --sync
```

## Best Practices

1. **Start with one vendor** - Test with Nokia before adding others
2. **Use specific paths** - Limit yang_paths to needed models to reduce processing time
3. **Regular updates** - Run sync periodically to get latest vendor models
4. **Version control** - Consider specific branches/tags for production stability
5. **Selective enabling** - Disable vendors you don't actively use

## Future Enhancements

Potential improvements to the vendor management system:

- [ ] Support for private repositories (authentication)
- [ ] Automatic change detection (only process updated files)
- [ ] Vendor-specific preprocessing scripts
- [ ] Model validation before processing
- [ ] Dependency resolution between YANG modules
- [ ] Web UI for vendor management
- [ ] Scheduled automatic updates

## Support

For vendor-specific YANG model questions:
- **Nokia**: https://github.com/nokia/7x50_YangModels
- **General YANG**: https://github.com/YangModels/yang

For issues with the vendor management script:
- Check the logs for detailed error messages
- Run with `--verbose` flag for debugging
- Review the `vendors.yaml` configuration
