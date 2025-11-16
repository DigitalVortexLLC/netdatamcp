"""HTTP-based MCP server for YANG and SNMP MIB data management."""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from .database import DatabaseManager


# Initialize FastMCP server
mcp = FastMCP("NetData MCP Server")

# Initialize database
db_path = Path(__file__).parent.parent.parent / "data" / "netdata.db"
db = DatabaseManager(str(db_path))


@mcp.tool()
def query_data(
    type: Optional[str] = None,
    name: Optional[str] = None,
    version: Optional[str] = None
) -> str:
    """
    Query parsed YANG/SNMP data from the database.
    
    Args:
        type: Filter by type ("yang" or "snmp")
        name: Search by name (supports partial matching)
        version: Filter by specific version
    
    Returns:
        JSON string with matching data entries
    """
    try:
        # Query based on provided parameters
        if type and name and version:
            result = db.query_by_name_and_version(name, version)
            if result and result.get('type') == type:
                return json.dumps([result], indent=2)
            return json.dumps([], indent=2)
        elif type:
            result = db.query_by_type(type)
        elif name:
            result = db.query_by_name(name)
        elif version:
            result = db.query_by_version(version)
        else:
            result = db.get_all_data()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def list_all_data() -> str:
    """
    List all parsed data entries in the database.
    
    Returns:
        JSON string with all data entries
    """
    try:
        result = db.get_all_data()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_versions(name: str) -> str:
    """
    Get all available versions for a specific module/MIB name.
    
    Args:
        name: Name of the module/MIB
    
    Returns:
        JSON string with list of versions
    """
    try:
        versions = db.get_versions(name)
        return json.dumps({"name": name, "versions": versions}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_statistics() -> str:
    """
    Get database statistics including counts of YANG and SNMP entries.
    
    Returns:
        JSON string with statistics
    """
    try:
        all_data = db.get_all_data()
        yang_count = sum(1 for d in all_data if d['type'] == 'yang')
        snmp_count = sum(1 for d in all_data if d['type'] == 'snmp')
        
        stats = {
            "total": len(all_data),
            "yang": yang_count,
            "snmp": snmp_count
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Resource endpoint to get raw data
@mcp.resource("db://all")
def get_all_database_data() -> str:
    """Get all database data as a resource."""
    return json.dumps(db.get_all_data(), indent=2)


@mcp.resource("db://stats")
def get_database_stats() -> str:
    """Get database statistics as a resource."""
    all_data = db.get_all_data()
    yang_count = sum(1 for d in all_data if d['type'] == 'yang')
    snmp_count = sum(1 for d in all_data if d['type'] == 'snmp')
    
    stats = {
        "total": len(all_data),
        "yang": yang_count,
        "snmp": snmp_count
    }
    return json.dumps(stats, indent=2)
