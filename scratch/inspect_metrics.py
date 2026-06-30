import sqlite3
from backend import config

try:
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, metric_name, metric_value, timestamp FROM observability_metrics")
    rows = cursor.fetchall()
    print(f"Total metrics rows: {len(rows)}")
    for row in rows[:50]:
        print(f"ID: {row[0]} | Name: {row[1]} | Value: {row[2]} | TS: {row[3]}")
    conn.close()
except Exception as e:
    print(f"Failed to inspect SQLite metrics: {e}")
