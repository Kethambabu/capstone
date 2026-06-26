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
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(override=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
USE_SUPABASE = os.environ.get("USE_SUPABASE", "True").lower() in ("true", "1", "yes")

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

# --- Token Management Settings ---
# Primary and fallback model configuration
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_FALLBACK_MODEL = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash")

# Output Token Limits (to control generation verbosity and save cost)
MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "2000"))

# Maximum length of characters allowed for context elements before truncation
MAX_SKILL_INSTRUCTION_CHARS = int(os.environ.get("MAX_SKILL_INSTRUCTION_CHARS", "2000"))
MAX_WORKING_MEMORY_CHARS = int(os.environ.get("MAX_WORKING_MEMORY_CHARS", "1000"))
MAX_EPISODIC_MEMORY_CHARS = int(os.environ.get("MAX_EPISODIC_MEMORY_CHARS", "3000"))
MAX_SEMANTIC_MEMORY_CHARS = int(os.environ.get("MAX_SEMANTIC_MEMORY_CHARS", "2000"))

def get_agent_config():
    """Returns a GenerateContentConfig with configured output token limits."""
    from google.genai import types
    return types.GenerateContentConfig(
        max_output_tokens=MAX_OUTPUT_TOKENS,
        temperature=0.1,  # Predictable business answers
        http_options=types.HttpOptions(
            retry_options=None
        )
    )

# Apply Gemini Key Pool rotation monkeypatch globally on startup
import backend.services.gemini_client_service

import contextvars
user_role_var = contextvars.ContextVar("user_role", default="Executive")



