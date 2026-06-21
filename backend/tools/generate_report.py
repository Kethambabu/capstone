def generate_report(analysis_results: str) -> str:
    """
    Formats the analysis results into a clean executive summary draft,
    structuring it with key sections: Executive Summary, Key Findings, and Strategic Recommendations.
    
    Args:
        analysis_results: The raw text containing data calculations and trends.
        
    Returns:
        A structured Markdown executive report.
    """
    report_lines = [
        "# BOARDROOM AI - EXECUTIVE ANALYSIS REPORT",
        "**Confidential | Prepared for Executive Leadership**",
        "\n---",
        "\n## 1. Executive Summary",
        "Provide a high-level summary of the business question and the critical bottom-line answer.",
        "\n## 2. Key Findings & Data Trends",
        "Below is the data extracted and analyzed for this report:",
        f"\n```\n{analysis_results}\n```",
        "\n## 3. Strategic Recommendations",
        "Outline actionable business recommendations (e.g., target marketing, product focus, region expansion) based on the findings above.",
        "\n---",
        "Report compiled by Boardroom AI Executive Agent."
    ]
    return "\n".join(report_lines)
