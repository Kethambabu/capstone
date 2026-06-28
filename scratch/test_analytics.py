import io
import pandas as pd
import duckdb

def extract_timeframe_from_query(question: str, df: pd.DataFrame, date_col: str):
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

def run_revenue_analysis_dynamic(df: pd.DataFrame, question: str) -> str:
    col_mapping = {col.lower(): col for col in df.columns}
    rev_col = col_mapping.get("revenue") or col_mapping.get("sales") or col_mapping.get("amount")
    date_col = col_mapping.get("date") or col_mapping.get("month") or col_mapping.get("timestamp")
    region_col = col_mapping.get("region") or col_mapping.get("country")
    prod_col = col_mapping.get("product category") or col_mapping.get("product_category") or col_mapping.get("product") or col_mapping.get("category")
    
    duckdb.register("df", df)
    
    event_col = col_mapping.get("event")
    event_type_col = col_mapping.get("event_type")
    anomaly_col = col_mapping.get("anomaly")
    prod_name_col = col_mapping.get("product_name") or col_mapping.get("product")

    insights = []
    insights.append(f"Revenue Analysis for query: '{question}'")
    
    if rev_col and date_col:
        tf = extract_timeframe_from_query(question, df, date_col)
        print(f"Extracted timeframe: {tf}")
        
        # Monthly grouping
        q = f"""
            SELECT 
                strftime(CAST({date_col} AS DATE), '%Y-%m') as Month,
                SUM({rev_col}) as Monthly_Revenue
            FROM df
            GROUP BY 1
            ORDER BY 1
        """
        monthly_rev = duckdb.query(q).to_df()
        monthly_rev["MoM_Growth_Pct"] = monthly_rev["Monthly_Revenue"].pct_change() * 100
        insights.append("\n### Monthly Revenue Trends:")
        insights.append(monthly_rev.to_markdown(index=False))
        
        if region_col:
            q_region = f"""
                SELECT {region_col}, SUM({rev_col}) as Revenue
                FROM df
                WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}'
                GROUP BY 1
                ORDER BY 2 DESC
            """
            region_res = duckdb.query(q_region).to_df()
            insights.append(f"\n### {tf['target_month_name']} {tf['target_year']} Revenue by Region:")
            insights.append(region_res.to_markdown(index=False))
            
        if prod_col:
            q_prod = f"""
                SELECT "{prod_col}" as Category, SUM({rev_col}) as Revenue
                FROM df
                WHERE strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}'
                GROUP BY 1
                ORDER BY 2 DESC
            """
            prod_res = duckdb.query(q_prod).to_df()
            insights.append(f"\n### {tf['target_month_name']} {tf['target_year']} Revenue by Product Category:")
            insights.append(prod_res.to_markdown(index=False))

        # YoY Comparison
        q_yoy = f"""
            SELECT 
                SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["target_ym"]}' THEN {rev_col} ELSE 0 END) as target_rev,
                SUM(CASE WHEN strftime(CAST({date_col} AS DATE), '%Y-%m') = '{tf["yoy_ym"]}' THEN {rev_col} ELSE 0 END) as prev_rev
            FROM df
        """
        yoy_df = duckdb.query(q_yoy).to_df()
        target_rev_val = yoy_df.loc[0, "target_rev"] or 0.0
        prev_rev_val = yoy_df.loc[0, "prev_rev"] or 0.0
        if prev_rev_val > 0:
            yoy_pct = ((target_rev_val - prev_rev_val) / prev_rev_val) * 100
            insights.append(f"\n### YoY Comparison ({tf['target_month_name']} {tf['target_year']} vs {tf['target_month_name']} {tf['prev_year_yoy']}):\n- {tf['target_month_name']} {tf['target_year']} Revenue: ${target_rev_val:,.2f}\n- {tf['target_month_name']} {tf['prev_year_yoy']} Revenue: ${prev_rev_val:,.2f}\n- YoY Growth Pct: {yoy_pct:+.2f}%")

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
            
    return "\n".join(insights)

if __name__ == "__main__":
    df = pd.read_csv("data/sales_large.csv")
    print("--- TESTING APRIL SALES BREAKDOWN ---")
    res1 = run_revenue_analysis_dynamic(df, "What is the sales breakdown by Product Category in April?")
    print("\n--- TESTING JUNE REVENUE ---")
    res2 = run_revenue_analysis_dynamic(df, "What was the total revenue for June?")
    print(res2)
