import io
import pandas as pd
from backend.services import dataset_service

def query_data_tool(dataset: str, filters: dict = None) -> dict:
    """
    Retrieve data from the specified dataset (e.g. 'sales'), optionally applying filters.
    """
    print(f"[ADK TRACE] MCP Query Executed: query_data for dataset '{dataset}'")
    try:
        content = dataset_service.get_dataset_content_by_name(dataset)
        df = pd.read_csv(io.BytesIO(content))
        
        # Apply filters if provided
        if filters:
            for col, val in filters.items():
                col_match = None
                for c in df.columns:
                    if c.lower() == col.lower():
                        col_match = c
                        break
                if col_match:
                    df = df[df[col_match].astype(str).str.lower() == str(val).lower()]
        
        # Limit returned records to avoid exceeding LLM context window
        records = df.head(30).to_dict(orient="records")
        return {"records": records, "total_count": len(df)}
    except Exception as e:
        print(f"Error in query_data capability: {e}")
        return {"error": str(e)}
