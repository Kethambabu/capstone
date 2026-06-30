import sqlite3
from backend import config

try:
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    for metric in ["total_input_tokens", "total_output_tokens", "total_api_cost_usd"]:
        cursor.execute("SELECT SUM(metric_value) FROM observability_metrics WHERE metric_name = ?", (metric,))
        val = cursor.fetchone()[0] or 0.0
        print(f"Metric: {metric} | SUM: {val}")
        
    conn.close()
except Exception as e:
    print(f"Failed to inspect SQLite sums: {e}")
