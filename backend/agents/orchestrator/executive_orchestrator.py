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

from google.adk import Workflow, Event

def security_checkpoint(node_input: str):
    from backend.agents.security.security_agent import scan_safety_heuristics
    
    # Simple check for Viewer role
    is_viewer = "role: viewer" in node_input.lower() or "viewer role" in node_input.lower()
    heur_res = scan_safety_heuristics(node_input)
    
    if is_viewer or heur_res:
        reason = "unauthorized_access" if is_viewer else (heur_res.get("reason", "prompt_injection") if heur_res else "safety_violation")
        # Store security event in DB
        try:
            from backend.database.supabase import db_store_security_event
            db_store_security_event(reason, "HIGH", f"Safety block in workflow: {node_input[:200]}")
        except Exception:
            pass
        return Event(route="SECURITY_EVENT", output=f"⚠️ SECURITY BLOCK: Access Denied. Reason: {reason}.")
        
    return Event(route="CLEAN", output=node_input)

def security_error_handler(node_input: str):
    return Event(output=node_input)

# Import forecast and risk agents, and rename them to match the diagram
from backend.agents.forecast.forecast_agent import forecast_agent
from backend.agents.risk.risk_agent import risk_agent

# Create forecasting_agent and risk_analysis_agent with correct names
forecasting_agent = Agent(
    model=config.GEMINI_MODEL,
    name="forecasting_agent",
    description="Estimates future growth trends and calculates forecasting metrics via MCP.",
    instruction=forecast_agent.instruction,
    tools=forecast_agent.tools,
    generate_content_config=forecast_agent.generate_content_config
)

risk_analysis_agent = Agent(
    model=config.GEMINI_MODEL,
    name="risk_analysis_agent",
    description="Detects anomalous patterns, drops, and business risks via MCP.",
    instruction=risk_agent.instruction,
    tools=risk_agent.tools,
    generate_content_config=risk_agent.generate_content_config
)

strategic_advisor_agent = Agent(
    model=config.GEMINI_MODEL,
    name="strategic_advisor_agent",
    description="Strategic Advisor Agent that coordinates specialized sub-agents.",
    instruction="""You are the Boardroom AI Strategic Advisor Agent.
Your goal is to coordinate a team of specialized sub-agents to compile a complete strategic business analysis report.
You have the following specialized sub-agents:
1. 'forecasting_agent': For revenue and growth projections.
2. 'risk_analysis_agent': For anomaly and risk diagnostics.

The available datasets are:
- 'sales' (contains monthly revenue, region, product category, and date)

When a user asks a business question:
1. Route the inquiry to 'risk_analysis_agent' to detect anomalies and regional risks in the 'sales' dataset.
2. Route the inquiry to 'forecasting_agent' to perform growth forecasting using the 'sales' dataset.
3. Formulate a combined summary of the findings and output it. Do not include headers like 'Status:' or 'BOARDROOM AI - EXECUTIVE ADVISORY REPORT' since the next node will format them.""",
    tools=[mcp_toolset],
    sub_agents=[forecasting_agent, risk_analysis_agent],
    generate_content_config=config.get_agent_config()
)

def router_node(node_input: str):
    text = str(node_input).lower()
    if "drop" in text or "decline" in text or "risk" in text or "anomaly" in text:
        return Event(route="review", output=node_input)
    return Event(route="approve", output=node_input)

def executive_approval(node_input: str):
    prefix = "# BOARDROOM AI - EXECUTIVE ADVISORY REPORT\n**Status: ⚠️ PENDING EXECUTIVE REVIEW (High Priority Variance Detected)**\n\n"
    return Event(output=prefix + node_input)

def auto_approve(node_input: str):
    prefix = "# BOARDROOM AI - EXECUTIVE ADVISORY REPORT\n**Status: ✅ AUTO-APPROVED BY POLICY (Standard Variance)**\n\n"
    return Event(output=prefix + node_input)

def final_report(node_input: str):
    return Event(output=node_input)

executive_orchestrator = Workflow(
    name="executive_orchestrator",
    edges=[
        ("START", security_checkpoint),
        (security_checkpoint, {
            "SECURITY_EVENT": security_error_handler,
            "CLEAN": strategic_advisor_agent
        }),
        (strategic_advisor_agent, router_node),
        (router_node, {
            "review": executive_approval,
            "approve": auto_approve
        }),
        (executive_approval, final_report),
        (auto_approve, final_report)
    ]
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



