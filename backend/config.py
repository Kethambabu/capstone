import os
from pathlib import Path
from dotenv import load_dotenv

# Search for the .env file up the directory chain
current_dir = Path(__file__).resolve().parent
env_path = None
for parent in [current_dir, current_dir.parent, current_dir.parent.parent]:
    candidate = parent / ".env"
    if candidate.exists():
        env_path = candidate
        break

if env_path:
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Set Gemini API Key in the environment for google-genai / google-adk
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Local SQLite DB path (fallback)
DB_PATH = BASE_DIR / "datasets.db"

# Mock Mode if API keys are missing
MOCK_MODE = not bool(GEMINI_API_KEY)
