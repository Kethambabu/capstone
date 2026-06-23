import uuid
from backend.database import supabase
from backend.services import storage_service

def create_dataset(name: str, content: bytes) -> str:
    """
    Saves the dataset file content and inserts the metadata in the database.
    Returns the newly created dataset_id.
    """
    dataset_id = str(uuid.uuid4())
    file_path = storage_service.upload_file(dataset_id, name, content)
    supabase.insert_dataset(dataset_id, name, file_path)
    return dataset_id

def get_dataset_meta(dataset_id: str) -> dict:
    """
    Retrieves metadata for the specified dataset.
    """
    meta = supabase.get_dataset(dataset_id)
    if not meta:
        raise ValueError(f"Dataset {dataset_id} not found in database.")
    return meta

def get_dataset_content(dataset_id: str) -> bytes:
    """
    Retrieves the actual binary content of the dataset.
    """
    meta = get_dataset_meta(dataset_id)
    return storage_service.download_file(meta["file_path"])

def get_dataset_by_name(name: str) -> dict:
    """
    Retrieves metadata for the dataset matching the name.
    """
    meta = supabase.get_dataset_by_name(name)
    if not meta:
        raise ValueError(f"Dataset with name matching '{name}' not found in database.")
    return meta

def get_dataset_content_by_name(name: str) -> bytes:
    """
    Retrieves dataset content by searching for the dataset name.
    """
    meta = get_dataset_by_name(name)
    return storage_service.download_file(meta["file_path"])
