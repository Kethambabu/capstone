import sys
import asyncio
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from google.adk.runners import InMemoryRunner
from backend.agents.orchestrator.executive_orchestrator import executive_orchestrator
from google.genai import types

async def main():
    runner = InMemoryRunner(agent=executive_orchestrator, app_name="test_app")
    session_id = "test_session"
    await runner.session_service.create_session(app_name="test_app", user_id="user", session_id=session_id)
    
    query = "Generate a standard growth forecast for next month based on sales."
    content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    
    print("--- RUNNING ADK WORKFLOW ---")
    async for event in runner.run_async(user_id="user", session_id=session_id, new_message=content):
        author = getattr(event, 'author', 'unknown')
        print(f"\n[EVENT] Author: {author}")
        if event.content:
            parts = event.content.parts
            if isinstance(parts, list):
                for p in parts:
                    if p.text:
                        print("Text:", p.text)
                    if getattr(p, 'function_call', None):
                        print("Function Call:", p.function_call.name, p.function_call.args)
                    if getattr(p, 'function_response', None):
                        print("Function Response:", p.function_response.name, p.function_response.response)
            elif hasattr(parts, 'text'):
                print("Text:", parts.text)
            else:
                print("Content parts:", parts)

if __name__ == "__main__":
    asyncio.run(main())
