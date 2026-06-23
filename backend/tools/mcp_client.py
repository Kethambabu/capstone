import sys
from pathlib import Path
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

# Resolve absolute path to project root
project_root = Path(__file__).resolve().parent.parent.parent
server_script_path = str(project_root / "mcp_server" / "server.py")

# Configure Stdio server parameters to spawn the FastMCP Python script
server_params = StdioServerParameters(
    command=sys.executable,
    args=[server_script_path]
)

# Connect over stdio connection parameters
connection_params = StdioConnectionParams(server_params=server_params, timeout=15.0)

# Instantiate the McpToolset
mcp_toolset = McpToolset(connection_params=connection_params)
