import uuid
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from backend.agents.revenue.revenue_agent import revenue_agent
from backend.agents.customer.customer_agent import customer_agent
from backend.agents.risk.risk_agent import risk_agent
from backend.agents.report.report_agent import report_agent
from backend.tools.report_tools import generate_report

async def ask_revenue_agent(question: str) -> str:
    """
    Queries the Revenue Agent for revenue, growth, and product category analysis.
    
    Args:
        question: The business question to ask the Revenue Agent (e.g. 'Why did revenue drop in May?').
        
    Returns:
        The analysis report from the Revenue Agent.
    """
    from backend.services.agentops_service import run_agent_with_ops
    
    async def run_rev():
        runner = InMemoryRunner(agent=revenue_agent, app_name="revenue_sub_app")
        session_id = f"rev_{uuid.uuid4().hex[:8]}"
        await runner.session_service.create_session(app_name="revenue_sub_app", user_id="system", session_id=session_id)
        
        content = types.Content(role="user", parts=[types.Part.from_text(text=question)])
        response_text = ""
        async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
            if event.is_final_response() and event.content:
                parts = event.content.parts
                if isinstance(parts, list):
                    response_text = "".join(part.text for part in parts if part.text)
                elif hasattr(parts, 'text'):
                    response_text = parts.text
                else:
                    response_text = str(parts)
        if not response_text:
            raise ValueError("No final response text received from Revenue Agent.")
        from backend.services.token_manager import track_agent_tokens
        track_agent_tokens("revenue_agent", question, response_text)
        return response_text

    from backend.services.gemini_client_service import execute_with_retry
    try:
        async def run_rev_wrapped():
            return await run_agent_with_ops("revenue_agent", run_rev)
        return await execute_with_retry(run_rev_wrapped)
    except Exception as e:
        print(f"Error in ask_revenue_agent: {e}.")
        raise e

async def ask_customer_agent(question: str) -> str:
    """
    Queries the Customer Agent for customer segments and churn analysis.
    
    Args:
        question: The request/query to ask the Customer Agent (e.g. 'Analyze customer segments').
        
    Returns:
        The customer segment analysis from the Customer Agent.
    """
    from backend.services.agentops_service import run_agent_with_ops

    async def run_cust():
        runner = InMemoryRunner(agent=customer_agent, app_name="customer_sub_app")
        session_id = f"cust_{uuid.uuid4().hex[:8]}"
        await runner.session_service.create_session(app_name="customer_sub_app", user_id="system", session_id=session_id)
        
        content = types.Content(role="user", parts=[types.Part.from_text(text=question)])
        response_text = ""
        async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
            if event.is_final_response() and event.content:
                parts = event.content.parts
                if isinstance(parts, list):
                    response_text = "".join(part.text for part in parts if part.text)
                elif hasattr(parts, 'text'):
                    response_text = parts.text
                else:
                    response_text = str(parts)
        if not response_text:
            raise ValueError("No final response text received from Customer Agent.")
        from backend.services.token_manager import track_agent_tokens
        track_agent_tokens("customer_agent", question, response_text)
        return response_text

    from backend.services.gemini_client_service import execute_with_retry
    try:
        async def run_cust_wrapped():
            return await run_agent_with_ops("customer_agent", run_cust)
        return await execute_with_retry(run_cust_wrapped)
    except Exception as e:
        print(f"Error in ask_customer_agent: {e}.")
        raise e

async def ask_risk_agent(question: str) -> str:
    """
    Queries the Risk Agent for business risks and anomaly alerts.
    
    Args:
        question: The request/query to ask the Risk Agent (e.g. 'Identify anomalies').
        
    Returns:
        The risk detection report from the Risk Agent.
    """
    from backend.services.agentops_service import run_agent_with_ops

    async def run_risk():
        runner = InMemoryRunner(agent=risk_agent, app_name="risk_sub_app")
        session_id = f"risk_{uuid.uuid4().hex[:8]}"
        await runner.session_service.create_session(app_name="risk_sub_app", user_id="system", session_id=session_id)
        
        content = types.Content(role="user", parts=[types.Part.from_text(text=question)])
        response_text = ""
        async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
            if event.is_final_response() and event.content:
                parts = event.content.parts
                if isinstance(parts, list):
                    response_text = "".join(part.text for part in parts if part.text)
                elif hasattr(parts, 'text'):
                    response_text = parts.text
                else:
                    response_text = str(parts)
        if not response_text:
            raise ValueError("No final response text received from Risk Agent.")
        from backend.services.token_manager import track_agent_tokens
        track_agent_tokens("risk_agent", question, response_text)
        return response_text

    from backend.services.gemini_client_service import execute_with_retry
    try:
        async def run_risk_wrapped():
            return await run_agent_with_ops("risk_agent", run_risk)
        return await execute_with_retry(run_risk_wrapped)
    except Exception as e:
        print(f"Error in ask_risk_agent: {e}.")
        raise e

async def ask_report_agent(revenue_findings: str, customer_findings: str, risk_findings: str) -> str:
    """
    Queries the Report Agent to compile findings into the final executive report.
    
    Args:
        revenue_findings: The findings returned by the Revenue Agent.
        customer_findings: The findings returned by the Customer Agent.
        risk_findings: The findings returned by the Risk Agent.
        
    Returns:
        The compiled executive report.
    """
    from backend.services.agentops_service import run_agent_with_ops

    async def run_rep():
        runner = InMemoryRunner(agent=report_agent, app_name="report_sub_app")
        session_id = f"rep_{uuid.uuid4().hex[:8]}"
        await runner.session_service.create_session(app_name="report_sub_app", user_id="system", session_id=session_id)
        
        prompt = f"Revenue findings: {revenue_findings}\nCustomer findings: {customer_findings}\nRisk findings: {risk_findings}"
        content = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        response_text = ""
        async for event in runner.run_async(user_id="system", session_id=session_id, new_message=content):
            if event.is_final_response() and event.content:
                parts = event.content.parts
                if isinstance(parts, list):
                    response_text = "".join(part.text for part in parts if part.text)
                elif hasattr(parts, 'text'):
                    response_text = parts.text
                else:
                    response_text = str(parts)
        if not response_text:
            raise ValueError("No final response text received from Report Agent.")
        from backend.services.token_manager import track_agent_tokens
        track_agent_tokens("report_agent", prompt, response_text)
        return response_text

    from backend.services.gemini_client_service import execute_with_retry
    try:
        async def run_rep_wrapped():
            return await run_agent_with_ops("report_agent", run_rep)
        return await execute_with_retry(run_rep_wrapped)
    except Exception as e:
        print(f"Error in ask_report_agent: {e}.")
        raise e

async def ask_agents_in_parallel(question: str) -> str:
    """
    Queries the Revenue Agent, Customer Agent, and Risk Agent concurrently in parallel.
    Always call this tool first to gather findings quickly and avoid sequential delay.
    
    Args:
        question: The user query or business question.
        
    Returns:
        Combined findings text from all three agents.
    """
    import asyncio
    print("[ADK TRACE] Parallel Sub-agent Execution Started via ADK Parallel Tool")
    
    results = await asyncio.gather(
        ask_revenue_agent(question),
        ask_customer_agent("Analyze customer segment performance and churn metrics."),
        ask_risk_agent("Detect critical anomalies and business risk events."),
        return_exceptions=True
    )
    
    rev_res, cust_res, risk_res = results
    
    if isinstance(rev_res, Exception):
        rev_res = f"Revenue Agent Error: {str(rev_res)}"
    if isinstance(cust_res, Exception):
        cust_res = f"Customer Agent Error: {str(cust_res)}"
    if isinstance(risk_res, Exception):
        risk_res = f"Risk Agent Error: {str(risk_res)}"
        
    combined_findings = f"""
=== REVENUE AGENT FINDINGS ===
{rev_res}

=== CUSTOMER AGENT FINDINGS ===
{cust_res}

=== RISK AGENT FINDINGS ===
{risk_res}
"""
    return combined_findings

from google.genai import types
from backend.tools.mcp_client import mcp_toolset

# Define retry options for robust API handling
retry_config = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(initial_delay=2.0, attempts=3)
    )
)

from backend import config

executive_orchestrator = Agent(
    model=config.GEMINI_MODEL,
    name="executive_orchestrator",
    description="The parent orchestrator agent that delegates business analysis tasks and compiles reports.",
    instruction="""You are the Boardroom AI Executive Orchestrator.
Your goal is to coordinate a fleet of sub-agents to compile a complete strategic business analysis report.
When a user asks a business question:
1. Delegate the analysis gathering to the sub-agents by calling `ask_agents_in_parallel` with the user's question. This runs Revenue, Customer, and Risk analysis concurrently.
2. Compile these findings into the final report by calling `ask_report_agent` with the collected findings text.
3. Save the final report using the `memory` tool if needed, or simply return the report.
4. Return the final compiled report to the user.""",
    tools=[ask_agents_in_parallel, ask_report_agent, mcp_toolset],
    sub_agents=[revenue_agent, customer_agent, risk_agent, report_agent],
    generate_content_config=config.get_agent_config()
)

executive_orchestrator_fallback = Agent(
    model=config.GEMINI_FALLBACK_MODEL,
    name="executive_orchestrator_fallback",
    description="The fallback orchestrator agent that delegates business analysis tasks and compiles reports.",
    instruction="""You are the Boardroom AI Executive Orchestrator Fallback.
Your goal is to coordinate a fleet of sub-agents to compile a complete strategic business analysis report using fallback models.
When a user asks a business question:
1. Delegate the analysis gathering to the sub-agents by calling `ask_agents_in_parallel` with the user's question. This runs Revenue, Customer, and Risk analysis concurrently.
2. Compile these findings into the final report by calling `ask_report_agent` with the collected findings text.
3. Save the final report using the `memory` tool if needed, or simply return the report.
4. Return the final compiled report to the user.""",
    tools=[ask_agents_in_parallel, ask_report_agent, mcp_toolset],
    generate_content_config=config.get_agent_config()
)

root_agent = executive_orchestrator


