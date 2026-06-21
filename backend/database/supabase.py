import sqlite3
import datetime
from backend import config

# Initialize Supabase client if credentials exist
supabase_client = None
if config.SUPABASE_URL and config.SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}. Falling back to SQLite.")

def db_init():
    """Initializes the database. For local fallback, creates SQLite table."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT,
            uploaded_at TEXT,
            file_path TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Local database initialized/verified.")

def insert_dataset(dataset_id: str, name: str, file_path: str):
    """Inserts a dataset metadata record."""
    uploaded_at = datetime.datetime.utcnow().isoformat()
    
    # Try Supabase first if available
    if supabase_client:
        try:
            data, count = supabase_client.table("datasets").insert({
                "id": dataset_id,
                "name": name,
                "uploaded_at": uploaded_at,
                "file_path": file_path
            }).execute()
            print("Successfully inserted dataset metadata into Supabase.")
            return True
        except Exception as e:
            print(f"Failed to insert into Supabase: {e}. Writing to local database.")
            
    # Local fallback
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets (id, name, uploaded_at, file_path) VALUES (?, ?, ?, ?)",
        (dataset_id, name, uploaded_at, file_path)
    )
    conn.commit()
    conn.close()
    print("Successfully inserted dataset metadata locally.")
    return True

def get_dataset(dataset_id: str):
    """Retrieves dataset metadata."""
    if supabase_client:
        try:
            response = supabase_client.table("datasets").select("*").eq("id", dataset_id).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            print(f"Supabase query failed: {e}. Checking local database.")
            
    # Local fallback
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, uploaded_at, file_path FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "uploaded_at": row[2],
            "file_path": row[3]
        }
    return None
