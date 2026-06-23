# Customer Churn Skill

**Goal**: Assess customer segment health, calculate churn rates, and identify risk distributions.

**Steps**:
1. Query customer records using `query_data` tool with the dataset name (e.g. "customers").
2. Call the `run_analysis` capability tool with `analysis_type="customer"`.
3. Compute the overall churn percentage.
4. Distinguish churn patterns between key segment classes (e.g. Premium vs Standard).
5. Identify segments requiring immediate retention strategies.
