from google.adk import Agent
from backend.tools.mcp_client import mcp_toolset
from backend import config

report_agent = Agent(
    model=config.GEMINI_MODEL,
    name="report_agent",
    description="Synthesizes analysis findings into the final report via MCP.",
    instruction="""You are the Boardroom AI Report Agent.
Your role is to aggregate findings from the Revenue Agent, Customer Agent, and Risk Agent.
When given these three sets of findings, you must:
1. Call the `generate_artifact` tool passing the three findings as parameters (`revenue_findings`, `customer_findings`, and `risk_findings`).
2. Polish the output report, filling in any gaps with details from the findings.
3. Provide the final completed executive report.""",
    tools=[mcp_toolset],
    generate_content_config=config.get_agent_config()
)

