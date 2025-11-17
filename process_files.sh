#!/bin/bash
# Process YANG and SNMP MIB files

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src"

echo "Processing YANG and SNMP MIB files..."
python -m netdatamcp.processor
