# Risk & Anomaly Detection Skill

**Goal**: Identify anomalous business metrics, sharp declines, and volatility warnings.

**Steps**:
1. Query transaction/revenue records using `query_data`.
2. Call the `run_analysis` capability tool with `analysis_type="risk"`.
3. Check if month-over-month decline exceeds risk thresholds (e.g. -10%).
4. Check if regional declines exceed limits (e.g. -20%).
5. Generate warning indicators detailing critical anomalies for senior leadership.
