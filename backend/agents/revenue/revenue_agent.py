from google.adk import Agent
from backend.tools.mcp_client import mcp_toolset
from backend import config

revenue_agent = Agent(
    model=config.GEMINI_MODEL,
    name="revenue_agent",
    description="Analyzes revenue growth, product splits, and regional dynamics via MCP.",
    instruction="""You are the Boardroom AI Revenue Agent.
Your role is to evaluate revenue patterns and growth metrics.
When asked a question:
1. Run revenue calculations using the `run_analysis` tool (with parameters: analysis_type='revenue', dataset_name='sales', question='your question').
2. Formulate a summary of the revenue metrics (including percentage drop or growth, worst performing regions, and worst performing product categories) based on the tool output.""",
    tools=[mcp_toolset],
    generate_content_config=config.get_agent_config()
)


