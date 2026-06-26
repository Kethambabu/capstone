.PHONY: install playground run test

install:
	uv sync

playground:
	uv run adk web backend/agents/orchestrator --host 127.0.0.1 --port 18081 --reload_agents

run:
	uv run python -c "import subprocess, sys; p1 = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.app:app', '--host', '0.0.0.0', '--port', '8000']); p2 = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'frontend/app.py']); p1.wait(); p2.wait()"

test:
	uv run python backend/test_e2e.py
