import sys
from pathlib import Path
agent_dir = Path(__file__).resolve().parent
project_root = agent_dir.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.agents.forecast.forecast_agent import forecast_agent as root_agent
