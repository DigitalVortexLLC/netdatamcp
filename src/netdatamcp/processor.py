"""Side process for parsing YANG and SNMP MIB files."""
import sys
from pathlib import Path
from .database import DatabaseManager
from .yang_parser import YangParser
from .snmp_parser import SnmpParser
from .config import Config


def main():
    """Process all YANG and SNMP MIB files."""
    print("Starting file processing...")
    print(f"YANG directory: {Config.YANG_DIR}")
    print(f"MIBs directory: {Config.MIBS_DIR}")
    print(f"Database path: {Config.DB_PATH}")

    # Ensure directories exist
    Config.ensure_directories()

    # Initialize database and parsers
    db = DatabaseManager(str(Config.DB_PATH))
    yang_parser = YangParser(db)
    snmp_parser = SnmpParser(db)

    try:
        # Process YANG files
        print("\nProcessing YANG files...")
        yang_results = yang_parser.process_yang_directory(Config.YANG_DIR)
        print(f"Processed {len(yang_results)} YANG files")

        # Process SNMP MIB files
        print("\nProcessing SNMP MIB files...")
        snmp_results = snmp_parser.process_snmp_directory(Config.MIBS_DIR)
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
