"""Configuration settings for NetData MCP Server."""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration settings."""

    # Base directory
    BASE_DIR = Path(__file__).parent.parent.parent

    # Directories
    YANG_DIR = BASE_DIR / "yang"
    MIBS_DIR = BASE_DIR / "mibs"
    DATA_DIR = BASE_DIR / "data"

    # Database
    DB_PATH = DATA_DIR / "netdata.db"

    # Server settings
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "3000"))

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.YANG_DIR.mkdir(exist_ok=True)
        cls.MIBS_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)


# Ensure directories exist on import
Config.ensure_directories()
