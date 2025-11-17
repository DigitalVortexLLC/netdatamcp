"""SNMP MIB file parser for extracting and storing MIB data."""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from .database import DatabaseManager


class SnmpParser:
    """Parser for SNMP MIB files."""

    def __init__(self, db: DatabaseManager):
        """Initialize with database manager."""
        self.db = db

    def parse_snmp_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse an SNMP MIB file and extract metadata."""
        content = file_path.read_text(encoding='utf-8')
        file_name = file_path.stem

        # Extract basic MIB metadata using regex
        mib_match = re.search(
            r'([A-Z][-A-Za-z0-9]*?)\s+DEFINITIONS\s*::=\s*BEGIN',
            content
        )
        revision_match = re.search(r'REVISION\s+"?([0-9]+[Z]?)"?', content)
        oid_match = re.search(
            r'MODULE-IDENTITY[^}]*OBJECT IDENTIFIER\s*::=\s*{\s*([^}]+)\s*}',
            content
        )
        description_match = re.search(r'DESCRIPTION\s+"([^"]+)"', content)

        # Extract imports
        import_matches = re.finditer(
            r'IMPORTS[^;]*FROM\s+([A-Z][A-Z0-9-]*)',
            content
        )
        imports = [match.group(1) for match in import_matches]

        # Extract object definitions
        object_matches = re.finditer(
            r'([A-Z][A-Za-z0-9-]*)\s+OBJECT[-\s](?:TYPE|IDENTIFIER)',
            content
        )
        objects = [match.group(1) for match in object_matches]

        mib_name = mib_match.group(1) if mib_match else file_name

        # Convert revision format from "YYYYMMDD" to "YYYY-MM-DD"
        version = "1.0.0"
        if revision_match:
            rev = revision_match.group(1).rstrip('Z')  # Remove trailing Z if present
            if len(rev) >= 8:
                version = f"{rev[0:4]}-{rev[4:6]}-{rev[6:8]}"
            else:
                version = rev

        return {
            'name': mib_name,
            'version': version,
            'oid': oid_match.group(1).strip() if oid_match else None,
            'description': description_match.group(1) if description_match else None,
            'imports': imports if imports else None,
            'objects': objects if objects else None,
            'content': content,
            'file_path': str(file_path)
        }

    def process_snmp_file(self, file_path: Path) -> int:
        """Process an SNMP MIB file and store it in the database."""
        snmp_mib = self.parse_snmp_file(file_path)

        metadata = {
            'oid': snmp_mib['oid'],
            'description': snmp_mib['description'],
            'imports': snmp_mib['imports'],
            'objects': snmp_mib['objects'],
            'file_path': snmp_mib['file_path']
        }

        return self.db.insert_parsed_data(
            data_type='snmp',
            name=snmp_mib['name'],
            version=snmp_mib['version'],
            data=snmp_mib['content'],
            metadata=metadata
        )

    def process_snmp_directory(self, dir_path: Path) -> List[int]:
        """Process all MIB files in a directory."""
        results = []

        for file_path in dir_path.glob('*'):
            if file_path.suffix in ['.mib', '.txt']:
                try:
                    result_id = self.process_snmp_file(file_path)
                    results.append(result_id)
                    print(f"Processed SNMP MIB file: {file_path.name} (ID: {result_id})")
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")

        return results
