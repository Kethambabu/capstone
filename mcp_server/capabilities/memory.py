from backend.database import supabase

def memory_tool(action: str, category: str, key: str, data: dict = None) -> dict:
    """
    Exposes reading/writing capabilities to SQLite memory tables.
    """
    print(f"[ADK TRACE] MCP Query Executed: memory for action '{action}' on category '{category}'")
    try:
        act = action.lower().strip()
        cat = category.lower().strip()
        
        if act == "store":
            if not data:
                return {"error": "Data dictionary is required for store action."}
            success = supabase.db_store_memory(cat, key, data)
            return {"status": "success", "stored": success}
            
        elif act == "retrieve":
            memory_data = supabase.db_retrieve_memory(cat, key)
            return {"status": "success", "data": memory_data}
            
        elif act == "search":
            memory_data = supabase.db_retrieve_memory(cat, key)
            return {"status": "success", "results": [memory_data] if memory_data else []}
            
        elif act == "summarize":
            memory_data = supabase.db_retrieve_memory(cat, key)
            if not memory_data:
                return {"summary": f"No memory found for key '{key}'"}
            return {"summary": f"Memory summary for '{key}': {str(memory_data)}"}
            
        else:
            return {"error": f"Unknown memory action: {action}"}
    except Exception as e:
        print(f"Error in memory capability: {e}")
        return {"error": str(e)}
