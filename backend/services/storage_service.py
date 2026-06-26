import os
from pathlib import Path
from backend import config
from backend.database import supabase

def upload_file(dataset_id: str, file_name: str, file_content: bytes) -> str:
    """
    Saves the file content to Supabase Storage if configured.
    Otherwise, saves it locally in the uploads/ directory.
    Returns the resolved file path (local or remote path).
    """
    # 1. Try uploading to Supabase Storage
    if supabase.supabase_client:
        try:
            # Check if bucket exists, or just try to upload
            # File path inside bucket: "dataset_id/filename.csv"
            storage_path = f"{dataset_id}/{file_name}"
            # Supabase Python SDK upload signature:
            # supabase.storage.from_('bucket').upload(path, file_bytes, file_options)
            response = supabase.supabase_client.storage.from_("datasets").upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "text/csv"}
            )
            print(f"Uploaded to Supabase storage datasets bucket: {storage_path}")
            return f"supabase://datasets/{storage_path}"
        except Exception as e:
            supabase._handle_supabase_error(e)
            print(f"Supabase storage upload failed: {e}. Falling back to local storage.")

    # 2. Local fallback
    local_path = config.UPLOAD_DIR / f"{dataset_id}_{file_name}"
    with open(local_path, "wb") as f:
        f.write(file_content)
    print(f"Saved file locally: {local_path}")
    return str(local_path)

def download_file(file_path: str) -> bytes:
    """
    Reads the file from local storage or downloads it from Supabase storage.
    Returns file content as bytes.
    """
    if file_path.startswith("supabase://"):
        if supabase.supabase_client:
            try:
                # Format: supabase://datasets/dataset_id/filename.csv
                parts = file_path.replace("supabase://", "").split("/", 1)
                bucket_name = parts[0]
                storage_path = parts[1]
                
                response = supabase.supabase_client.storage.from_(bucket_name).download(storage_path)
                return response
            except Exception as e:
                supabase._handle_supabase_error(e)
                print(f"Failed to download from Supabase storage: {e}. Checking local disk.")
        
        # If we have a supabase link but supabase client failed, try finding a local version
        # using the file path structure.
        local_filename = file_path.split("/")[-1]
        # Let's search uploads/ directory
        for f in config.UPLOAD_DIR.iterdir():
            if f.name.endswith(local_filename):
                with open(f, "rb") as file_obj:
                    return file_obj.read()
                
        raise FileNotFoundError(f"Supabase file {file_path} not found locally or remotely.")
    
    # Local path
    with open(file_path, "rb") as f:
        return f.read()
