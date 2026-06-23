def generate_report(revenue_findings: str, customer_findings: str, risk_findings: str) -> str:
    """
    Combines analysis findings from the Revenue Agent, Customer Agent, 
    and Risk Agent into a polished Executive Summary report.
    
    Args:
        revenue_findings: Output findings from the Revenue Agent.
        customer_findings: Output findings from the Customer Agent.
        risk_findings: Output findings from the Risk Agent.
        
    Returns:
        A structured Markdown executive report.
    """
    report_lines = [
        "# BOARDROOM AI - MULTI-AGENT ADVISORY REPORT",
        "**Confidential | Prepared for Executive Leadership**",
        "\n---",
        "\n## 1. Executive Summary",
        "Synthesis of the quantitative trends, user metrics, and business alerts compiled by the Boardroom AI sub-agent fleet.",
        "\n## 2. Key Findings & Data Trends",
        "\n### A. Revenue & Financial Diagnostics",
        f"```\n{revenue_findings}\n```",
        "\n### B. Customer Segment & Churn Insights",
        f"```\n{customer_findings}\n```",
        "\n### C. Business Risks & Anomalies",
        f"```\n{risk_findings}\n```",
        "\n## 3. Strategic Recommendations",
        "Actionable business guidance derived from the cross-functional agent inputs:",
        "1. **Stabilize High-Churn Segments:** Address churn in high-risk categories highlighted in the Customer Analysis.",
        "2. **Address regional declines:** Reallocate capital to cover declining geographic regions identified in the Risk Alerts.",
        "3. **Optimize product campaigns:** Boost underperforming product categories shown in the Revenue breakdown.",
        "\n---",
        "Report compiled by Boardroom AI Agent Fleet via Executive Orchestrator."
    ]
    return "\n".join(report_lines)
