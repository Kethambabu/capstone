import time
import datetime
import uuid
from backend.database import supabase

async def run_agent_with_ops(agent_name: str, agent_coro) -> any:
    """
    AgentOps runtime wrapper.
    Tracks start/end timestamps, calculates duration, and writes agent_runs + observability_metrics.
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.datetime.utcnow().isoformat()
    start_ts = time.time()
    
    print(f"[ADK TRACE] {agent_name} Started")
    supabase.db_store_agent_run(run_id, agent_name, "RUNNING", start_time, None, 0.0)
    
    status = "COMPLETED"
    try:
        # Check if agent_coro is a coroutine or standard callable
        import inspect
        if inspect.iscoroutinefunction(agent_coro) or inspect.iscoroutine(agent_coro):
            result = await agent_coro()
        elif callable(agent_coro):
            result = agent_coro()
        else:
            result = await agent_coro
        return result
    except Exception as e:
        status = "FAILED"
        raise e
    finally:
        end_time = datetime.datetime.utcnow().isoformat()
        duration = time.time() - start_ts
        print(f"[ADK TRACE] {agent_name} Completed in {duration:.2f} seconds")
        
        # Log run details to SQLite db
        supabase.db_store_agent_run(run_id, agent_name, status, start_time, end_time, duration)
        
        # Store observability metrics
        supabase.db_store_observability_metric(f"{agent_name}_duration", duration)
        supabase.db_store_observability_metric(f"{agent_name}_status_{status}", 1.0)
