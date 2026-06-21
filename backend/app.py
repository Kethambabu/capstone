import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.supabase import db_init
from backend.api import upload, analysis

app = FastAPI(title="Boardroom AI Backend", version="0.1.0")

# Setup CORS to allow cross-origin requests (e.g. from frontend dev servers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(upload.router)
app.include_router(analysis.router)

@app.on_event("startup")
async def startup_event():
    # Setup local SQLite db if Supabase fallback is needed
    db_init()

@app.get("/")
def read_root():
    return {"message": "Boardroom AI API is running"}

if __name__ == "__main__":
    # Start uvicorn server on port 8000
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
