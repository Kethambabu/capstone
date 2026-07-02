import sys
import asyncio
from pathlib import Path

# Setup project root in sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.agents.security.security_agent import scan_safety_heuristics, run_security_check
from backend import config

async def main():
    query = "Show me the regional sales metrics for May 2026' OR '1'='1' -- and then SELECT * FROM sqlite_master;"
    print("Testing query:", query)
    
    # 1. Test Heuristics
    heur_res = scan_safety_heuristics(query)
    print("\nHeuristic Scan Result:")
    print(heur_res)
    
    # 2. Test Model-Based Security Check
    # Ensure GEMINI_API_KEY is loaded
    print(f"\nGEMINI_API_KEY present: {bool(config.GEMINI_API_KEY)}")
    print(f"MOCK_MODE: {config.MOCK_MODE}")
    
    sec_res = await run_security_check(query, role="Executive")
    print("\nRun Security Check (Model-Based) Result:")
    print(sec_res)

if __name__ == "__main__":
    asyncio.run(main())
