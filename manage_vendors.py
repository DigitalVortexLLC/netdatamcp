#!/usr/bin/env python3
"""
Vendor YANG Model Repository Manager

This script manages vendor YANG model repositories by cloning, updating,
and processing YANG files from multiple vendor sources into the MCP server.

Usage:
    python manage_vendors.py [options]

Options:
    --sync              Sync (clone/pull) all enabled vendor repositories
    --process           Process YANG files from vendor repos into the database
    --vendor <name>     Only process specific vendor (e.g., --vendor nokia)
    --clean             Remove vendor repositories before syncing
    --list              List all configured vendors
    --help              Show this help message
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VendorManager:
    """Manages vendor YANG model repositories"""

    def __init__(self, config_path: str = "vendors.yaml"):
        """Initialize the vendor manager

        Args:
            config_path: Path to the vendors configuration file
        """
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / config_path
        self.vendors_dir = self.base_dir / "vendors"
        self.yang_dir = self.base_dir / "yang"
        self.config = self._load_config()

        # Ensure directories exist
        self.vendors_dir.mkdir(exist_ok=True)
        self.yang_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict:
        """Load vendor configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('vendors', {})
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)

    def list_vendors(self):
        """List all configured vendors"""
        logger.info("Configured Vendors:")
        logger.info("-" * 60)

        for vendor_id, vendor_info in self.config.items():
            status = "✓ Enabled" if vendor_info.get('enabled', True) else "✗ Disabled"
            logger.info(f"  {vendor_id}: {vendor_info.get('name', 'Unknown')}")
            logger.info(f"    Status: {status}")
            logger.info(f"    Repo: {vendor_info.get('repo_url', 'N/A')}")
            logger.info(f"    Description: {vendor_info.get('description', 'N/A')}")
            logger.info("")

    def _run_git_command(self, cmd: List[str], cwd: Path) -> bool:
        """Run a git command and return success status

        Args:
            cmd: Git command and arguments
            cwd: Working directory for the command

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            return False

    def sync_vendor(self, vendor_id: str, vendor_info: Dict) -> bool:
        """Sync a vendor repository (clone or pull)

        Args:
            vendor_id: Vendor identifier
            vendor_info: Vendor configuration

        Returns:
            True if successful, False otherwise
        """
        vendor_name = vendor_info.get('name', vendor_id)
        repo_url = vendor_info.get('repo_url')
        branch = vendor_info.get('branch', 'master')

        if not repo_url:
            logger.error(f"No repository URL configured for {vendor_name}")
            return False

        vendor_path = self.vendors_dir / vendor_id

        # Clone if doesn't exist, otherwise pull
        if not vendor_path.exists():
            logger.info(f"Cloning {vendor_name} repository...")
            if not self._run_git_command(
                ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, str(vendor_path)],
                self.vendors_dir
            ):
                return False
            logger.info(f"✓ Successfully cloned {vendor_name}")
        else:
            logger.info(f"Updating {vendor_name} repository...")
            if not self._run_git_command(['git', 'fetch', 'origin', branch], vendor_path):
                return False
            if not self._run_git_command(['git', 'reset', '--hard', f'origin/{branch}'], vendor_path):
                return False
            logger.info(f"✓ Successfully updated {vendor_name}")

        return True

    def sync_all_vendors(self, specific_vendor: Optional[str] = None, clean: bool = False):
        """Sync all enabled vendor repositories

        Args:
            specific_vendor: Only sync this vendor if specified
            clean: Remove existing vendor directories before syncing
        """
        logger.info("Starting vendor repository sync...")
        logger.info("=" * 60)

        if clean and self.vendors_dir.exists():
            logger.info("Cleaning vendor directories...")
            shutil.rmtree(self.vendors_dir)
            self.vendors_dir.mkdir(exist_ok=True)

        success_count = 0
        fail_count = 0

        for vendor_id, vendor_info in self.config.items():
            # Skip if specific vendor requested and this isn't it
            if specific_vendor and vendor_id != specific_vendor:
                continue

            # Skip disabled vendors
            if not vendor_info.get('enabled', True):
                logger.info(f"Skipping disabled vendor: {vendor_id}")
                continue

            if self.sync_vendor(vendor_id, vendor_info):
                success_count += 1
            else:
                fail_count += 1

        logger.info("=" * 60)
        logger.info(f"Sync complete: {success_count} successful, {fail_count} failed")

    def process_vendor_yang_files(self, vendor_id: str, vendor_info: Dict) -> int:
        """Process YANG files from a vendor repository

        Args:
            vendor_id: Vendor identifier
            vendor_info: Vendor configuration

        Returns:
            Number of files processed
        """
        vendor_name = vendor_info.get('name', vendor_id)
        vendor_path = self.vendors_dir / vendor_id

        if not vendor_path.exists():
            logger.error(f"Vendor repository not found: {vendor_path}")
            logger.error(f"Run with --sync first to clone the repository")
            return 0

        yang_paths = vendor_info.get('yang_paths', ['**/*.yang'])
        processed_count = 0

        logger.info(f"Processing YANG files for {vendor_name}...")

        # Create vendor subdirectory in yang/
        vendor_yang_dir = self.yang_dir / vendor_id
        vendor_yang_dir.mkdir(exist_ok=True)

        # Process each configured path pattern
        for path_pattern in yang_paths:
            logger.info(f"  Searching pattern: {path_pattern}")
            yang_files = list(vendor_path.glob(path_pattern))

            for yang_file in yang_files:
                try:
                    # Create relative path structure to preserve vendor organization
                    rel_path = yang_file.relative_to(vendor_path)
                    dest_file = vendor_yang_dir / rel_path

                    # Create parent directories if needed
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy the YANG file
                    shutil.copy2(yang_file, dest_file)
                    processed_count += 1
                    logger.debug(f"    Copied: {rel_path}")

                except Exception as e:
                    logger.error(f"    Error processing {yang_file}: {e}")

        logger.info(f"✓ Processed {processed_count} YANG files from {vendor_name}")
        return processed_count

    def process_all_vendors(self, specific_vendor: Optional[str] = None):
        """Process YANG files from all enabled vendors

        Args:
            specific_vendor: Only process this vendor if specified
        """
        logger.info("Starting YANG file processing...")
        logger.info("=" * 60)

        total_processed = 0

        for vendor_id, vendor_info in self.config.items():
            # Skip if specific vendor requested and this isn't it
            if specific_vendor and vendor_id != specific_vendor:
                continue

            # Skip disabled vendors
            if not vendor_info.get('enabled', True):
                logger.info(f"Skipping disabled vendor: {vendor_id}")
                continue

            count = self.process_vendor_yang_files(vendor_id, vendor_info)
            total_processed += count

        logger.info("=" * 60)
        logger.info(f"Processing complete: {total_processed} total YANG files processed")

        # Suggest running the processor
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run './process_files.sh' to parse YANG files into the database")
        logger.info("  2. Start the MCP server with './start_server.sh'")

    def clean_vendor(self, vendor_id: str):
        """Remove a vendor's repository and YANG files

        Args:
            vendor_id: Vendor identifier to clean
        """
        vendor_path = self.vendors_dir / vendor_id
        vendor_yang_path = self.yang_dir / vendor_id

        if vendor_path.exists():
            logger.info(f"Removing vendor repository: {vendor_path}")
            shutil.rmtree(vendor_path)

        if vendor_yang_path.exists():
            logger.info(f"Removing vendor YANG files: {vendor_yang_path}")
            shutil.rmtree(vendor_yang_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage vendor YANG model repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured vendors
  python manage_vendors.py --list

  # Sync all vendor repositories
  python manage_vendors.py --sync

  # Sync only Nokia repository
  python manage_vendors.py --sync --vendor nokia

  # Process YANG files from all vendors
  python manage_vendors.py --process

  # Full workflow: sync and process
  python manage_vendors.py --sync --process

  # Clean and re-sync all vendors
  python manage_vendors.py --clean --sync --process
        """
    )

    parser.add_argument('--sync', action='store_true',
                        help='Sync (clone/pull) vendor repositories')
    parser.add_argument('--process', action='store_true',
                        help='Process YANG files into yang/ directory')
    parser.add_argument('--vendor', type=str,
                        help='Only process specific vendor (e.g., nokia)')
    parser.add_argument('--clean', action='store_true',
                        help='Remove vendor repositories before syncing')
    parser.add_argument('--list', action='store_true',
                        help='List all configured vendors')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create manager
    manager = VendorManager()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Execute requested operations
    if args.list:
        manager.list_vendors()

    if args.sync:
        manager.sync_all_vendors(specific_vendor=args.vendor, clean=args.clean)

    if args.process:
        manager.process_all_vendors(specific_vendor=args.vendor)


if __name__ == '__main__':
    main()
