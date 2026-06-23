import io
import pandas as pd
from backend.services import dataset_service

def load_dataset(dataset_name: str) -> str:
    """
    Loads a dataset CSV by name (e.g. 'sales' or 'customers') and returns a summary description
    including columns, shape, and sample rows.
    
    Args:
        dataset_name: The name or type of the dataset (e.g. 'sales', 'customers').
        
    Returns:
        A text summary of the dataset structure and sample rows.
    """
    try:
        content = dataset_service.get_dataset_content_by_name(dataset_name)
        df = pd.read_csv(io.BytesIO(content))
        
        summary = []
        summary.append(f"Dataset Name: {dataset_name}")
        summary.append(f"Columns: {', '.join(df.columns.tolist())}")
        summary.append(f"Total Rows: {len(df)}")
        summary.append(f"Total Columns: {len(df.columns)}")
        summary.append("\nFirst 5 Rows of Data:")
        summary.append(df.head(5).to_markdown(index=False))
        
        summary_text = "\n".join(summary)
        print(f"Tool load_dataset executed successfully for dataset '{dataset_name}'.")
        return summary_text
    except Exception as e:
        err_msg = f"Error loading dataset '{dataset_name}': {str(e)}"
        print(err_msg)
        return err_msg
