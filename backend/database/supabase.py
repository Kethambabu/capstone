import sqlite3
import datetime
from backend import config

# Initialize Supabase client if credentials exist and host is reachable
supabase_client = None

def _handle_supabase_error(e):
    """Checks if the exception is due to network connection/resolution failure and disables Supabase if so."""
    global supabase_client
    err_str = str(e).lower()
    if "getaddrinfo" in err_str or "connection" in err_str or "timeout" in err_str or "unreachable" in err_str:
        print(f"[Supabase Offline Check] Connection lost or host unreachable: {e}. Disabling Supabase client to prevent future timeouts.")
        supabase_client = None

if config.USE_SUPABASE and config.SUPABASE_URL and config.SUPABASE_KEY:
    try:
        from supabase import create_client
        from supabase.client import ClientOptions
        
        # Configure a 5.0-second timeout for quick failover when offline/unreachable
        options = ClientOptions(
            postgrest_client_timeout=5.0,
            storage_client_timeout=5.0
        )
        supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY, options=options)
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Supabase client ({e}). Falling back to SQLite database mode.")
        supabase_client = None
else:
    if not config.USE_SUPABASE:
        print("Supabase is disabled by configuration. Using SQLite database mode.")
    else:
        print("Supabase credentials missing. Using SQLite database mode.")
    supabase_client = None

def db_init():
    """Initializes the database. For local fallback, creates SQLite tables."""
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception as e:
        print(f"Failed to set WAL mode: {e}")
    cursor = conn.cursor()
    
    # Drop investigations and agent_runs to recreate with Phase 5 schemas
    cursor.execute("DROP TABLE IF EXISTS investigations")
    cursor.execute("DROP TABLE IF EXISTS agent_runs")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT,
            uploaded_at TEXT,
            file_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id TEXT PRIMARY KEY,
            state TEXT,
            status TEXT,
            question TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS working_memory (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            data TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id TEXT PRIMARY KEY,
            investigation_id TEXT,
            findings TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semantic_memory (
            id TEXT PRIMARY KEY,
            concept TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            name TEXT,
            instructions TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY,
            agent_name TEXT,
            status TEXT,
            start_time TEXT,
            end_time TEXT,
            duration REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id TEXT PRIMARY KEY,
            event_type TEXT,
            severity TEXT,
            message TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id TEXT PRIMARY KEY,
            investigation_id TEXT,
            confidence_score REAL,
            accuracy_score REAL,
            completeness_score REAL,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observability_metrics (
            id TEXT PRIMARY KEY,
            metric_name TEXT,
            metric_value REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Local database initialized/verified with Memory, Skills, Security, Evaluation, and Observability tables.")

    # --- Self-Healing Logic (stale record cleanup only) ---
    # NOTE: Auto-seeding from data/ directory is intentionally DISABLED.
    # Datasets must be explicitly uploaded by the user through the Dataset Explorer.
    # This ensures that user-deleted datasets are permanently removed and never silently re-added.
    try:
        import os

        # Clean up stale local dataset records whose files no longer exist on disk
        conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, file_path FROM datasets")
        rows = cursor.fetchall()
        stale_ids = []
        for r_id, r_name, r_path in rows:
            if not r_path.startswith("supabase://") and not os.path.exists(r_path):
                stale_ids.append(r_id)
        if stale_ids:
            print(f"[Self-Healing] Found {len(stale_ids)} stale local dataset records. Removing them.")
            for s_id in stale_ids:
                cursor.execute("DELETE FROM datasets WHERE id = ?", (s_id,))
            conn.commit()
        conn.close()
    except Exception as ex:
        print(f"[Self-Healing] Error during stale record cleanup: {ex}")


def insert_investigation(investigation_id: str, question: str, status: str):
    """Inserts a new investigation record."""
    created_at = datetime.datetime.utcnow().isoformat()
    if supabase_client:
        try:
            supabase_client.table("investigations").insert({
                "id": investigation_id,
                "question": question,
                "status": status,
                "state": status,
                "created_at": created_at
            }).execute()
            print("Successfully inserted investigation into Supabase.")
            return True
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to insert investigation into Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigations (id, state, status, question, created_at) VALUES (?, ?, ?, ?, ?)",
        (investigation_id, status, status, question, created_at)
    )
    conn.commit()
    conn.close()
    print("Successfully inserted investigation locally.")
    return True

def update_investigation_status(investigation_id: str, status: str):
    """Updates the status of an investigation."""
    if supabase_client:
        try:
            supabase_client.table("investigations").update({
                "status": status
            }).eq("id", investigation_id).execute()
            print("Successfully updated investigation status in Supabase.")
            return True
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to update investigation status in Supabase: {e}. Updating locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE investigations SET status = ? WHERE id = ?",
        (status, investigation_id)
    )
    conn.commit()
    conn.close()
    print("Successfully updated investigation status locally.")
    return True

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
            _handle_supabase_error(e)
            print(f"Failed to insert into Supabase: {e}. Writing to local database.")
            
    # Local fallback
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets (id, name, uploaded_at, file_path) VALUES (?, ?, ?, ?)",
        (dataset_id, name, uploaded_at, file_path)
    )
    conn.commit()
    conn.close()
    print("Successfully inserted dataset metadata locally.")
    return True

def db_delete_dataset(dataset_id: str) -> bool:
    """Deletes dataset metadata record."""
    if supabase_client:
        try:
            supabase_client.table("datasets").delete().eq("id", dataset_id).execute()
            print("Successfully deleted dataset metadata from Supabase.")
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to delete from Supabase: {e}. Deleting from local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
    conn.commit()
    conn.close()
    print("Successfully deleted dataset metadata locally.")
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
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
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

def get_dataset_by_name(name: str):
    """Retrieves dataset metadata matching name (case-insensitive, prioritized exact matching, partial matching, ordered by most recent)."""
    clean_name = name.lower().replace(".csv", "").strip()
    
    # ── 1. EXACT MATCH PRIORITIZATION ─────────────────────────────────────────
    # Try exact match (case-insensitive) first (e.g. name = 'sales' or 'sales.csv')
    if supabase_client:
        try:
            for candidate in [clean_name, f"{clean_name}.csv"]:
                response = supabase_client.table("datasets").select("*").ilike("name", candidate).order("uploaded_at", desc=True).execute()
                if response.data:
                    return response.data[0]
        except Exception as e:
            print(f"Supabase exact lookup failed: {e}. Checking local database.")
            
    try:
        conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, uploaded_at, file_path FROM datasets WHERE LOWER(name) = ? OR LOWER(name) = ? ORDER BY uploaded_at DESC",
            (clean_name, f"{clean_name}.csv")
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "uploaded_at": row[2],
                "file_path": row[3]
            }
    except Exception as e:
        print(f"SQLite exact lookup failed: {e}")

    # ── 2. CLEAN PREFIX MATCHING (Exclude test fixtures unless queried) ───────
    # Skip _empty, _missing, _clean unless they are specifically in the query name
    if not any(x in clean_name for x in ["empty", "missing", "clean"]):
        if supabase_client:
            try:
                response = supabase_client.table("datasets").select("*") \
                    .ilike("name", f"{clean_name}%") \
                    .not_.ilike("name", "%_empty%") \
                    .not_.ilike("name", "%_missing%") \
                    .order("uploaded_at", desc=True).execute()
                if response.data:
                    return response.data[0]
            except Exception:
                pass

        try:
            conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, uploaded_at, file_path FROM datasets WHERE name LIKE ? AND name NOT LIKE '%_empty%' AND name NOT LIKE '%_missing%' ORDER BY uploaded_at DESC",
                (f"{clean_name}%",)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "uploaded_at": row[2],
                    "file_path": row[3]
                }
        except Exception:
            pass

    # ── 3. FALLBACK PREFIX MATCHING (Original logic) ──────────────────────────
    if supabase_client:
        try:
            response = supabase_client.table("datasets").select("*").ilike("name", f"{clean_name}%").order("uploaded_at", desc=True).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            print(f"Supabase query by name failed: {e}. Checking local database.")
            
    try:
        conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, uploaded_at, file_path FROM datasets WHERE name LIKE ? ORDER BY uploaded_at DESC", (f"{clean_name}%",))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "uploaded_at": row[2],
                "file_path": row[3]
            }
    except Exception:
        pass
        
    # ── 4. SELF-HEALING FALLBACK LOGIC ────────────────────────────────────────
    alternative_keywords = []
    if "sale" in clean_name or "rev" in clean_name or "forecast" in clean_name or "risk" in clean_name:
        alternative_keywords = ["sales", "revenue", "transaction", "amount", "data"]
    elif "customer" in clean_name or "churn" in clean_name or "user" in clean_name or "segment" in clean_name:
        alternative_keywords = ["customer", "churn", "client", "user", "segment"]
        
    for kw in alternative_keywords:
        if supabase_client:
            try:
                response = supabase_client.table("datasets").select("*").ilike("name", f"%{kw}%").order("uploaded_at", desc=True).execute()
                if response.data:
                    return response.data[0]
            except Exception:
                pass
        try:
            conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, uploaded_at, file_path FROM datasets WHERE name LIKE ? ORDER BY uploaded_at DESC", (f"%{kw}%",))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "uploaded_at": row[2],
                    "file_path": row[3]
                }
        except Exception:
            pass

    # Ultimate fallback: return the most recently uploaded dataset
    all_ds = db_get_all_datasets()
    if all_ds:
        return all_ds[0]
        
    return None

def db_get_all_datasets() -> list:
    """Retrieves all uploaded datasets."""
    if supabase_client:
        try:
            response = supabase_client.table("datasets").select("*").execute()
            if response.data:
                return response.data
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Supabase query for all datasets failed: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, uploaded_at, file_path FROM datasets ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "name": row[1],
            "uploaded_at": row[2],
            "file_path": row[3]
        }
        for row in rows
    ]

def db_store_memory(category: str, key_val: str, data_val: dict):
    """
    Stores memory in the specified category table.
    Categories: 'working', 'episodic', 'semantic'
    """
    import json
    import uuid
    memory_id = str(uuid.uuid4())
    data_str = json.dumps(data_val)
    
    if supabase_client:
        try:
            if category == 'working':
                supabase_client.table("working_memory").upsert({
                    "session_id": key_val,
                    "data": data_str
                }, on_conflict="session_id").execute()
            elif category == 'episodic':
                supabase_client.table("episodic_memory").upsert({
                    "investigation_id": key_val,
                    "findings": data_str
                }, on_conflict="investigation_id").execute()
            elif category == 'semantic':
                supabase_client.table("semantic_memory").upsert({
                    "concept": key_val,
                    "content": data_str
                }, on_conflict="concept").execute()
            print(f"Stored memory under category '{category}' in Supabase.")
        except Exception as e:
            print(f"Failed to store memory under category '{category}' in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    
    if category == 'working':
        cursor.execute("SELECT id FROM working_memory WHERE session_id = ?", (key_val,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE working_memory SET data = ? WHERE session_id = ?", (data_str, key_val))
        else:
            cursor.execute("INSERT INTO working_memory (id, session_id, data) VALUES (?, ?, ?)", (memory_id, key_val, data_str))
    elif category == 'episodic':
        cursor.execute("SELECT id FROM episodic_memory WHERE investigation_id = ?", (key_val,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE episodic_memory SET findings = ? WHERE investigation_id = ?", (data_str, key_val))
        else:
            cursor.execute("INSERT INTO episodic_memory (id, investigation_id, findings) VALUES (?, ?, ?)", (memory_id, key_val, data_str))
    elif category == 'semantic':
        cursor.execute("SELECT id FROM semantic_memory WHERE concept = ?", (key_val,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE semantic_memory SET content = ? WHERE concept = ?", (data_str, key_val))
        else:
            cursor.execute("INSERT INTO semantic_memory (id, concept, content) VALUES (?, ?, ?)", (memory_id, key_val, data_str))
            
    conn.commit()
    conn.close()
    print(f"Stored memory under category '{category}' locally for key '{key_val}'")
    return True

def db_retrieve_memory(category: str, key_val: str) -> dict:
    """
    Retrieves memory from the specified category table.
    """
    import json
    if supabase_client:
        try:
            response = None
            if category == 'working':
                response = supabase_client.table("working_memory").select("data").eq("session_id", key_val).execute()
            elif category == 'episodic':
                response = supabase_client.table("episodic_memory").select("findings").eq("investigation_id", key_val).execute()
            elif category == 'semantic':
                response = supabase_client.table("semantic_memory").select("content").eq("concept", key_val).execute()
                
            if response and response.data:
                field = "data" if category == 'working' else ("findings" if category == 'episodic' else "content")
                return json.loads(response.data[0][field])
        except Exception as e:
            print(f"Failed to retrieve memory under category '{category}' from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    
    row = None
    if category == 'working':
        cursor.execute("SELECT data FROM working_memory WHERE session_id = ?", (key_val,))
        row = cursor.fetchone()
    elif category == 'episodic':
        cursor.execute("SELECT findings FROM episodic_memory WHERE investigation_id = ?", (key_val,))
        row = cursor.fetchone()
    elif category == 'semantic':
        cursor.execute("SELECT content FROM semantic_memory WHERE concept = ?", (key_val,))
        row = cursor.fetchone()
        
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return None

def db_store_skill(name: str, instructions: str):
    """Stores or updates agentic skills."""
    import uuid
    skill_id = str(uuid.uuid4())
    
    if supabase_client:
        try:
            supabase_client.table("skills").upsert({
                "name": name,
                "instructions": instructions
            }, on_conflict="name").execute()
            print(f"Stored skill '{name}' in Supabase.")
        except Exception as e:
            print(f"Failed to store skill '{name}' in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM skills WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE skills SET instructions = ? WHERE name = ?", (instructions, name))
    else:
        cursor.execute("INSERT INTO skills (id, name, instructions) VALUES (?, ?, ?)", (skill_id, name, instructions))
    conn.commit()
    conn.close()
    return True

def db_get_skill(name: str) -> str:
    """Retrieves instructions for a skill by name."""
    if supabase_client:
        try:
            response = supabase_client.table("skills").select("instructions").eq("name", name).execute()
            if response.data:
                return response.data[0]["instructions"]
        except Exception as e:
            print(f"Failed to retrieve skill '{name}' from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT instructions FROM skills WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def db_store_security_event(event_type: str, severity: str, message: str) -> bool:
    """Logs a security event to the security_events table."""
    import uuid
    event_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat()
    
    if supabase_client:
        try:
            supabase_client.table("security_events").insert({
                "id": event_id,
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "created_at": created_at
            }).execute()
            print(f"Logged security event '{event_type}' in Supabase.")
        except Exception as e:
            print(f"Failed to log security event in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO security_events (id, event_type, severity, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (event_id, event_type, severity, message, created_at)
    )
    conn.commit()
    conn.close()
    print(f"Logged security event '{event_type}' ({severity}) locally.")
    return True

def db_store_evaluation(investigation_id: str, confidence: float, accuracy: float, completeness: float) -> bool:
    """Logs evaluation scores to the evaluations table."""
    import uuid
    eval_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat()
    
    if supabase_client:
        try:
            supabase_client.table("evaluations").insert({
                "id": eval_id,
                "investigation_id": investigation_id,
                "confidence_score": confidence,
                "accuracy_score": accuracy,
                "completeness_score": completeness,
                "created_at": created_at
            }).execute()
            print(f"Logged evaluation in Supabase.")
        except Exception as e:
            print(f"Failed to log evaluation in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO evaluations (id, investigation_id, confidence_score, accuracy_score, completeness_score, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (eval_id, investigation_id, confidence, accuracy, completeness, created_at)
    )
    conn.commit()
    conn.close()
    print(f"Logged evaluation metrics for investigation '{investigation_id}' locally.")
    return True

def db_get_average_evaluations() -> dict:
    """Computes average metrics across all stored evaluations."""
    if supabase_client:
        try:
            response = supabase_client.table("evaluations").select("confidence_score, accuracy_score, completeness_score").execute()
            if response.data and len(response.data) > 0:
                import pandas as pd
                df_evals = pd.DataFrame(response.data)
                if not df_evals.empty:
                    return {
                        "avg_confidence": round(df_evals["confidence_score"].mean(), 2),
                        "avg_accuracy": round(df_evals["accuracy_score"].mean(), 2),
                        "avg_completeness": round(df_evals["completeness_score"].mean(), 2),
                        "total_runs": len(df_evals)
                    }
        except Exception as e:
            print(f"Failed to get average evaluations from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(confidence_score), AVG(accuracy_score), AVG(completeness_score), COUNT(*) FROM evaluations")
    row = cursor.fetchone()
    conn.close()
    if row and row[3] > 0:
        return {
            "avg_confidence": round(row[0], 2),
            "avg_accuracy": round(row[1], 2),
            "avg_completeness": round(row[2], 2),
            "total_runs": row[3]
        }
    return {
        "avg_confidence": 0.0,
        "avg_accuracy": 0.0,
        "avg_completeness": 0.0,
        "total_runs": 0
    }

def update_investigation_state(investigation_id: str, state: str) -> bool:
    """Updates the state and status of an investigation."""
    if supabase_client:
        try:
            supabase_client.table("investigations").update({
                "state": state,
                "status": state
            }).eq("id", investigation_id).execute()
            print(f"Investigation '{investigation_id}' state updated to '{state}' in Supabase.")
        except Exception as e:
            print(f"Failed to update investigation state in Supabase: {e}. Updating locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE investigations SET state = ?, status = ? WHERE id = ?",
        (state, state, investigation_id)
    )
    conn.commit()
    conn.close()
    print(f"Investigation '{investigation_id}' state updated to '{state}' locally.")
    return True

def db_store_agent_run(run_id: str, agent_name: str, status: str, start_time: str, end_time: str = None, duration: float = 0.0) -> bool:
    """Logs/updates agent runs in the agent_runs table."""
    if supabase_client:
        try:
            supabase_client.table("agent_runs").upsert({
                "id": run_id,
                "agent_name": agent_name,
                "status": status,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration
            }, on_conflict="id").execute()
            print(f"Logged agent run '{agent_name}' ({status}) in Supabase.")
        except Exception as e:
            print(f"Failed to log agent run in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM agent_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE agent_runs SET status = ?, end_time = ?, duration = ? WHERE id = ?",
            (status, end_time, duration, run_id)
        )
    else:
        cursor.execute(
            "INSERT INTO agent_runs (id, agent_name, status, start_time, end_time, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, agent_name, status, start_time, end_time, duration)
        )
    conn.commit()
    conn.close()
    return True

def db_store_observability_metric(metric_name: str, metric_value: float) -> bool:
    """Stores an observability metric (e.g. latency, token count, success)."""
    import uuid
    metric_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()
    
    if supabase_client:
        try:
            supabase_client.table("observability_metrics").insert({
                "id": metric_id,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "timestamp": timestamp
            }).execute()
            print(f"Logged observability metric '{metric_name}' in Supabase.")
        except Exception as e:
            print(f"Failed to log observability metric in Supabase: {e}. Writing locally.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO observability_metrics (id, metric_name, metric_value, timestamp) VALUES (?, ?, ?, ?)",
        (metric_id, metric_name, metric_value, timestamp)
    )
    conn.commit()
    conn.close()
    return True

def db_get_observability_averages() -> dict:
    """Calculates average latency and success counts for dashboard observability."""
    if supabase_client:
        try:
            run_resp = supabase_client.table("agent_runs").select("duration").eq("status", "COMPLETED").execute()
            sec_resp = supabase_client.table("security_events").select("id").execute()
            
            if run_resp.data and len(run_resp.data) > 0 and sec_resp.data is not None:
                import pandas as pd
                df_runs = pd.DataFrame(run_resp.data)
                avg_duration = round(df_runs["duration"].mean() if not df_runs.empty else 0.0, 2)
                return {
                    "avg_agent_duration": avg_duration,
                    "total_agent_runs": len(df_runs),
                    "total_security_events": len(sec_resp.data)
                }
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to calculate observability averages from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(duration), COUNT(*) FROM agent_runs WHERE status='COMPLETED'")
    run_row = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM security_events")
    sec_row = cursor.fetchone()
    conn.close()
    return {
        "avg_agent_duration": round(run_row[0] or 0.0, 2),
        "total_agent_runs": run_row[1] or 0,
        "total_security_events": sec_row[0] or 0
    }

def db_get_agent_runs() -> list:
    """Retrieves detailed logs of all agent runs."""
    if supabase_client:
        try:
            response = supabase_client.table("agent_runs").select("id, agent_name, status, start_time, end_time, duration").order("start_time", desc=True).execute()
            if response.data and len(response.data) > 0:
                return response.data
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to retrieve agent runs from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, agent_name, status, start_time, end_time, duration FROM agent_runs ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "agent_name": row[1],
            "status": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "duration": row[5]
        }
        for row in rows
    ]

def db_get_investigations() -> list:
    """Retrieves all investigation history states."""
    if supabase_client:
        try:
            response = supabase_client.table("investigations").select("id, state, status, question, created_at").order("created_at", desc=True).execute()
            if response.data and len(response.data) > 0:
                return response.data
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to retrieve investigations from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, state, status, question, created_at FROM investigations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "state": row[1],
            "status": row[2],
            "question": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

def db_get_security_events() -> list:
    """Retrieves all logged security events."""
    if supabase_client:
        try:
            response = supabase_client.table("security_events").select("id, event_type, severity, message, created_at").order("created_at", desc=True).execute()
            if response.data and len(response.data) > 0:
                return response.data
        except Exception as e:
            _handle_supabase_error(e)
            print(f"Failed to retrieve security events from Supabase: {e}. Checking local database.")
            
    conn = sqlite3.connect(config.DB_PATH, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_type, severity, message, created_at FROM security_events ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "event_type": row[1],
            "severity": row[2],
            "message": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

