from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services import dataset_service

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV business dataset.
    Saves the file and registers it in the database.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    try:
        file_content = await file.read()
        dataset_id = dataset_service.create_dataset(file.filename, file_content)
        
        # Invalidate the query cache for this dataset
        try:
            from backend.api.analysis import clear_query_cache
            clear_query_cache(dataset_id)
            clear_query_cache(file.filename)
        except Exception as cache_err:
            print(f"Failed to clear cache on upload: {cache_err}")
            
        return {"dataset_id": dataset_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload CSV: {str(e)}")

@router.get("/datasets")
def list_datasets():
    """
    Endpoint to list all uploaded datasets.
    """
    try:
        from backend.database import supabase
        return supabase.db_get_all_datasets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")

@router.get("/datasets/{dataset_id}/content")
def get_dataset_content(dataset_id: str):
    """
    Endpoint to retrieve binary content of an uploaded dataset.
    """
    try:
        content = dataset_service.get_dataset_content(dataset_id)
        from fastapi.responses import Response
        return Response(content=content, media_type="text/csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dataset content: {str(e)}")


