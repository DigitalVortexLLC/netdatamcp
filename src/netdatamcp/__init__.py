"""NetData MCP - HTTP-based MCP server for YANG and SNMP MIB data management."""

__version__ = "1.0.0"

from .database import DatabaseManager
from .yang_parser import YangParser
from .snmp_parser import SnmpParser

# Lazy import server to avoid dependency issues when only using parsers/database
def __getattr__(name):
    if name == "mcp":
        from .server import mcp
        return mcp
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "DatabaseManager",
    "YangParser",
    "SnmpParser",
    "mcp",
]
