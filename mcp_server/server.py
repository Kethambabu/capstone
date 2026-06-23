import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP
from backend.database.supabase import db_init

# Initialize FastMCP server
mcp = FastMCP("Boardroom MCP Server")

# Ensure database tables are initialized
db_init()

# Import capability tools to bind to the MCP decorators
from mcp_server.capabilities.query_data import query_data_tool
from mcp_server.capabilities.run_analysis import run_analysis_tool
from mcp_server.capabilities.generate_artifact import generate_artifact_tool
from mcp_server.capabilities.memory import memory_tool

@mcp.tool(name="query_data")
def query_data(dataset: str, filters: dict = None) -> dict:
    """Retrieve data records from an uploaded dataset, optionally applying filters."""
    return query_data_tool(dataset, filters)

@mcp.tool(name="run_analysis")
def run_analysis(analysis_type: str, dataset_name: str, question: str = "") -> dict:
    """Execute analysis (revenue, customer, or risk) on a dataset."""
    return run_analysis_tool(analysis_type, dataset_name, question)

@mcp.tool(name="generate_artifact")
def generate_artifact(revenue_findings: str, customer_findings: str, risk_findings: str) -> dict:
    """Generate final executive advisory report from analysis findings."""
    return generate_artifact_tool(revenue_findings, customer_findings, risk_findings)

@mcp.tool(name="memory")
def memory(action: str, category: str, key: str, data: dict = None) -> dict:
    """Store, retrieve, or search working, episodic, or semantic memory."""
    return memory_tool(action, category, key, data)

if __name__ == "__main__":
    mcp.run()
