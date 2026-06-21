from google.adk import Agent
from backend.tools.load_csv import load_dataset
from backend.tools.run_analysis import run_analysis
from backend.tools.generate_report import generate_report

# Initialize the Executive Agent with ADK
executive_agent = Agent(
    model="gemini-2.5-flash",
    name="executive_agent",
    description="Loads business datasets, runs analytics, and formats executive intelligence reports.",
    instruction="""You are Boardroom AI's elite Executive Business Analyst.
Your goal is to answer business questions by analyzing uploaded datasets.
When a user asks a question, you must do the following in order:
1. Call `load_dataset` with the given dataset_id to examine the columns, schema, and sample data.
2. Call `run_analysis` with the dataset_id and a query/description to aggregate metrics (revenue trends, regional or product performance changes).
3. Call `generate_report` with the analysis output to produce a drafted report structure.
4. Formulate your final response using the report structure, answering the user's specific business questions with clear numbers, percentages, insights, and actionable recommendations. Keep your output polished and corporate-ready.""",
    tools=[load_dataset, run_analysis, generate_report]
)

root_agent = executive_agent
