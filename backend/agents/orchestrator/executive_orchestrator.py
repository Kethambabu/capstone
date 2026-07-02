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
    from backend.config import user_role_var
    from backend.agents.security.security_agent import is_role_allowed_for_dataset
    role = user_role_var.get()
    if not is_role_allowed_for_dataset(role, "sales"):
        return f"Access Denied: User with role '{role}' does not have permissions to access revenue data."

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
    from backend.config import user_role_var
    from backend.agents.security.security_agent import is_role_allowed_for_dataset
    role = user_role_var.get()
    if not is_role_allowed_for_dataset(role, "customers"):
        return f"Access Denied: User with role '{role}' does not have permissions to access customer data."

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
    from backend.config import user_role_var
    from backend.agents.security.security_agent import is_role_allowed_for_dataset
    role = user_role_var.get()
    if not is_role_allowed_for_dataset(role, "risks"):
        return f"Access Denied: User with role '{role}' does not have permissions to access risk data."

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

async def security_checkpoint(node_input: str):
    import re
    from backend.config import user_role_var
    from backend.agents.security.security_agent import run_security_check
    
    # 1. Dynamically extract role from input query if specified (e.g. "role: sales manager", "[Sales Manager]")
    role_match = re.search(
        r'(?:role:\s*|\[)(admin|sales manager|finance manager|viewer|analyst|ceo|executive|sales|finance)(?:\]|\b)',
        node_input,
        re.IGNORECASE
    )
    if role_match:
        extracted_role = role_match.group(1).strip().title()
        # Map shorthand names
        if extracted_role == "Sales":
            extracted_role = "Sales Manager"
        elif extracted_role == "Finance":
            extracted_role = "Finance Manager"
        user_role_var.set(extracted_role)
        print(f"[ADK TRACE] Extracted role '{extracted_role}' from query and updated context to: {extracted_role}")
    
    role = user_role_var.get()
    
    # Extract the user's actual question to prevent false positive length/injection blocks on assembled_context
    question_text = node_input
    if "Question:" in node_input:
        question_text = node_input.split("Question:", 1)[1].strip()

    # Preserve explicit viewer override checks
    if "role: viewer" in question_text.lower() or "viewer role" in question_text.lower():
        role = "Viewer"
        user_role_var.set("Viewer")

    # 2. Extract dataset ID
    dataset_id = None
    dataset_id_match = re.search(r'Dataset ID:\s*([a-zA-Z0-9_-]+)', node_input)
    if dataset_id_match:
        dataset_id = dataset_id_match.group(1).strip()

    # Run the unified security check (includes RBAC, heuristics, and model-based check)
    sec_res = await run_security_check(question_text, role, dataset_id)

    if not sec_res.get("allowed", True):
        reason = sec_res.get("reason", "safety_violation")
        msg = sec_res.get("message", "Model-based security check blocked the request.")
        
        # Store security event in DB
        try:
            from backend.database.supabase import db_store_security_event
            db_store_security_event(reason, "HIGH", f"Safety block in workflow: {node_input[:200]}")
        except Exception:
            pass
            
        return Event(route="SECURITY_EVENT", output=f"⚠️ SECURITY BLOCK: Access Denied. Reason: {reason}. {msg}")
        
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
    description="Strategic Advisor Agent that coordinates specialized sub-agents based on question intent.",
    instruction="""You are the Boardroom AI Strategic Advisor Agent.
Your goal is to coordinate a team of specialized sub-agents to compile a concise, executive-grade strategic business analysis report.
You have the following specialized sub-agents:
1. 'revenue_agent': For revenue growth, sales trends, and regional splits.
2. 'customer_agent': For customer churn, segments, and tier demographics.
3. 'risk_analysis_agent': For anomaly and risk diagnostics.
4. 'forecasting_agent': For growth forecasting and future projections.

When a user asks a business question:
1. Identify the primary intent (revenue, customer, risk, forecast).
2. Route the inquiry ONLY to the corresponding sub-agent first (e.g. 'revenue_agent' for sales questions like "What about my sales in June?"). Do not invoke other agents unless needed.
3. If the user asks an exploratory question (e.g., "Why did revenue drop?") or the primary agent's findings show a significant variance/decline, route to 'risk_analysis_agent' and 'forecasting_agent' to get explaining context. Otherwise, bypass them to save tokens.
4. Formulate the compiled findings into the final report structure:
   - ## 1. Direct Answer: Answer the user's specific question directly and concisely first. (e.g., June Sales Summary with MoM/YoY growth and Status).
   - ## 2. Executive Summary: Provide a brief high-level overview.
   - ## 3. Key Findings & Data Trends: Detail the metrics of the active agents (e.g. Revenue diagnostics). Do not include customer demographics or unrelated details unless relevant.
   - ## 4. Strategic Recommendations: Provide 2 specific, evidence-linked recommendations referencing specific regions, dates, and products.
Do not include headers like 'Status:' or 'BOARDROOM AI - EXECUTIVE ADVISORY REPORT' since the next node will format them.""",
    tools=[mcp_toolset],
    sub_agents=[revenue_agent, customer_agent, forecasting_agent, risk_analysis_agent],
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
1. Determine the query intent. Call the primary agent (e.g. ask_revenue_agent for sales queries).
2. If exploratory or if a decline is found, call ask_risk_agent or forecast agents to get context. Otherwise, bypass them to save tokens.
3. Return the compiled report following the target structure (Direct Answer, Executive Summary, Key Findings, Strategic Recommendations).""",
    tools=[ask_agents_in_parallel, ask_report_agent, mcp_toolset],
    generate_content_config=config.get_agent_config()
)

root_agent = executive_orchestrator



