"""YANG file parser for extracting and storing YANG module data."""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from .database import DatabaseManager


class YangParser:
    """Parser for YANG files."""

    def __init__(self, db: DatabaseManager):
        """Initialize with database manager."""
        self.db = db

    def parse_yang_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a YANG file and extract metadata."""
        content = file_path.read_text(encoding='utf-8')
        file_name = file_path.stem

        # Extract basic YANG metadata using regex
        module_match = re.search(r'module\s+([^\s{]+)', content)
        revision_match = re.search(r'revision\s+"?([0-9-]+)"?', content)
        namespace_match = re.search(r'namespace\s+"([^"]+)"', content)
        prefix_match = re.search(r'prefix\s+"?([^\s";]+)"?', content)
        description_match = re.search(r'description\s+"([^"]+)"', content)

        # Extract imports
        import_matches = re.finditer(r'import\s+([^\s{]+)', content)
        imports = [match.group(1) for match in import_matches]

        module_name = module_match.group(1) if module_match else file_name
        version = revision_match.group(1) if revision_match else "1.0.0"

        return {
            'name': module_name,
            'version': version,
            'namespace': namespace_match.group(1) if namespace_match else None,
            'prefix': prefix_match.group(1) if prefix_match else None,
            'description': description_match.group(1) if description_match else None,
            'imports': imports if imports else None,
            'content': content,
            'file_path': str(file_path)
        }

    def process_yang_file(self, file_path: Path) -> int:
        """Process a YANG file and store it in the database."""
        yang_module = self.parse_yang_file(file_path)

        metadata = {
            'namespace': yang_module['namespace'],
            'prefix': yang_module['prefix'],
            'description': yang_module['description'],
            'imports': yang_module['imports'],
            'file_path': yang_module['file_path']
        }

        return self.db.insert_parsed_data(
            data_type='yang',
            name=yang_module['name'],
            version=yang_module['version'],
            data=yang_module['content'],
            metadata=metadata
        )

    def process_yang_directory(self, dir_path: Path) -> List[int]:
        """Process all YANG files in a directory."""
        results = []
        
        for file_path in dir_path.glob('*.yang'):
            try:
                result_id = self.process_yang_file(file_path)
                results.append(result_id)
                print(f"Processed YANG file: {file_path.name} (ID: {result_id})")
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        return results
