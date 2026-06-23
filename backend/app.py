import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.supabase import db_init
from backend.api import upload, analysis
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup local SQLite db if Supabase fallback is needed
    db_init()
    yield

app = FastAPI(title="Boardroom AI Backend", version="0.1.0", lifespan=lifespan)

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

@app.get("/")
def read_root():
    return {"message": "Boardroom AI API is running"}

if __name__ == "__main__":
    # Start uvicorn server on port 8000
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
