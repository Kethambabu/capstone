from backend import config
from backend.database import supabase
import sqlite3

print("=== SUPABASE DATASETS ===")
if supabase.supabase_client:
    try:
        response = supabase.supabase_client.table("datasets").select("*").execute()
        for r in response.data:
            print(f"ID: {r.get('id')} | Name: {r.get('name')} | Uploaded At: {r.get('uploaded_at')}")
    except Exception as e:
        print(f"Failed to fetch Supabase datasets: {e}")
else:
    print("Supabase client not initialized.")

print("\n=== SQLITE DATASETS ===")
try:
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, uploaded_at FROM datasets")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Uploaded At: {row[2]}")
    conn.close()
except Exception as e:
    print(f"Failed to fetch SQLite datasets: {e}")
