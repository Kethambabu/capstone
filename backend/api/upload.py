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
        return {"dataset_id": dataset_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload CSV: {str(e)}")
