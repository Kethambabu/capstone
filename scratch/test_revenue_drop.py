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
    session_id = "test_session_revenue_drop"
    await runner.session_service.create_session(app_name="test_app", user_id="user", session_id=session_id)
    
    query = "why my revenue drops in may"
    content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    
    print("--- RUNNING ADK WORKFLOW FOR REVENUE DROP ---")
    step_num = 0
    async for event in runner.run_async(user_id="user", session_id=session_id, new_message=content):
        step_num += 1
        author = getattr(event, 'author', 'unknown')
        print(f"\n[EVENT #{step_num}] Author: {author}")
        print(f"  is_final_response(): {event.is_final_response()}")
        print(f"  content: {event.content}")
        if event.content:
            parts = event.content.parts
            if isinstance(parts, list):
                for p in parts:
                    if p.text:
                        print("  Text:", repr(p.text))
                    if getattr(p, 'function_call', None):
                        print("  Function Call:", p.function_call.name, p.function_call.args)
                    if getattr(p, 'function_response', None):
                        print("  Function Response:", p.function_response.name, p.function_response.response)
            elif hasattr(parts, 'text'):
                print("  Text:", repr(parts.text))
            else:
                print("  Content parts:", parts)

if __name__ == "__main__":
    asyncio.run(main())
