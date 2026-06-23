from google.adk import Agent
from backend.tools.mcp_client import mcp_toolset
from backend import config

customer_agent = Agent(
    model=config.GEMINI_MODEL,
    name="customer_agent",
    description="Analyzes customer segmentation, retention, and churn rates via MCP.",
    instruction="""You are the Boardroom AI Customer Agent.
Your role is to assess customer churn rates and segmentation.
When invoked:
1. Load the customer dataset (usually 'customers') using the `query_data` tool.
2. Run churn metrics using the `run_analysis` tool (with parameters: analysis_type='customer', dataset_name='customers').
3. Summarize the findings (e.g. overall churn rate, high-risk customer segments).""",
    tools=[mcp_toolset],
    generate_content_config=config.get_agent_config()
)

