import sys
import asyncio
from pathlib import Path

# Setup project root in sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from google.adk import Workflow, Event, Agent
from google.adk.runners import InMemoryRunner
from backend import config

# Define a simple agent
test_agent = Agent(
    model=config.GEMINI_FALLBACK_MODEL,
    name="test_agent",
    instruction="Translate the text to uppercase.",
    generate_content_config=config.get_agent_config()
)

# Define async node
async def async_checkpoint(node_input: str):
    print("Async checkpoint starting...")
    await asyncio.sleep(0.1)
    print("Async checkpoint finished!")
    return Event(route="CLEAN", output=node_input)

test_workflow = Workflow(
    name="test_workflow",
    edges=[
        ("START", async_checkpoint),
        (async_checkpoint, {
            "CLEAN": test_agent
        })
    ]
)

async def main():
    runner = InMemoryRunner(agent=test_workflow, app_name="test_async_workflow")
    await runner.session_service.create_session(app_name="test_async_workflow", user_id="system", session_id="s1")
    from google.genai import types
    content = types.Content(role="user", parts=[types.Part.from_text(text="hello")])
    async for event in runner.run_async(user_id="system", session_id="s1", new_message=content):
        print("Event:", event.__class__.__name__)

if __name__ == "__main__":
    asyncio.run(main())
