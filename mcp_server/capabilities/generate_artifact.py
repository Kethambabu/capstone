from backend.tools.report_tools import generate_report

def generate_artifact_tool(revenue_findings: str, customer_findings: str, risk_findings: str) -> dict:
    """
    Synthesizes findings into the final executive advisory report.
    """
    print("[ADK TRACE] MCP Query Executed: generate_artifact")
    try:
        report = generate_report(revenue_findings, customer_findings, risk_findings)
        print("[ADK TRACE] Report Generated")
        return {
            "artifact_content": report,
            "type": "markdown_report"
        }
    except Exception as e:
        print(f"Error in generate_artifact capability: {e}")
        return {"error": str(e)}
