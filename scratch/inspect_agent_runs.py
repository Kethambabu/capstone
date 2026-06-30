import sqlite3
from backend import config

try:
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Check agent runs
    cursor.execute("SELECT id, agent_name, status, duration, start_time FROM agent_runs ORDER BY start_time DESC LIMIT 20")
    rows = cursor.fetchall()
    print(f"Total agent runs: {len(rows)}")
    for row in rows:
        print(f"ID: {row[0]} | Agent: {row[1]} | Status: {row[2]} | Duration: {row[3]}s | Start: {row[4]}")
        
    # Check average latency and count
    cursor.execute("SELECT AVG(duration), COUNT(*) FROM agent_runs WHERE status='COMPLETED'")
    avg_dur, count = cursor.fetchone()
    print(f"\nSQLite Calculated Avg Duration: {avg_dur}s | Count: {count}")
    
    conn.close()
except Exception as e:
    print(f"Failed to inspect SQLite agent runs: {e}")
