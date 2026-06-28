import io
import pandas as pd
import duckdb
from backend.services import dataset_service

def extract_timeframe_from_query(question: str, df: pd.DataFrame, date_col: str) -> dict:
    """
    Dynamically extracts target year, month name, and YYYY-MM strings for calculations.
    Defaults to the latest date in the dataset if no month/year is requested.
    """
    import re
    question_lower = question.lower()
    
    months_map = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12"
    }
    
    full_months = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    
    target_month_num = None
    target_month_name = None
    for m_name, m_num in months_map.items():
        if re.search(r'\b' + m_name + r'\b', question_lower):
            target_month_num = m_num
            target_month_name = full_months[m_num]
            break
            
    target_year = None
    year_match = re.search(r'\b(20\d{2})\b', question_lower)
    if year_match:
        target_year = int(year_match.group(1))
        
    available_dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
    
    if available_dates.empty:
        target_year = target_year or 2026
        target_month_num = target_month_num or "05"
        target_month_name = target_month_name or "May"
    else:
        if target_month_num and target_year:
            pass
        elif target_month_num and not target_year:
            years_with_month = []
            for dt in available_dates:
                if f"{dt.month:02d}" == target_month_num:
                    years_with_month.append(dt.year)
            if years_with_month:
                target_year = max(years_with_month)
            else:
                target_year = available_dates.dt.year.max()
        elif not target_month_num and target_year:
            months_in_year = []
            for dt in available_dates:
                if dt.year == target_year:
                    months_in_year.append(dt.month)
            if months_in_year:
                max_m = max(months_in_year)
                target_month_num = f"{max_m:02d}"
                target_month_name = full_months[target_month_num]
            else:
                target_month_num = "05"
                target_month_name = "May"
        else:
            latest_dt = available_dates.max()
            target_year = latest_dt.year
            target_month_num = f"{latest_dt.month:02d}"
            target_month_name = full_months[target_month_num]
                
    if not target_month_name:
        target_month_name = full_months.get(target_month_num, "May")

    target_year_int = int(target_year)
    target_month_int = int(target_month_num)
    
    if target_month_int == 1:
        prev_month_int = 12
        prev_year_int = target_year_int - 1
    else:
        prev_month_int = target_month_int - 1
        prev_year_int = target_year_int
        
    prev_month_num = f"{prev_month_int:02d}"
    prev_year = str(prev_year_int)
    prev_month_name = full_months[prev_month_num]
        
    prev_year_yoy_int = target_year_int - 1
    prev_year_yoy = str(prev_year_yoy_int)
    
    target_ym = f"{target_year_int}-{target_month_num}"
    prev_ym = f"{prev_year_int}-{prev_month_num}"
    yoy_ym = f"{prev_year_yoy_int}-{target_month_num}"
    
    return {
        "target_year": str(target_year_int),
        "target_month_num": target_month_num,
        "target_month_name": target_month_name,
        "target_ym": target_ym,
        "prev_year": prev_year,
        "prev_month_num": prev_month_num,
        "prev_month_name": prev_month_name,
        "prev_ym": prev_ym,
        "prev_year_yoy": prev_year_yoy,
        "yoy_ym": yoy_ym
    }

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
        
        # Identify columns
        event_col = col_mapping.get("event")
        event_type_col = col_mapping.get("event_type")
        anomaly_col = col_mapping.get("anomaly")
        prod_name_col = col_mapping.get("product_name") or col_mapping.get("product")

        insights = []
        insights.append(f"Revenue Analysis on dataset '{dataset_name}' for query: '{question}'")
        
        if rev_col and date_col:
            # Resolve timeframe dynamically
            tf = extract_timeframe_from_query(question, df, date_col)
            
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
                
                # Check for drop in target month
                if region_col:
                    q_region = f"""
                        SELECT {region_col}, SUM({rev_col}) as Revenue
                        FROM df
                        WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}'
                        GROUP BY 1
                        ORDER BY 2 DESC
                    """
                    region_may = duckdb.query(q_region).to_df()
                    insights.append(f"\n### {tf['target_month_name']} {tf['target_year']} Revenue by Region:")
                    insights.append(region_may.to_markdown(index=False))
                    
                if prod_col:
                    q_prod = f"""
                        SELECT "{prod_col}" as Category, SUM({rev_col}) as Revenue
                        FROM df
                        WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}'
                        GROUP BY 1
                        ORDER BY 2 DESC
                    """
                    prod_may = duckdb.query(q_prod).to_df()
                    insights.append(f"\n### {tf['target_month_name']} {tf['target_year']} Revenue by Product Category:")
                    insights.append(prod_may.to_markdown(index=False))

                # YoY Comparison
                q_yoy = f"""
                    SELECT 
                        SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}' THEN {rev_col} ELSE 0 END) as target_rev,
                        SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["yoy_ym"]}' THEN {rev_col} ELSE 0 END) as prev_rev
                    FROM df
                """
                yoy_df = duckdb.query(q_yoy).to_df()
                may_26 = yoy_df.loc[0, "target_rev"] or 0.0
                may_25 = yoy_df.loc[0, "prev_rev"] or 0.0
                if may_25 > 0:
                    yoy_pct = ((may_26 - may_25) / may_25) * 100
                    insights.append(f"\n### YoY Comparison ({tf['target_month_name']} {tf['target_year']} vs {tf['target_month_name']} {tf['prev_year_yoy']}):\n- {tf['target_month_name']} {tf['target_year']} Revenue: ${may_26:,.2f}\n- {tf['target_month_name']} {tf['prev_year_yoy']} Revenue: ${may_25:,.2f}\n- YoY Growth Pct: {yoy_pct:+.2f}%")

                # Regional MoM breakdown
                if region_col:
                    q_reg_mom = f"""
                        SELECT 
                            {region_col} as Region,
                            SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["prev_ym"]}' THEN {rev_col} ELSE 0 END) as Prev_Revenue,
                            SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}' THEN {rev_col} ELSE 0 END) as Target_Revenue
                        FROM df
                        GROUP BY 1
                    """
                    reg_mom_df = duckdb.query(q_reg_mom).to_df()
                    reg_mom_df["MoM_Change_Pct"] = ((reg_mom_df["Target_Revenue"] - reg_mom_df["Prev_Revenue"]) / reg_mom_df["Prev_Revenue"]) * 100
                    reg_mom_df["MoM_Change_Pct"] = reg_mom_df["MoM_Change_Pct"].fillna(0.0)
                    insights.append(f"\n### Regional Revenue Shift ({tf['prev_month_name']} {tf['prev_year']} vs {tf['target_month_name']} {tf['target_year']}):")
                    insights.append(reg_mom_df.to_markdown(index=False))

                # Event type extraction
                if event_type_col:
                    q_ev_type = f"""
                        SELECT 
                            COALESCE({event_type_col}, 'Normal') as Event_Type,
                            COUNT(*) as Record_Count,
                            SUM({rev_col}) as Total_Revenue
                        FROM df
                        WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}'
                        GROUP BY 1
                        ORDER BY 3 DESC
                    """
                    ev_type_df = duckdb.query(q_ev_type).to_df()
                    insights.append(f"\n### {tf['target_month_name']} {tf['target_year']} Revenue Impact by Business Event Type:")
                    insights.append(ev_type_df.to_markdown(index=False))

                    # List all rows where event_type is filled in (non-Normal)
                    q_ev_rows = f"""
                        SELECT 
                            strftime(CAST({date_col} AS DATE), '%Y-%m-%d') as Date,
                            {region_col} as Region,
                            COALESCE({prod_name_col}, 'N/A') as Product,
                            {event_type_col} as Event_Type,
                            {event_col} as Event_Description,
                            {rev_col} as Revenue
                        FROM df
                        WHERE {event_type_col} IS NOT NULL 
                          AND {event_type_col} != '' 
                          AND LOWER({event_type_col}) != 'normal'
                        ORDER BY Date DESC
                    """
                    ev_rows_df = duckdb.query(q_ev_rows).to_df()
                    if not ev_rows_df.empty:
                        insights.append("\n### Detailed Business Events (Non-Normal):")
                        insights.append(ev_rows_df.to_markdown(index=False))

                # Anomaly rows listing
                if anomaly_col:
                    q_anom = f"""
                        SELECT 
                            strftime(CAST({date_col} AS DATE), '%Y-%m') as Month,
                            {region_col} as Region,
                            COALESCE({prod_name_col}, 'N/A') as Product,
                            {rev_col} as Revenue,
                            {event_col} as Event_Description,
                            {anomaly_col} as Anomaly_Severity
                        FROM df
                        WHERE LOWER({anomaly_col}) = 'critical'
                        ORDER BY Month DESC
                    """
                    anom_df = duckdb.query(q_anom).to_df()
                    if not anom_df.empty:
                        insights.append(f"\n### Critical Anomalies Detected ({len(anom_df)} total):")
                        insights.append(f"- **Total Critical Anomalies Count:** {len(anom_df)}")
                        insights.append(anom_df.to_markdown(index=False))

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
        
        churn_month_col = col_mapping.get("churn_month")
        region_col = col_mapping.get("region")
        sat_col = col_mapping.get("satisfaction_score") or col_mapping.get("satisfaction")

        if churn_col:
            # Calculate overall churn
            is_str_or_bool = df[churn_col].dtype in [object, bool] or str(df[churn_col].dtype) in ['object', 'bool', 'string', 'str', 'category']
            if is_str_or_bool:
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

            # Churn month spike: group by churn_month, find peak month
            if churn_month_col:
                q_churn_month = f"""
                    SELECT 
                        "{churn_month_col}" as Churn_Month,
                        COUNT(*) as Churned_Count
                    FROM df
                    WHERE LOWER(CAST({churn_col} AS VARCHAR)) IN ('yes', 'true', '1')
                      AND "{churn_month_col}" IS NOT NULL 
                      AND "{churn_month_col}" != ''
                    GROUP BY 1
                    ORDER BY 2 DESC
                """
                try:
                    churn_months_df = duckdb.query(q_churn_month).to_df()
                    if not churn_months_df.empty:
                        insights.append("\n### Churn Trend by Month (Spikes):")
                        insights.append(churn_months_df.to_markdown(index=False))
                        peak_row = churn_months_df.iloc[0]
                        insights.append(f"- **Peak Churn Month:** {peak_row['Churn_Month']} with **{peak_row['Churned_Count']}** churned customers.")
                except Exception as e:
                    pass

            # Regional churn breakdown: group by region + segment for churned customers
            if region_col and segment_col:
                q_reg_seg = f"""
                    SELECT 
                        "{region_col}" as Region,
                        "{segment_col}" as Segment,
                        COUNT(*) as Churned_Customers
                    FROM df
                    WHERE LOWER(CAST({churn_col} AS VARCHAR)) IN ('yes', 'true', '1')
                    GROUP BY 1, 2
                    ORDER BY 3 DESC
                """
                try:
                    reg_seg_df = duckdb.query(q_reg_seg).to_df()
                    insights.append("\n### Churn Breakdown by Region and Customer Segment:")
                    insights.append(reg_seg_df.to_markdown(index=False))
                except Exception as e:
                    pass

            # Satisfaction score comparison: average for churned vs retained
            if sat_col:
                q_sat = f"""
                    SELECT 
                        CASE WHEN LOWER(CAST({churn_col} AS VARCHAR)) IN ('yes', 'true', '1') THEN 'Churned' ELSE 'Retained' END as Customer_Status,
                        ROUND(AVG(CAST({sat_col} AS FLOAT)), 2) as Avg_Satisfaction_Score,
                        COUNT(*) as Customer_Count
                    FROM df
                    GROUP BY 1
                """
                try:
                    sat_df = duckdb.query(q_sat).to_df()
                    insights.append("\n### Satisfaction Score Comparison (Churned vs Retained):")
                    insights.append(sat_df.to_markdown(index=False))
                except Exception as e:
                    pass

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
        
        anomaly_col = col_mapping.get("anomaly")
        event_type_col = col_mapping.get("event_type")
        event_col = col_mapping.get("event")
        prod_col = col_mapping.get("product_name") or col_mapping.get("product")

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
            
            # Critical anomalies in sales
            if anomaly_col:
                critical_mask = df[anomaly_col].astype(str).str.lower().str.strip() == "critical"
                critical_df = df[critical_mask]
                if not critical_df.empty:
                    insights.append("\n### ⚠️ CRITICAL EVENT ANOMALIES:")
                    for _, row in critical_df.iterrows():
                        d_val = row[date_col] if date_col in row else "Unknown Date"
                        r_val = row[region_col] if region_col in row else "Unknown Region"
                        p_val = row[prod_col] if prod_col in row else "Unknown Product"
                        e_val = row[event_col] if event_col in row else "No details"
                        insights.append(f"- **{d_val}** [{r_val} Region] - {p_val}: {e_val}")

            # Revenue impact by event type
            if event_type_col:
                event_rev = df.groupby(event_type_col)[rev_col].agg(["count", "sum"]).reset_index()
                event_rev.columns = ["Event Type", "Event Count", "Total Revenue Affected"]
                insights.append("\n### 📊 REVENUE IMPACT BY EVENT TYPE:")
                insights.append(event_rev.to_markdown(index=False))

        else:
            insights.append("Revenue or date columns missing. Anomaly detection skipped.")
            
        # Open inventory_large.csv to check stockouts
        try:
            inv_df = None
            for name in ["inventory_large.csv", "inventory_large", "inventory"]:
                try:
                    content = dataset_service.get_dataset_content_by_name(name)
                    inv_df = pd.read_csv(io.BytesIO(content))
                    break
                except Exception:
                    continue
            
            if inv_df is not None:
                col_mapping_inv = {col.lower(): col for col in inv_df.columns}
                stockout_col = col_mapping_inv.get("stockout")
                stockout_month_col = col_mapping_inv.get("stockout_month")
                event_note_col = col_mapping_inv.get("event_note")
                prod_inv_col = col_mapping_inv.get("product")
                warehouse_col = col_mapping_inv.get("warehouse") or col_mapping_inv.get("region")
                
                if stockout_col:
                    stockout_mask = inv_df[stockout_col].astype(str).str.lower().str.strip().isin(["yes", "true", "1"])
                    stockout_rows = inv_df[stockout_mask]
                    if not stockout_rows.empty:
                        insights.append("\n### 📦 INVENTORY STOCKOUT ALERTS:")
                        for _, row in stockout_rows.iterrows():
                            p_val = row[prod_inv_col] if prod_inv_col in row else "Unknown Product"
                            wh_val = row[warehouse_col] if warehouse_col in row else "Unknown WH"
                            m_val = row[stockout_month_col] if stockout_month_col in row else "N/A"
                            n_val = row[event_note_col] if event_note_col in row else "No details"
                            insights.append(f"- **Stockout** for **{p_val}** in **{wh_val}** WH ({m_val}): {n_val}")
                    else:
                        insights.append("\nNo inventory stockouts detected in inventory records.")
        except Exception as inv_err:
            insights.append(f"\nCould not run inventory cross-reference analysis: {str(inv_err)}")
            
        return "\n".join(insights)
    except Exception as e:
        return f"Error analyzing risks: {str(e)}"
