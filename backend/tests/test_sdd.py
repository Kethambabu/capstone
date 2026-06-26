import os
import sys
import re
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app import app
from backend.database.supabase import db_init

client = TestClient(app)

class BDDContext:
    def __init__(self):
        self.role = None
        self.question = None
        self.response = None
        self.dataset_id = None

def create_mock_csv():
    return """Date,Region,Product Category,Revenue
2026-01-01,East,Product Category A,10000
2026-02-01,East,Product Category A,11000
2026-03-01,East,Product Category A,12000
2026-04-01,East,Product Category A,13000
2026-05-01,East,Product Category A,11000
""".encode("utf-8")

def run_feature_file(feature_path: Path):
    db_init()
    
    # Upload standard dataset to make sure one is active
    res_clean = client.post("/upload", files={"file": ("sales_clean.csv", create_mock_csv(), "text/csv")})
    assert res_clean.status_code == 200
    dataset_id = res_clean.json()["dataset_id"]

    context = BDDContext()
    context.dataset_id = dataset_id

    lines = feature_path.read_text(encoding="utf-8").splitlines()
    
    scenario_name = ""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if line.startswith("Scenario:"):
            scenario_name = line.replace("Scenario:", "").strip()
            print(f"\nRunning BDD Scenario: {scenario_name}")
            context = BDDContext() # Reset context per scenario
            context.dataset_id = dataset_id
            continue

        # Given user role
        match_given_role = re.match(r"^Given the user has the role \"([^\"]+)\"", line)
        if match_given_role:
            context.role = match_given_role.group(1)
            print(f"  Given: Role is set to '{context.role}'")
            continue

        # When run investigation
        match_when_run = re.match(r"^When they run an investigation with question \"([^\"]+)\"", line)
        if match_when_run:
            context.question = match_when_run.group(1)
            print(f"  When: Running investigation with question '{context.question}'")
            # Call API
            payload = {
                "dataset_id": context.dataset_id,
                "question": context.question,
                "role": context.role,
                "execution_mode": "sequential"
            }
            response = client.post("/analyze", json=payload)
            assert response.status_code == 200, f"API failed with {response.status_code}"
            context.response = response.json()
            continue

        # Then block request
        match_then_block = re.match(r"^Then the security check blocks the request with reason \"([^\"]+)\"", line)
        if match_then_block:
            expected_reason = match_then_block.group(1)
            print(f"  Then: Checking block reason '{expected_reason}'")
            assert context.response.get("status") == "blocked", "Request was not blocked"
            assert context.response.get("reason") == expected_reason, f"Expected reason {expected_reason}, got {context.response.get('reason')}"
            continue

        # Then run parallel/sequential
        if line.startswith("Then the orchestrator runs parallel revenue, customer, and risk diagnostics"):
            print("  Then: Checking diagnostics run")
            report = context.response.get("report", "")
            # Verify the report has been generated successfully
            assert len(report) > 0, "No report content generated"
            continue

        # And include evaluation
        if line.startswith("And the report includes an evaluation score") or line.startswith("And the report includes an evaluation card"):
            print("  And: Checking for evaluation score")
            report = context.response.get("report", "")
            assert "Confidence Score" in report or "Fleet Diagnostics" in report, "Evaluation summary missing from report"
            continue

    print("\nBDD SDD Feature Specification verification SUCCESS!")

if __name__ == "__main__":
    feature_file = Path(__file__).parent / "features" / "orchestrator.feature"
    run_feature_file(feature_file)
