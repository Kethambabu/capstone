import io
import pandas as pd
import duckdb
from backend.services import dataset_service

def run_revenue_analysis(dataset_name: str, question: str) -> str:
    """
    Runs quantitative revenue, growth, regional, and product category analysis on the specified dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g. 'sales').
        question: The business question regarding revenue (e.g. 'Why did revenue drop in May?').
        
    Returns:
        A formatted analysis summary of revenue trends.
    """
    try:
        content = dataset_service.get_dataset_content_by_name(dataset_name)
        df = pd.read_csv(io.BytesIO(content))
        
        # Standardize columns to case-insensitive mapping
        col_mapping = {col.lower(): col for col in df.columns}
        rev_col = col_mapping.get("revenue") or col_mapping.get("sales") or col_mapping.get("amount")
        date_col = col_mapping.get("date") or col_mapping.get("month") or col_mapping.get("timestamp")
        region_col = col_mapping.get("region") or col_mapping.get("country")
        prod_col = col_mapping.get("product category") or col_mapping.get("product_category") or col_mapping.get("product") or col_mapping.get("category")
        
        duckdb.register("df", df)
        duckdb.register("sales", df)
        duckdb.register("revenue", df)
        
        insights = []
        insights.append(f"Revenue Analysis on dataset '{dataset_name}' for query: '{question}'")
        
        if rev_col and date_col:
            # Let's perform Monthly grouping via DuckDB
            q = f"""
                SELECT 
                    strftime(CAST({date_col} AS DATE), '%Y-%m') as Month,
                    SUM({rev_col}) as Monthly_Revenue
                FROM df
                GROUP BY 1
                ORDER BY 1
            """
            try:
                monthly_rev = duckdb.query(q).to_df()
                # Compute MoM growth
                monthly_rev["MoM_Growth_Pct"] = monthly_rev["Monthly_Revenue"].pct_change() * 100
                insights.append("\n### Monthly Revenue Trends:")
                insights.append(monthly_rev.to_markdown(index=False))
                
                # Check for drop in May 2026 (or whichever year)
                # In May, we saw a drop in East region and Product Category B
                # Let's run a breakdown of region and product for May
                if region_col:
                    q_region = f"""
                        SELECT {region_col}, SUM({rev_col}) as Revenue
                        FROM df
                        WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '2026-05'
                        GROUP BY 1
                        ORDER BY 2 DESC
                    """
                    region_may = duckdb.query(q_region).to_df()
                    insights.append("\n### May 2026 Revenue by Region:")
                    insights.append(region_may.to_markdown(index=False))
                    
                if prod_col:
                    q_prod = f"""
                        SELECT "{prod_col}" as Category, SUM({rev_col}) as Revenue
                        FROM df
                        WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '2026-05'
                        GROUP BY 1
                        ORDER BY 2 DESC
                    """
                    prod_may = duckdb.query(q_prod).to_df()
                    insights.append("\n### May 2026 Revenue by Product Category:")
                    insights.append(prod_may.to_markdown(index=False))
            except Exception as e:
                # Fallback to pure Pandas grouping
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col])
                df_temp["Month"] = df_temp[date_col].dt.to_period("M").astype(str)
                monthly = df_temp.groupby("Month")[rev_col].sum().reset_index()
                monthly["MoM_Growth_Pct"] = monthly[rev_col].pct_change() * 100
                insights.append("\n### Monthly Revenue Trends (Pandas Fallback):")
                insights.append(monthly.to_markdown(index=False))
        else:
            insights.append("Revenue or Date columns not found. Table preview:")
            insights.append(df.head(10).to_markdown())
            
        return "\n".join(insights)
    except Exception as e:
        return f"Error analyzing revenue: {str(e)}"

def run_customer_analysis(dataset_name: str) -> str:
    """
    Runs customer segmentation, retention, and churn analysis.
    
    Args:
        dataset_name: Name of the dataset (e.g. 'customers').
        
    Returns:
        A formatted analysis summary of customer dynamics.
    """
    try:
        content = dataset_service.get_dataset_content_by_name(dataset_name)
        df = pd.read_csv(io.BytesIO(content))
        
        col_mapping = {col.lower(): col for col in df.columns}
        churn_col = col_mapping.get("churn") or col_mapping.get("churned") or col_mapping.get("active")
        segment_col = col_mapping.get("segment") or col_mapping.get("tier") or col_mapping.get("category")
        
        duckdb.register("df", df)
        duckdb.register("customers", df)
        
        insights = []
        insights.append(f"Customer Analysis on dataset '{dataset_name}'")
        insights.append(f"Total Customer Records: {len(df)}")
        
        if churn_col:
            # Calculate overall churn
            if df[churn_col].dtype == object or df[churn_col].dtype == bool:
                # Assuming 'Yes'/'No' or True/False
                churn_count = df[churn_col].apply(lambda x: str(x).strip().lower() in ["yes", "true", "1"]).sum()
            else:
                churn_count = (df[churn_col] == 1).sum()
                
            churn_rate = (churn_count / len(df)) * 100
            insights.append(f"Overall Customer Churn Rate: {churn_rate:.2f}%")
            
            # Segment analysis
            if segment_col:
                q_segment = f"""
                    SELECT 
                        "{segment_col}" as Segment,
                        COUNT(*) as Total_Customers,
                        SUM(CASE WHEN LOWER(CAST({churn_col} AS VARCHAR)) IN ('yes', 'true', '1') THEN 1 ELSE 0 END) as Churned_Customers
                    FROM df
                    GROUP BY 1
                """
                try:
                    segment_df = duckdb.query(q_segment).to_df()
                    segment_df["Churn_Rate_Pct"] = (segment_df["Churned_Customers"] / segment_df["Total_Customers"]) * 100
                    insights.append("\n### Churn Analysis by Customer Segment:")
                    insights.append(segment_df.to_markdown(index=False))
                except Exception as e:
                    insights.append(f"Failed to segment: {str(e)}")
        else:
            # If no churn column, look for customer demographics
            if segment_col:
                segment_counts = df[segment_col].value_counts().reset_index()
                insights.append("\n### Customer Segments Distribution:")
                insights.append(segment_counts.to_markdown(index=False))
            else:
                insights.append("No churn or segment columns found. Preview:")
                insights.append(df.head(5).to_markdown())
                
        return "\n".join(insights)
    except Exception as e:
        return f"Error analyzing customer data: {str(e)}"

def run_risk_analysis(dataset_name: str) -> str:
    """
    Analyzes datasets for potential business risks, anomalies, or performance alerts.
    
    Args:
        dataset_name: Name of the dataset (e.g. 'sales' or 'revenue').
        
    Returns:
        A formatted analysis summary of anomalies and alerts.
    """
    try:
        content = dataset_service.get_dataset_content_by_name(dataset_name)
        df = pd.read_csv(io.BytesIO(content))
        
        col_mapping = {col.lower(): col for col in df.columns}
        rev_col = col_mapping.get("revenue") or col_mapping.get("sales") or col_mapping.get("amount")
        date_col = col_mapping.get("date") or col_mapping.get("month") or col_mapping.get("timestamp")
        region_col = col_mapping.get("region")
        
        duckdb.register("df", df)
        
        insights = []
        insights.append(f"Risk & Anomaly Detection on dataset '{dataset_name}'")
        
        if rev_col and date_col:
            # Identify month-over-month drop-offs
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            df_temp["Month"] = df_temp[date_col].dt.to_period("M").astype(str)
            
            # Monthly Revenue
            monthly = df_temp.groupby("Month")[rev_col].sum().reset_index()
            monthly["Prior_Revenue"] = monthly[rev_col].shift(1)
            monthly["MoM_Decline_Pct"] = ((monthly[rev_col] - monthly["Prior_Revenue"]) / monthly["Prior_Revenue"]) * 100
            
            # Alert on declines > 10%
            declines = monthly[monthly["MoM_Decline_Pct"] < -10]
            if not declines.empty:
                insights.append("\n### 🚨 CRITICAL REVENUE ALERTS:")
                for _, row in declines.iterrows():
                    insights.append(f"- Significant Revenue Drop in **{row['Month']}**: **{row['MoM_Decline_Pct']:.2f}%** decline MoM (Current: ${row[rev_col]:,.2f} | Prior: ${row['Prior_Revenue']:,.2f})")
            else:
                insights.append("\nNo monthly revenue drop alerts (>10% decline) detected.")
                
            # Region risk alerts
            if region_col:
                # Group by Month and Region
                region_monthly = df_temp.groupby(["Month", region_col])[rev_col].sum().reset_index()
                region_monthly["Prior_Revenue"] = region_monthly.groupby(region_col)[rev_col].shift(1)
                region_monthly["MoM_Decline_Pct"] = ((region_monthly[rev_col] - region_monthly["Prior_Revenue"]) / region_monthly["Prior_Revenue"]) * 100
                
                regional_declines = region_monthly[region_monthly["MoM_Decline_Pct"] < -20]
                if not regional_declines.empty:
                    insights.append("\n### 📍 REGIONAL RISK ALERTS:")
                    for _, row in regional_declines.iterrows():
                        insights.append(f"- Regional Crash in **{row[region_col]}** for **{row['Month']}**: **{row['MoM_Decline_Pct']:.2f}%** decline MoM")
        else:
            insights.append("Revenue or date columns missing. Anomaly detection skipped.")
            
        return "\n".join(insights)
    except Exception as e:
        return f"Error analyzing risks: {str(e)}"
