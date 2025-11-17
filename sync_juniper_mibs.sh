#!/bin/bash
#
# Juniper MIB Sync Script
#
# Convenient wrapper for manage_juniper_mibs.py
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required Python packages are installed
python3 -c "import yaml" 2>/dev/null || {
    print_error "PyYAML is not installed. Install with: pip install pyyaml"
    exit 1
}

python3 -c "import requests" 2>/dev/null || {
    print_error "requests library is not installed. Install with: pip install requests"
    exit 1
}

# Default action
ACTION="help"

# Parse arguments
if [ $# -eq 0 ]; then
    ACTION="help"
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    ACTION="help"
elif [ "$1" = "--list" ]; then
    ACTION="list"
elif [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
    ACTION="interactive"
elif [ "$1" = "--download" ]; then
    ACTION="download"
    shift
    EXTRA_ARGS="$@"
elif [ "$1" = "--clean" ]; then
    ACTION="clean"
    shift
    EXTRA_ARGS="$@"
else
    # Pass all arguments to Python script
    python3 manage_juniper_mibs.py "$@"
    exit $?
fi

# Execute action
case $ACTION in
    help)
        cat << EOF
Juniper MIB Sync Script

Usage:
    ./sync_juniper_mibs.sh [options]

Options:
    --list                  List configured products and versions
    --interactive, -i       Interactive mode to select what to download
    --download             Download all configured MIBs
    --clean                Remove all downloaded files and MIBs
    --help, -h             Show this help message

Examples:
    # List available configurations
    ./sync_juniper_mibs.sh --list

    # Interactive mode (recommended)
    ./sync_juniper_mibs.sh --interactive

    # Download all configured MIBs
    ./sync_juniper_mibs.sh --download

    # Download specific product
    ./sync_juniper_mibs.sh --download --product junos

    # Download specific version
    ./sync_juniper_mibs.sh --download --product junos --version 24.2R1

    # Clean and re-download
    ./sync_juniper_mibs.sh --clean
    ./sync_juniper_mibs.sh --download

Advanced:
    For more options, run:
    python3 manage_juniper_mibs.py --help

Configuration:
    Edit juniper_mibs.yaml to configure products, versions, and download settings

More Information:
    Juniper MIB Explorer: https://apps.juniper.net/mib-explorer/download
EOF
        ;;

    list)
        print_info "Listing configured Juniper MIB products..."
        python3 manage_juniper_mibs.py --list
        ;;

    interactive)
        print_info "Starting interactive mode..."
        python3 manage_juniper_mibs.py --interactive
        ;;

    download)
        print_info "Downloading Juniper MIBs..."
        python3 manage_juniper_mibs.py --download $EXTRA_ARGS

        if [ $? -eq 0 ]; then
            print_info "Download completed successfully!"
            echo ""
            print_info "Next steps:"
            echo "  1. Review downloaded MIBs in: mibs/juniper/"
            echo "  2. Run './process_files.sh' to parse MIBs into the database"
            echo "  3. Start the MCP server with './start_server.sh'"
        else
            print_error "Download failed. Check the logs above for details."
            exit 1
        fi
        ;;

    clean)
        print_warning "This will remove all downloaded MIB archives and extracted files."
        read -p "Are you sure? [y/N] " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Cleaning Juniper MIBs..."
            python3 manage_juniper_mibs.py --clean $EXTRA_ARGS
            print_info "Cleanup completed."
        else
            print_info "Cleanup cancelled."
        fi
        ;;
esac

exit 0
