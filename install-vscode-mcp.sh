#!/bin/bash

# NetData MCP Server - VSCode Installation Script
# This script configures VSCode to use the NetData MCP server for all Claude models
# Server URL: https://netdata.0xp.dev/mcp
# Purpose: Query and analyze YANG modules and SNMP MIB data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MCP_SERVER_URL="https://netdata.0xp.dev/mcp"
MCP_SERVER_NAME="netdata"
MCP_DESCRIPTION="NetData MCP server for YANG and SNMP MIB data queries"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to get VSCode config directory
get_vscode_config_dir() {
    local os_type=$(detect_os)

    if [[ "$os_type" == "linux" ]]; then
        echo "$HOME/.config/Code/User"
    elif [[ "$os_type" == "macos" ]]; then
        echo "$HOME/Library/Application Support/Code/User"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Function to get Claude Code config directory
get_claude_code_config_dir() {
    local os_type=$(detect_os)

    if [[ "$os_type" == "linux" ]]; then
        echo "$HOME/.config/claude-code"
    elif [[ "$os_type" == "macos" ]]; then
        echo "$HOME/Library/Application Support/claude-code"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Installing jq for JSON manipulation..."

        local os_type=$(detect_os)
        if [[ "$os_type" == "linux" ]]; then
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y jq
            elif command -v yum &> /dev/null; then
                sudo yum install -y jq
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y jq
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm jq
            else
                print_error "Could not install jq automatically. Please install jq manually and run this script again."
                exit 1
            fi
        elif [[ "$os_type" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install jq
            else
                print_error "Homebrew not found. Please install jq manually and run this script again."
                exit 1
            fi
        fi

        print_success "jq installed successfully"
    fi
}

# Function to test MCP server connectivity
test_mcp_server() {
    print_info "Testing connectivity to MCP server at $MCP_SERVER_URL..."

    if command -v curl &> /dev/null; then
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$MCP_SERVER_URL" || echo "000")

        if [[ "$http_code" == "000" ]]; then
            print_warning "Could not connect to $MCP_SERVER_URL"
            print_warning "The server might not be running yet. You can still configure VSCode."
            read -p "Do you want to continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            print_success "MCP server is accessible (HTTP $http_code)"
        fi
    else
        print_warning "curl not found. Skipping connectivity test."
    fi
}

# Function to configure VSCode settings
configure_vscode() {
    local vscode_config_dir=$(get_vscode_config_dir)
    local settings_file="$vscode_config_dir/settings.json"

    print_info "Configuring VSCode settings at $settings_file..."

    # Create directory if it doesn't exist
    mkdir -p "$vscode_config_dir"

    # Create settings file if it doesn't exist
    if [[ ! -f "$settings_file" ]]; then
        echo "{}" > "$settings_file"
        print_info "Created new settings.json file"
    fi

    # Backup existing settings
    cp "$settings_file" "$settings_file.backup.$(date +%Y%m%d_%H%M%S)"
    print_info "Backed up existing settings"

    # Add or update MCP server configuration
    local temp_file=$(mktemp)

    jq --arg server_name "$MCP_SERVER_NAME" \
       --arg server_url "$MCP_SERVER_URL" \
       --arg description "$MCP_DESCRIPTION" \
       '
       .["claude.mcpServers"] = (.["claude.mcpServers"] // {}) |
       .["claude.mcpServers"][$server_name] = {
           "url": $server_url,
           "transport": "http",
           "description": $description
       } |
       .["claude.mcpServers"][$server_name + ".enabled"] = true
       ' "$settings_file" > "$temp_file"

    mv "$temp_file" "$settings_file"
    print_success "VSCode settings updated"
}

# Function to configure Claude Code MCP settings
configure_claude_code() {
    local claude_config_dir=$(get_claude_code_config_dir)
    local mcp_settings_file="$claude_config_dir/mcp_settings.json"

    print_info "Configuring Claude Code MCP settings at $mcp_settings_file..."

    # Create directory if it doesn't exist
    mkdir -p "$claude_config_dir"

    # Create MCP settings file if it doesn't exist
    if [[ ! -f "$mcp_settings_file" ]]; then
        echo "{\"mcpServers\":{}}" > "$mcp_settings_file"
        print_info "Created new mcp_settings.json file"
    fi

    # Backup existing settings
    if [[ -f "$mcp_settings_file" ]]; then
        cp "$mcp_settings_file" "$mcp_settings_file.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backed up existing MCP settings"
    fi

    # Add or update MCP server configuration
    local temp_file=$(mktemp)

    jq --arg server_name "$MCP_SERVER_NAME" \
       --arg server_url "$MCP_SERVER_URL" \
       --arg description "$MCP_DESCRIPTION" \
       '
       .mcpServers = (.mcpServers // {}) |
       .mcpServers[$server_name] = {
           "url": $server_url,
           "transport": "http",
           "description": $description,
           "enabled": true,
           "availableToAllModels": true
       }
       ' "$mcp_settings_file" > "$temp_file"

    mv "$temp_file" "$mcp_settings_file"
    print_success "Claude Code MCP settings updated"
}

# Function to configure for Cline/Claude Dev extension
configure_cline() {
    local vscode_config_dir=$(get_vscode_config_dir)
    local cline_dir="$vscode_config_dir/globalStorage/saoudrizwan.claude-dev/settings"
    local cline_mcp_file="$cline_dir/cline_mcp_settings.json"

    if [[ -d "$vscode_config_dir/globalStorage/saoudrizwan.claude-dev" ]]; then
        print_info "Configuring Cline/Claude Dev extension..."

        mkdir -p "$cline_dir"

        # Create MCP settings file if it doesn't exist
        if [[ ! -f "$cline_mcp_file" ]]; then
            echo "{\"mcpServers\":{}}" > "$cline_mcp_file"
            print_info "Created new Cline MCP settings file"
        fi

        # Backup existing settings
        if [[ -f "$cline_mcp_file" ]]; then
            cp "$cline_mcp_file" "$cline_mcp_file.backup.$(date +%Y%m%d_%H%M%S)"
        fi

        # Add or update MCP server configuration
        local temp_file=$(mktemp)

        jq --arg server_name "$MCP_SERVER_NAME" \
           --arg server_url "$MCP_SERVER_URL" \
           --arg description "$MCP_DESCRIPTION" \
           '
           .mcpServers = (.mcpServers // {}) |
           .mcpServers[$server_name] = {
               "url": $server_url,
               "transport": "http",
               "description": $description,
               "enabled": true
           }
           ' "$cline_mcp_file" > "$temp_file"

        mv "$temp_file" "$cline_mcp_file"
        print_success "Cline/Claude Dev extension configured"
    else
        print_info "Cline/Claude Dev extension not found, skipping"
    fi
}

# Function to display summary
display_summary() {
    echo
    echo "======================================================================"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo "======================================================================"
    echo
    echo "MCP Server Configuration:"
    echo "  Name:        $MCP_SERVER_NAME"
    echo "  URL:         $MCP_SERVER_URL"
    echo "  Description: $MCP_DESCRIPTION"
    echo
    echo "Next Steps:"
    echo "  1. Restart VSCode to apply the changes"
    echo "  2. Open a Claude conversation in VSCode"
    echo "  3. The Netdata MCP server should now be available to all models"
    echo "  4. You can verify the installation in VSCode settings"
    echo
    echo "Configuration Files Modified:"
    local vscode_dir=$(get_vscode_config_dir)
    local claude_dir=$(get_claude_code_config_dir)
    echo "  - $vscode_dir/settings.json"
    echo "  - $claude_dir/mcp_settings.json"
    local cline_dir="$vscode_dir/globalStorage/saoudrizwan.claude-dev/settings"
    if [[ -d "$cline_dir" ]]; then
        echo "  - $cline_dir/cline_mcp_settings.json"
    fi
    echo
    echo "Backups have been created with .backup.YYYYMMDD_HHMMSS extension"
    echo "======================================================================"
}

# Main installation process
main() {
    echo "======================================================================"
    echo "NetData MCP Server - VSCode Installation Script"
    echo "YANG and SNMP MIB Data Query Tool"
    echo "======================================================================"
    echo

    print_info "Detecting operating system..."
    local os_type=$(detect_os)
    print_success "Operating system: $os_type"

    # Check for jq
    check_jq

    # Test MCP server connectivity
    test_mcp_server

    # Configure VSCode
    configure_vscode

    # Configure Claude Code
    configure_claude_code

    # Configure Cline if present
    configure_cline

    # Display summary
    display_summary
}

# Run main function
main
