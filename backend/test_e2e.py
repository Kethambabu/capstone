import os
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from backend.app import app
from backend.database.supabase import db_init

def create_mock_csv():
    csv_data = """Date,Region,Product Category,Revenue
2026-01-01,East,Product Category A,10000
2026-01-01,East,Product Category B,15000
2026-02-01,East,Product Category A,11000
2026-02-01,East,Product Category B,16000
2026-03-01,East,Product Category A,12000
2026-03-01,East,Product Category B,17000
2026-04-01,East,Product Category A,13000
2026-04-01,East,Product Category B,18000
2026-05-01,East,Product Category A,11000
2026-05-01,East,Product Category B,12000
2026-05-01,West,Product Category A,14000
2026-06-01,East,Product Category A,13500
2026-06-01,East,Product Category B,18500
"""
    return csv_data.encode("utf-8")

def run_test():
    print("Initializing test database...")
    db_init()
    
    client = TestClient(app)
    
    # 1. Test Root
    print("Testing GET / ...")
    response = client.get("/")
    print("Status:", response.status_code)
    print("Response:", response.json())
    assert response.status_code == 200
    
    # 2. Test Upload
    print("\nTesting POST /upload ...")
    csv_bytes = create_mock_csv()
    files = {"file": ("sales.csv", csv_bytes, "text/csv")}
    response = client.post("/upload", files=files)
    print("Status:", response.status_code)
    print("Response:", response.json())
    assert response.status_code == 200
    dataset_id = response.json()["dataset_id"]
    print("Dataset ID:", dataset_id)
    
    # 3. Test Analyze
    print("\nTesting POST /analyze ...")
    payload = {
        "dataset_id": dataset_id,
        "question": "Why did revenue drop in May?"
    }
    response = client.post("/analyze", json=payload)
    print("Status:", response.status_code)
    assert response.status_code == 200
    report = response.json()["report"]
    print("\n--- GENERATED REPORT ---")
    print(report)
    print("------------------------")
    
    print("\nE2E Verification SUCCESS!")

if __name__ == "__main__":
    run_test()
