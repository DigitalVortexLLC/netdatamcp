"""Database manager for storing parsed YANG and SNMP MIB data."""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database for parsed network data."""

    def __init__(self, db_path: str = "data/netdata.db"):
        """Initialize database connection and schema."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS parsed_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                data TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(type, name, version)
            )
        """)
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_type_name ON parsed_data(type, name)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_version ON parsed_data(version)"
        )
        self.conn.commit()

    def insert_parsed_data(
        self,
        data_type: str,
        name: str,
        version: str,
        data: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Insert or replace parsed data entry."""
        cursor = self.conn.execute(
            """
            INSERT OR REPLACE INTO parsed_data (type, name, version, data, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (data_type, name, version, data, json.dumps(metadata))
        )
        self.conn.commit()
        return cursor.lastrowid

    def query_by_type(self, data_type: str) -> List[Dict[str, Any]]:
        """Query all entries by type (yang or snmp)."""
        cursor = self.conn.execute(
            "SELECT * FROM parsed_data WHERE type = ?",
            (data_type,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def query_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Query entries by name (supports partial matching)."""
        cursor = self.conn.execute(
            "SELECT * FROM parsed_data WHERE name LIKE ?",
            (f"%{name}%",)
        )
        return [dict(row) for row in cursor.fetchall()]

    def query_by_version(self, version: str) -> List[Dict[str, Any]]:
        """Query entries by version."""
        cursor = self.conn.execute(
            "SELECT * FROM parsed_data WHERE version = ?",
            (version,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def query_by_name_and_version(
        self, name: str, version: str
    ) -> Optional[Dict[str, Any]]:
        """Query specific entry by name and version."""
        cursor = self.conn.execute(
            "SELECT * FROM parsed_data WHERE name = ? AND version = ?",
            (name, version)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all parsed data entries."""
        cursor = self.conn.execute(
            "SELECT * FROM parsed_data ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_versions(self, name: str) -> List[str]:
        """Get all available versions for a specific module/MIB name."""
        cursor = self.conn.execute(
            "SELECT DISTINCT version FROM parsed_data WHERE name = ? ORDER BY version DESC",
            (name,)
        )
        return [row["version"] for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()
