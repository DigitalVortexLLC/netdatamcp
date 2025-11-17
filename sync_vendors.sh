#!/bin/bash
# Convenience script to sync and process vendor YANG model repositories

set -e

echo "==================================================================="
echo "  Vendor YANG Model Repository Manager"
echo "==================================================================="
echo ""

# Default to sync and process
SYNC=false
PROCESS=false
VENDOR=""
CLEAN=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --sync)
            SYNC=true
            shift
            ;;
        --process)
            PROCESS=true
            shift
            ;;
        --vendor)
            VENDOR="--vendor $2"
            shift 2
            ;;
        --clean)
            CLEAN="--clean"
            shift
            ;;
        --all)
            SYNC=true
            PROCESS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--sync] [--process] [--all] [--vendor <name>] [--clean]"
            echo ""
            echo "Options:"
            echo "  --sync      Sync vendor repositories"
            echo "  --process   Process YANG files"
            echo "  --all       Both sync and process (default)"
            echo "  --vendor    Only process specific vendor"
            echo "  --clean     Clean before syncing"
            exit 1
            ;;
    esac
done

# If no options specified, do both
if [ "$SYNC" = false ] && [ "$PROCESS" = false ]; then
    SYNC=true
    PROCESS=true
fi

# Build command
CMD="python3 manage_vendors.py"
[ "$SYNC" = true ] && CMD="$CMD --sync"
[ "$PROCESS" = true ] && CMD="$CMD --process"
[ -n "$VENDOR" ] && CMD="$CMD $VENDOR"
[ -n "$CLEAN" ] && CMD="$CMD $CLEAN"

# Execute
echo "Running: $CMD"
echo ""
$CMD

echo ""
echo "==================================================================="
echo "  Done!"
echo "==================================================================="
