import io
import pandas as pd
import duckdb
from backend.services import dataset_service

def run_analysis(dataset_id: str, query: str) -> str:
    """
    Analyzes the dataset using SQL queries via DuckDB or pandas operations.
    If the query parameter looks like a SQL statement (starts with SELECT, WITH, etc.), 
    it executes it on the dataset.
    Otherwise, it runs standard diagnostics (aggregations by date/month, region, and product category) 
    to extract business insights.
    
    Args:
        dataset_id: The ID of the dataset to analyze.
        query: Either a raw SQL statement or a natural language description of what to analyze.
        
    Returns:
        A string summary of the analysis findings.
    """
    try:
        content = dataset_service.get_dataset_content(dataset_id)
        df = pd.read_csv(io.BytesIO(content))
        
        # Get metadata to find clean filename
        try:
            meta = dataset_service.get_dataset_meta(dataset_id)
            filename_clean = meta["name"].split(".")[0].lower()
        except Exception:
            filename_clean = "sales"

        # Register standard aliases in DuckDB to avoid table name mismatches
        duckdb.register("df", df)
        duckdb.register("data", df)
        duckdb.register("dataset", df)
        duckdb.register("datasets", df)
        duckdb.register("sales", df)
        if filename_clean.isidentifier():
            duckdb.register(filename_clean, df)

        # Standardize columns to case-insensitive matching if they exist
        col_mapping = {col.lower(): col for col in df.columns}
        
        # Check if the query is a SQL statement
        is_sql = any(query.strip().upper().startswith(keyword) for keyword in ["SELECT", "WITH", "SHOW", "DESCRIBE"])
        
        if is_sql:
            # Execute SQL via DuckDB
            # DuckDB can query the local pandas DataFrame 'df' directly
            result = duckdb.query(query).to_df()
            return f"SQL Query Executed:\n{query}\n\nResult:\n{result.to_markdown(index=False)}"
        
        # Run standard business analysis
        insights = []
        insights.append(f"Business Diagnostics for Query: '{query}'")
        
        # 1. Look for Date/Month and Revenue columns
        rev_col = None
        for candidate in ["revenue", "sales", "amount", "price"]:
            if candidate in col_mapping:
                rev_col = col_mapping[candidate]
                break
                
        date_col = None
        for candidate in ["date", "month", "timestamp", "period"]:
            if candidate in col_mapping:
                date_col = col_mapping[candidate]
                break
                
        region_col = None
        for candidate in ["region", "country", "state", "city", "location"]:
            if candidate in col_mapping:
                region_col = col_mapping[candidate]
                break
                
        prod_col = None
        for candidate in ["product", "category", "item", "product category", "product_category"]:
            if candidate in col_mapping:
                prod_col = col_mapping[candidate]
                break

        # Let's perform aggregations based on identified columns
        if rev_col:
            total_rev = df[rev_col].sum()
            insights.append(f"Total Revenue across dataset: {total_rev:,.2f}")
            
            # Date/Month breakdown
            if date_col:
                # Convert to datetime if possible, or group by string
                try:
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col])
                    # Group by year-month
                    df_temp["YearMonth"] = df_temp[date_col].dt.to_period("M").astype(str)
                    monthly = df_temp.groupby("YearMonth")[rev_col].sum().reset_index()
                    # Calculate MoM growth
                    monthly["MoM_Growth_%"] = monthly[rev_col].pct_change() * 100
                    insights.append("\nMonthly Revenue Trend:")
                    insights.append(monthly.to_markdown(index=False))
                except Exception:
                    # Fallback to string grouping
                    monthly = df.groupby(date_col)[rev_col].sum().reset_index()
                    insights.append("\nRevenue by Date/Month:")
                    insights.append(monthly.to_markdown(index=False))
                    
            # Region breakdown
            if region_col:
                region_rev = df.groupby(region_col)[rev_col].sum().reset_index().sort_values(by=rev_col, ascending=False)
                insights.append("\nRevenue by Region:")
                insights.append(region_rev.to_markdown(index=False))
                
            # Product breakdown
            if prod_col:
                prod_rev = df.groupby(prod_col)[rev_col].sum().reset_index().sort_values(by=rev_col, ascending=False)
                insights.append("\nRevenue by Product/Category:")
                insights.append(prod_rev.to_markdown(index=False))
        else:
            # If no revenue column, just return basic info
            insights.append("No numeric revenue/sales column identified. Here is a summary of the dataset:")
            insights.append(df.describe().to_markdown())
            
        return "\n".join(insights)
    except Exception as e:
        err_msg = f"Error running analysis: {str(e)}"
        print(err_msg)
        return err_msg
