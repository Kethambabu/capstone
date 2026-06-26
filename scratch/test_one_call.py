import os
from google.genai import Client

# Use active key from environment
key = os.environ.get("GEMINI_API_KEY")
client = Client(api_key=key)


for model_name in ["gemini-flash-latest", "gemini-2.0-flash-lite"]:
    try:
        print(f"Testing key with {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents="Hello, reply with only 'success'",
        )
        print(f"{model_name} Success:", response.text.strip())
    except Exception as e:
        print(f"{model_name} ERROR:", str(e)[:200])
