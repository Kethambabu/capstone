import dotenv
import os
from google import genai

dotenv.load_dotenv()
keys = os.environ.get('GEMINI_API_KEY_POOL', '').split(',')
print(f"Loaded {len(keys)} keys.")
for i, k in enumerate(keys):
    try:
        client = genai.Client(api_key=k)
        res = client.models.generate_content(model='gemini-2.0-flash', contents='say hi')
        print(f"Key {i} (...{k[-8:]}): SUCCESS -> {res.text.strip()}")
    except Exception as e:
        print(f"Key {i} (...{k[-8:]}): FAILED -> {type(e).__name__}: {str(e)}")
