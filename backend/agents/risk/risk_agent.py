from google.adk import Agent
from backend.tools.mcp_client import mcp_toolset
from backend import config

risk_agent = Agent(
    model=config.GEMINI_MODEL,
    name="risk_agent",
    description="Detects anomalous patterns, drops, and business risks via MCP.",
    instruction="""You are the Boardroom AI Risk Agent.
Your role is to identify critical anomalies and declines in business datasets.
When invoked:
1. Run anomaly metrics using the `run_analysis` tool (with parameters: analysis_type='risk', dataset_name='sales').
2. Summarize any active risk alerts (such as MoM decline exceedances) based on the tool output.""",
    tools=[mcp_toolset],
    generate_content_config=config.get_agent_config()
)


