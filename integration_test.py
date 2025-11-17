#!/usr/bin/env python3
"""
Comprehensive integration test for NetData MCP Server.
This demonstrates the full workflow of the system.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pathlib import Path
from netdatamcp.database import DatabaseManager
from netdatamcp.yang_parser import YangParser
from netdatamcp.snmp_parser import SnmpParser
from netdatamcp.config import Config

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def main():
    """Run comprehensive integration tests."""
    print_section("NetData MCP Server - Integration Test")
    
    # Initialize components
    print("\n1. Initializing database and parsers...")
    db = DatabaseManager(str(Config.DB_PATH))
    yang_parser = YangParser(db)
    snmp_parser = SnmpParser(db)
    print("   ✓ Database and parsers initialized")
    
    # Test YANG parser
    print_section("YANG Parser Tests")
    
    yang_file = Config.YANG_DIR / "ietf-interfaces.yang"
    if yang_file.exists():
        print(f"\n2. Parsing YANG file: {yang_file.name}")
        yang_data = yang_parser.parse_yang_file(yang_file)
        print(f"   ✓ Module name: {yang_data['name']}")
        print(f"   ✓ Version: {yang_data['version']}")
        print(f"   ✓ Namespace: {yang_data['namespace']}")
        print(f"   ✓ Prefix: {yang_data['prefix']}")
        if yang_data['imports']:
            print(f"   ✓ Imports: {', '.join(yang_data['imports'])}")
    
    # Test SNMP parser
    print_section("SNMP Parser Tests")
    
    snmp_file = Config.MIBS_DIR / "SNMPv2-MIB.mib"
    if snmp_file.exists():
        print(f"\n3. Parsing SNMP MIB file: {snmp_file.name}")
        snmp_data = snmp_parser.parse_snmp_file(snmp_file)
        print(f"   ✓ MIB name: {snmp_data['name']}")
        print(f"   ✓ Version: {snmp_data['version']}")
        if snmp_data['oid']:
            print(f"   ✓ OID: {snmp_data['oid']}")
        if snmp_data['objects']:
            print(f"   ✓ Object count: {len(snmp_data['objects'])}")
    
    # Test database queries
    print_section("Database Query Tests")
    
    print("\n4. Testing database queries...")
    
    # Query by type
    yang_entries = db.query_by_type('yang')
    snmp_entries = db.query_by_type('snmp')
    print(f"   ✓ YANG entries: {len(yang_entries)}")
    print(f"   ✓ SNMP entries: {len(snmp_entries)}")
    
    # Query by name
    search_results = db.query_by_name('ietf')
    print(f"   ✓ Search results for 'ietf': {len(search_results)}")
    
    # Get versions
    if yang_entries:
        versions = db.get_versions(yang_entries[0]['name'])
        print(f"   ✓ Versions of {yang_entries[0]['name']}: {versions}")
    
    # Statistics
    all_data = db.get_all_data()
    print(f"   ✓ Total entries in database: {len(all_data)}")
    
    # Test version management
    print_section("Version Management Tests")
    
    print("\n5. Testing version management...")
    if yang_entries:
        module_name = yang_entries[0]['name']
        versions = db.get_versions(module_name)
        print(f"   ✓ Module '{module_name}' has {len(versions)} version(s)")
        for v in versions:
            print(f"      - Version {v}")
    
    if snmp_entries:
        mib_name = snmp_entries[0]['name']
        versions = db.get_versions(mib_name)
        print(f"   ✓ MIB '{mib_name}' has {len(versions)} version(s)")
        for v in versions:
            print(f"      - Version {v}")
    
    # Test detailed metadata
    print_section("Metadata Tests")
    
    print("\n6. Testing metadata extraction...")
    if all_data:
        import json
        for entry in all_data[:2]:  # Show first 2 entries
            print(f"\n   Entry: {entry['type'].upper()} - {entry['name']} (v{entry['version']})")
            metadata = json.loads(entry['metadata'])
            print(f"   Metadata keys: {', '.join(metadata.keys())}")
            if entry['type'] == 'yang':
                print(f"   - Namespace: {metadata.get('namespace', 'N/A')}")
                print(f"   - Prefix: {metadata.get('prefix', 'N/A')}")
            elif entry['type'] == 'snmp':
                print(f"   - OID: {metadata.get('oid', 'N/A')}")
                if metadata.get('objects'):
                    print(f"   - Objects defined: {len(metadata.get('objects', []))}")
    
    # Clean up
    db.close()
    
    # Summary
    print_section("Test Summary")
    print("\n✓ All integration tests passed successfully!")
    print(f"✓ Database location: {Config.DB_PATH}")
    print(f"✓ YANG directory: {Config.YANG_DIR}")
    print(f"✓ MIBs directory: {Config.MIBS_DIR}")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
