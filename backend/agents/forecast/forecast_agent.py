from google.adk import Agent
from backend.tools.mcp_client import mcp_toolset
from backend import config

forecast_agent = Agent(
    model=config.GEMINI_MODEL,
    name="forecast_agent",
    description="Estimates future growth trends and calculates forecasting metrics via MCP.",
    instruction="""You are the Boardroom AI Forecast Agent.
Your role is to run forecasts on business datasets.
When invoked:
1. Load dataset records via the `query_data` tool.
2. Calculate future values based on past monthly revenue trends.
3. Formulate and output the forecast growth percentage (e.g. 8.2%) and a confidence score (e.g. 91%).""",
    tools=[mcp_toolset],
    generate_content_config=config.get_agent_config()
)

