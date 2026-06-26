# Task List - Fix API Key Rotation Daily Exhaustion Bug and Verify Datasets

- [x] Fix `backend/services/gemini_client_service.py` API Key Rotation cooldown logic.
- [x] Apply print redirection patch to `mcp_server/server.py` to prevent stdout corruption of the MCP stdio transport.
- [x] Increase `max_attempts` in `backend/services/gemini_client_service.py` to handle concurrent rate limits gracefully.
- [x] Run `python scratch/run_playground_query.py` to verify key pool, retry delay, and dataset queries.
- [x] Restart ADK playground and verify datasets load successfully in the UI.

