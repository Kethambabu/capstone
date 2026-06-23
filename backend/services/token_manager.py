import os
from backend import config

# Standard pricing for Gemini 2.5 Flash / Gemini 2.0 Flash / Gemini 1.5 Flash
INPUT_COST_PER_MILLION = 0.075  # $0.075 per 1M tokens
OUTPUT_COST_PER_MILLION = 0.30  # $0.30 per 1M tokens

_client = None

def get_genai_client():
    """Lazy initialization of the GenAI client to avoid import cycles."""
    global _client
    if _client is None and not config.MOCK_MODE:
        try:
            from google import genai
            _client = genai.Client()
        except Exception as e:
            print(f"Failed to initialize GenAI client for token counting: {e}")
    return _client

def count_tokens(text: str, model: str = None) -> int:
    """
    Counts the number of tokens in the given text using the Gemini SDK count_tokens API.
    Falls back to character-based heuristic estimation if in Mock Mode or if the API fails.
    """
    if not text:
        return 0
        
    if config.MOCK_MODE:
        # Heuristic: 1 token is roughly 4 characters
        return max(1, len(text) // 4)
        
    client = get_genai_client()
    if client:
        try:
            model_name = model or config.GEMINI_MODEL
            response = client.models.count_tokens(model=model_name, contents=text)
            return response.total_tokens
        except Exception as e:
            # Fallback on API failure
            print(f"Token count API failed: {e}. Using character heuristic fallback.")
            
    return max(1, len(text) // 4)

def track_agent_tokens(agent_name: str, prompt: str, response: str, model: str = None) -> dict:
    """
    Tracks and records the token counts and estimated costs for a specific agent execution.
    Logs metrics directly to the database.
    """
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(response, model)
    total_tokens = input_tokens + output_tokens
    
    # Compute cost in USD
    cost = ((input_tokens * INPUT_COST_PER_MILLION) + (output_tokens * OUTPUT_COST_PER_MILLION)) / 1_000_000
    
    print(f"[TOKEN MANAGER] {agent_name} consumed {input_tokens} input, {output_tokens} output tokens (Total: {total_tokens}, Est Cost: ${cost:.6f})")
    
    # Store in database
    from backend.database import supabase
    try:
        supabase.db_store_observability_metric(f"{agent_name}_input_tokens", float(input_tokens))
        supabase.db_store_observability_metric(f"{agent_name}_output_tokens", float(output_tokens))
        supabase.db_store_observability_metric(f"{agent_name}_total_tokens", float(total_tokens))
        supabase.db_store_observability_metric(f"{agent_name}_api_cost_usd", float(cost))
        
        # Store global totals for simple sum query
        supabase.db_store_observability_metric("total_input_tokens", float(input_tokens))
        supabase.db_store_observability_metric("total_output_tokens", float(output_tokens))
        supabase.db_store_observability_metric("total_api_cost_usd", float(cost))
    except Exception as db_err:
        print(f"Failed to store token metrics in database: {db_err}")
        
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost
    }

def get_cumulative_token_stats() -> dict:
    """
    Aggregates all input, output, total tokens and estimated costs across all agent executions.
    """
    from backend.database import supabase
    import sqlite3
    
    # Check if using Supabase client
    if supabase.supabase_client:
        try:
            response = supabase.supabase_client.table("observability_metrics").select("metric_name, metric_value").execute()
            if response.data:
                import pandas as pd
                df = pd.DataFrame(response.data)
                input_sum = df[df["metric_name"] == "total_input_tokens"]["metric_value"].sum()
                output_sum = df[df["metric_name"] == "total_output_tokens"]["metric_value"].sum()
                cost_sum = df[df["metric_name"] == "total_api_cost_usd"]["metric_value"].sum()
                return {
                    "total_input_tokens": int(input_sum),
                    "total_output_tokens": int(output_sum),
                    "total_tokens": int(input_sum + output_sum),
                    "total_api_cost_usd": float(cost_sum)
                }
        except Exception as e:
            print(f"Supabase token stats fetch failed: {e}. Falling back to SQLite.")
            
    # Local SQLite fallback
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(metric_value) FROM observability_metrics WHERE metric_name = 'total_input_tokens'")
        input_sum = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT SUM(metric_value) FROM observability_metrics WHERE metric_name = 'total_output_tokens'")
        output_sum = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT SUM(metric_value) FROM observability_metrics WHERE metric_name = 'total_api_cost_usd'")
        cost_sum = cursor.fetchone()[0] or 0.0
        conn.close()
        return {
            "total_input_tokens": int(input_sum),
            "total_output_tokens": int(output_sum),
            "total_tokens": int(input_sum + output_sum),
            "total_api_cost_usd": float(cost_sum)
        }
    except Exception as e:
        print(f"SQLite token stats fetch failed: {e}")
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "total_api_cost_usd": 0.0
        }
