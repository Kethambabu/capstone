import io
import pandas as pd
from backend.services import dataset_service

def load_dataset(dataset_id: str) -> str:
    """
    Loads a dataset CSV by ID and returns a summary description, 
    including columns, shape, and head.
    
    Args:
        dataset_id: The unique identifier of the dataset.
        
    Returns:
        A text summary description of the dataset structure and sample rows.
    """
    try:
        content = dataset_service.get_dataset_content(dataset_id)
        # Load into pandas
        df = pd.read_csv(io.BytesIO(content))
        
        # Build a textual summary
        summary = []
        summary.append(f"Dataset ID: {dataset_id}")
        summary.append(f"Columns: {', '.join(df.columns.tolist())}")
        summary.append(f"Total Rows: {len(df)}")
        summary.append(f"Total Columns: {len(df.columns)}")
        summary.append("\nFirst 5 Rows of Data:")
        summary.append(df.head(5).to_markdown(index=False))
        
        summary_text = "\n".join(summary)
        print("Tool load_dataset executed successfully.")
        return summary_text
    except Exception as e:
        err_msg = f"Error loading dataset {dataset_id}: {str(e)}"
        print(err_msg)
        return err_msg
