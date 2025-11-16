"""Side process for parsing YANG and SNMP MIB files."""
import sys
from pathlib import Path
from .database import DatabaseManager
from .yang_parser import YangParser
from .snmp_parser import SnmpParser


def main():
    """Process all YANG and SNMP MIB files."""
    # Get paths
    base_path = Path(__file__).parent.parent.parent
    yang_dir = base_path / "yang"
    mibs_dir = base_path / "mibs"
    db_path = base_path / "data" / "netdata.db"

    print("Starting file processing...")
    print(f"YANG directory: {yang_dir}")
    print(f"MIBs directory: {mibs_dir}")
    print(f"Database path: {db_path}")

    # Ensure directories exist
    yang_dir.mkdir(exist_ok=True)
    mibs_dir.mkdir(exist_ok=True)

    # Initialize database and parsers
    db = DatabaseManager(str(db_path))
    yang_parser = YangParser(db)
    snmp_parser = SnmpParser(db)

    try:
        # Process YANG files
        print("\nProcessing YANG files...")
        yang_results = yang_parser.process_yang_directory(yang_dir)
        print(f"Processed {len(yang_results)} YANG files")

        # Process SNMP MIB files
        print("\nProcessing SNMP MIB files...")
        snmp_results = snmp_parser.process_snmp_directory(mibs_dir)
        print(f"Processed {len(snmp_results)} SNMP MIB files")

        print("\nFile processing complete!")
        print(f"Total files processed: {len(yang_results) + len(snmp_results)}")
        
        return 0
    except Exception as e:
        print(f"Error during file processing: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
