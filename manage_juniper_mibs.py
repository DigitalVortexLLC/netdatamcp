#!/usr/bin/env python3
"""
Juniper SNMP MIB Manager

This script downloads, extracts, and manages Juniper SNMP MIBs from the
Juniper MIB Explorer (https://apps.juniper.net/mib-explorer/).

Usage:
    python manage_juniper_mibs.py [options]

Options:
    --download          Download MIB archives for configured products/versions
    --extract           Extract downloaded MIB archives
    --product <name>    Only process specific product (e.g., --product junos)
    --version <ver>     Only download specific version (e.g., --version 24.2R1)
    --clean             Remove downloaded archives and extracted MIBs
    --list              List all configured products and versions
    --interactive       Interactive mode to select products and versions
    --help              Show this help message
"""

import argparse
import logging
import os
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install it with: pip install requests")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JuniperMIBManager:
    """Manages Juniper SNMP MIB downloads and organization"""

    def __init__(self, config_path: str = "juniper_mibs.yaml"):
        """Initialize the Juniper MIB manager

        Args:
            config_path: Path to the Juniper MIBs configuration file
        """
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / config_path
        self.config = self._load_config()

        # Get settings from config
        settings = self.config.get('settings', {})

        # Set up directories
        self.download_dir = self.base_dir / settings.get('download_dir', 'downloads/juniper_mibs')
        self.target_dir = self.base_dir / settings.get('target_dir', 'mibs/juniper')

        # Get other settings
        self.organize_by_version = settings.get('organize_by_version', True)
        self.file_patterns = settings.get('file_patterns', ['*.mib', '*.txt', '*.my'])
        self.auto_process = settings.get('auto_process', True)
        self.cleanup_archives = settings.get('cleanup_archives', False)

        # Ensure directories exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load Juniper MIB configuration from YAML file"""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            logger.error("Please create juniper_mibs.yaml with your desired configuration")
            sys.exit(1)

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)

    def list_products(self):
        """List all configured products and versions"""
        products = self.config.get('juniper_mibs', {})

        logger.info("Configured Juniper MIB Products:")
        logger.info("=" * 70)

        for product_id, product_info in products.items():
            status = "✓ Enabled" if product_info.get('enabled', True) else "✗ Disabled"
            logger.info(f"\n  Product: {product_id}")
            logger.info(f"    Name: {product_info.get('name', 'Unknown')}")
            logger.info(f"    Status: {status}")
            logger.info(f"    Description: {product_info.get('description', 'N/A')}")
            logger.info(f"    Download URL: {product_info.get('download_url', 'N/A')}")

            versions = product_info.get('versions', [])
            if versions:
                logger.info(f"    Versions: {', '.join(versions)}")
            else:
                logger.info(f"    Versions: None configured")

        logger.info("\n" + "=" * 70)

    def _download_file(self, url: str, dest_path: Path, timeout: int = 300) -> bool:
        """Download a file from URL to destination path

        Args:
            url: URL to download from
            dest_path: Destination file path
            timeout: Download timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading from: {url}")
            logger.info(f"Saving to: {dest_path}")

            # Create parent directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Download with streaming to handle large files
            response = requests.get(url, stream=True, timeout=timeout, allow_redirects=True)
            response.raise_for_status()

            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))

            # Write to file
            with open(dest_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Show progress
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                logger.debug(f"  Progress: {percent:.1f}%")

            logger.info(f"✓ Successfully downloaded: {dest_path.name}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return False

    def _extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract a tar.gz or zip archive

        Args:
            archive_path: Path to the archive file
            extract_to: Directory to extract files to

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Extracting: {archive_path.name}")
            extract_to.mkdir(parents=True, exist_ok=True)

            # Determine archive type and extract
            if archive_path.suffix == '.zip' or archive_path.name.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix == '.gz' or archive_path.name.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
            elif archive_path.suffix == '.tar':
                with tarfile.open(archive_path, 'r:') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                logger.warning(f"Unknown archive format: {archive_path}")
                return False

            logger.info(f"✓ Successfully extracted to: {extract_to}")
            return True

        except Exception as e:
            logger.error(f"Failed to extract {archive_path}: {e}")
            return False

    def _copy_mib_files(self, source_dir: Path, dest_dir: Path, product_id: str, version: str) -> int:
        """Copy MIB files from extracted directory to target directory

        Args:
            source_dir: Source directory containing extracted MIBs
            dest_dir: Destination directory for organized MIBs
            product_id: Product identifier
            version: Version string

        Returns:
            Number of files copied
        """
        count = 0

        try:
            # Create destination directory structure
            if self.organize_by_version:
                dest_path = dest_dir / product_id / version
            else:
                dest_path = dest_dir / product_id

            dest_path.mkdir(parents=True, exist_ok=True)

            # Find and copy all MIB files matching patterns
            for pattern in self.file_patterns:
                for mib_file in source_dir.glob(f"**/{pattern}"):
                    if mib_file.is_file():
                        # Get relative path to preserve directory structure
                        try:
                            rel_path = mib_file.relative_to(source_dir)
                            dest_file = dest_path / rel_path.name  # Just use filename, not full path

                            # Copy the file
                            shutil.copy2(mib_file, dest_file)
                            count += 1
                            logger.debug(f"  Copied: {mib_file.name}")
                        except Exception as e:
                            logger.warning(f"  Error copying {mib_file}: {e}")

            return count

        except Exception as e:
            logger.error(f"Error copying MIB files: {e}")
            return count

    def download_product_mibs(self, product_id: str, product_info: Dict,
                             specific_version: Optional[str] = None) -> bool:
        """Download MIBs for a specific product

        Args:
            product_id: Product identifier
            product_info: Product configuration
            specific_version: Only download this version if specified

        Returns:
            True if at least one version was downloaded successfully
        """
        product_name = product_info.get('name', product_id)
        download_url_template = product_info.get('download_url')
        versions = product_info.get('versions', [])

        if not download_url_template:
            logger.error(f"No download URL configured for {product_name}")
            return False

        if not versions:
            logger.warning(f"No versions configured for {product_name}")
            return False

        # Filter to specific version if requested
        if specific_version:
            if specific_version not in versions:
                logger.error(f"Version {specific_version} not configured for {product_name}")
                return False
            versions = [specific_version]

        success = False

        for version in versions:
            logger.info(f"\nDownloading {product_name} MIBs - Version {version}")
            logger.info("-" * 60)

            # Build download URL
            download_url = download_url_template.format(version=version)

            # Determine archive filename
            archive_name = f"{product_id}_{version}_mibs.tar.gz"
            archive_path = self.download_dir / product_id / archive_name

            # Download the archive
            if self._download_file(download_url, archive_path):
                success = True

                # Extract if download was successful
                extract_dir = self.download_dir / product_id / version
                if self._extract_archive(archive_path, extract_dir):
                    # Copy MIB files to target directory
                    copied = self._copy_mib_files(extract_dir, self.target_dir,
                                                  product_id, version)
                    logger.info(f"✓ Copied {copied} MIB files to {self.target_dir}")

                    # Cleanup if configured
                    if self.cleanup_archives:
                        logger.info(f"Cleaning up archive: {archive_path}")
                        archive_path.unlink()
                        shutil.rmtree(extract_dir)
            else:
                logger.warning(f"Failed to download {product_name} v{version}")

        return success

    def download_all_products(self, specific_product: Optional[str] = None,
                             specific_version: Optional[str] = None):
        """Download MIBs for all enabled products

        Args:
            specific_product: Only download this product if specified
            specific_version: Only download this version if specified
        """
        products = self.config.get('juniper_mibs', {})

        logger.info("Starting Juniper MIB download...")
        logger.info("=" * 70)

        success_count = 0
        fail_count = 0

        for product_id, product_info in products.items():
            # Skip if specific product requested and this isn't it
            if specific_product and product_id != specific_product:
                continue

            # Skip disabled products
            if not product_info.get('enabled', True):
                logger.info(f"Skipping disabled product: {product_id}")
                continue

            if self.download_product_mibs(product_id, product_info, specific_version):
                success_count += 1
            else:
                fail_count += 1

        logger.info("\n" + "=" * 70)
        logger.info(f"Download complete: {success_count} successful, {fail_count} failed")

        # Suggest next steps
        if success_count > 0:
            logger.info("\nNext steps:")
            logger.info(f"  1. MIB files are in: {self.target_dir}")
            if self.auto_process:
                logger.info("  2. Run './process_files.sh' to parse MIBs into the database")
                logger.info("  3. Start the MCP server with './start_server.sh'")

    def clean_mibs(self, specific_product: Optional[str] = None):
        """Remove downloaded archives and extracted MIBs

        Args:
            specific_product: Only clean this product if specified
        """
        if specific_product:
            # Clean specific product
            download_path = self.download_dir / specific_product
            target_path = self.target_dir / specific_product

            if download_path.exists():
                logger.info(f"Removing downloads: {download_path}")
                shutil.rmtree(download_path)

            if target_path.exists():
                logger.info(f"Removing MIBs: {target_path}")
                shutil.rmtree(target_path)
        else:
            # Clean all
            if self.download_dir.exists():
                logger.info(f"Removing all downloads: {self.download_dir}")
                shutil.rmtree(self.download_dir)
                self.download_dir.mkdir(parents=True, exist_ok=True)

            if self.target_dir.exists():
                logger.info(f"Removing all MIBs: {self.target_dir}")
                shutil.rmtree(self.target_dir)
                self.target_dir.mkdir(parents=True, exist_ok=True)

    def interactive_mode(self):
        """Interactive mode to select products and versions"""
        products = self.config.get('juniper_mibs', {})

        print("\n" + "=" * 70)
        print("Juniper MIB Manager - Interactive Mode")
        print("=" * 70)

        # List available products
        print("\nAvailable Products:")
        product_list = []
        for idx, (product_id, product_info) in enumerate(products.items(), 1):
            if product_info.get('enabled', True):
                product_list.append((product_id, product_info))
                print(f"  {idx}. {product_info.get('name', product_id)} ({product_id})")

        if not product_list:
            print("No enabled products found in configuration.")
            return

        # Select product
        try:
            choice = input("\nSelect product number (or 'all' for all products): ").strip()

            if choice.lower() == 'all':
                selected_product = None
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(product_list):
                    selected_product = product_list[idx][0]
                else:
                    print("Invalid selection.")
                    return
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return

        # Select version if specific product chosen
        selected_version = None
        if selected_product:
            product_info = products[selected_product]
            versions = product_info.get('versions', [])

            if versions:
                print(f"\nAvailable Versions for {product_info.get('name')}:")
                for idx, version in enumerate(versions, 1):
                    print(f"  {idx}. {version}")

                try:
                    ver_choice = input("\nSelect version number (or 'all' for all versions): ").strip()

                    if ver_choice.lower() != 'all':
                        idx = int(ver_choice) - 1
                        if 0 <= idx < len(versions):
                            selected_version = versions[idx]
                        else:
                            print("Invalid selection.")
                            return
                except (ValueError, KeyboardInterrupt):
                    print("\nCancelled.")
                    return

        # Confirm and download
        print("\n" + "-" * 70)
        print("Download Summary:")
        print(f"  Product: {selected_product if selected_product else 'All products'}")
        print(f"  Version: {selected_version if selected_version else 'All versions'}")
        print("-" * 70)

        try:
            confirm = input("\nProceed with download? [y/N]: ").strip().lower()
            if confirm == 'y':
                self.download_all_products(selected_product, selected_version)
            else:
                print("Cancelled.")
        except KeyboardInterrupt:
            print("\nCancelled.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage Juniper SNMP MIB downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured products and versions
  python manage_juniper_mibs.py --list

  # Interactive mode (recommended for first time)
  python manage_juniper_mibs.py --interactive

  # Download all configured MIBs
  python manage_juniper_mibs.py --download

  # Download only Junos MIBs
  python manage_juniper_mibs.py --download --product junos

  # Download specific version
  python manage_juniper_mibs.py --download --product junos --version 24.2R1

  # Clean downloaded files and MIBs
  python manage_juniper_mibs.py --clean

  # Clean and re-download
  python manage_juniper_mibs.py --clean --download

Note:
  The download URLs in juniper_mibs.yaml may need to be adjusted based on
  the actual Juniper MIB Explorer structure. Check the website at:
  https://apps.juniper.net/mib-explorer/download
        """
    )

    parser.add_argument('--download', action='store_true',
                        help='Download MIB archives for configured products')
    parser.add_argument('--product', type=str,
                        help='Only process specific product (e.g., junos)')
    parser.add_argument('--version', type=str,
                        help='Only download specific version (e.g., 24.2R1)')
    parser.add_argument('--clean', action='store_true',
                        help='Remove downloaded archives and extracted MIBs')
    parser.add_argument('--list', action='store_true',
                        help='List all configured products and versions')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive mode to select products and versions')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create manager
    try:
        manager = JuniperMIBManager()
    except Exception as e:
        logger.error(f"Failed to initialize manager: {e}")
        sys.exit(1)

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Execute requested operations
    if args.list:
        manager.list_products()

    if args.interactive:
        manager.interactive_mode()

    if args.clean:
        manager.clean_mibs(specific_product=args.product)

    if args.download:
        manager.download_all_products(
            specific_product=args.product,
            specific_version=args.version
        )


if __name__ == '__main__':
    main()
