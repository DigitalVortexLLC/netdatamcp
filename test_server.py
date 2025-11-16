#!/usr/bin/env python3
"""Test client for NetData MCP Server."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from netdatamcp.database import DatabaseManager

db_path = "data/netdata.db"
db = DatabaseManager(db_path)

print("=" * 80)
print("Testing NetData MCP Server - Database Layer")
print("=" * 80)

print("\n1. Test get_all_data:")
all_data = db.get_all_data()
print(f"Total entries: {len(all_data)}")
for entry in all_data:
    print(f"  - {entry['type']}: {entry['name']} (v{entry['version']})")

print("\n2. Test query_by_type('yang'):")
yang_data = db.query_by_type('yang')
print(f"YANG entries: {len(yang_data)}")
for entry in yang_data:
    print(f"  - {entry['name']} (v{entry['version']})")

print("\n3. Test query_by_type('snmp'):")
snmp_data = db.query_by_type('snmp')
print(f"SNMP entries: {len(snmp_data)}")
for entry in snmp_data:
    print(f"  - {entry['name']} (v{entry['version']})")

print("\n4. Test query_by_name('ietf'):")
search_results = db.query_by_name('ietf')
print(f"Search results for 'ietf': {len(search_results)}")
for entry in search_results:
    print(f"  - {entry['name']} (v{entry['version']})")

print("\n5. Test get_versions('ietf-interfaces'):")
versions = db.get_versions('ietf-interfaces')
print(f"Versions: {versions}")

print("\n6. Test get_versions('SNMPv2-MIB'):")
versions = db.get_versions('SNMPv2-MIB')
print(f"Versions: {versions}")

print("\n7. Test statistics:")
yang_count = len(db.query_by_type('yang'))
snmp_count = len(db.query_by_type('snmp'))
total = yang_count + snmp_count
print(f"Total: {total}, YANG: {yang_count}, SNMP: {snmp_count}")

db.close()

print("\n" + "=" * 80)
print("All tests completed successfully!")
print("=" * 80)
