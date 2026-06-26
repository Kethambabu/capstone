import os
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Reconfigure stdout to use UTF-8 encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from fastapi.testclient import TestClient
from backend.app import app
from backend.services.intent_service import detect_intent_local
from backend.database.supabase import db_init

def create_mock_csv():
    csv_data = """Date,Region,Product Category,Revenue
2026-01-01,East,Product Category A,10000
2026-01-01,East,Product Category B,15000
2026-05-01,East,Product Category A,11000
2026-05-01,East,Product Category B,12000
2026-06-01,East,Product Category A,13500
2026-06-01,East,Product Category B,18500
"""
    return csv_data.encode("utf-8")

def test_intent_detection():
    print("Testing local intent detector...")
    # Specific metric query
    res1 = detect_intent_local("What about my sales in June?")
    assert res1["primary_category"] == "revenue"
    assert res1["question_type"] == "specific_metric"
    assert res1["need_more_context"] is False
    assert res1["timeframe"] == "June"

    # Exploratory drop query
    res2 = detect_intent_local("Why did revenue drop in May?")
    assert res2["primary_category"] == "revenue"
    assert res2["question_type"] == "exploratory"
    assert res2["need_more_context"] is True

    # Customer churn query (exploratory)
    res3 = detect_intent_local("Why did customer churn rise in May?")
    assert res3["primary_category"] == "customer"
    assert res3["need_more_context"] is True

    print("Intent Detection Tests Passed!")

def test_integration_flow():
    print("Initializing database...")
    db_init()
    
    client = TestClient(app)
    
    # Upload mock sales dataset
    csv_bytes = create_mock_csv()
    files = {"file": ("sales.csv", csv_bytes, "text/csv")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    dataset_id = response.json()["dataset_id"]
    
    # Run analysis for "What about my sales in June?"
    for mode in ["quota_saver", "parallel", "sequential"]:
        print(f"Testing /analyze in '{mode}' mode for specific metric question...")
        payload = {
            "dataset_id": dataset_id,
            "question": "What about my sales in June?",
            "execution_mode": mode
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        ui_hints = data["ui_hints"]
        
        print(f"--- Mock Report ({mode}) ---")
        print(report[:400])
        print("----------------------------")
        
        # 1. Assertions on Report Structure
        assert "## 1. Direct Answer" in report or "## 1. Executive Summary" in report or "# BOARDROOM AI" in report
        assert "June" in report
        
        # 2. Assertions on Bypassed Modules (Conciseness/Token saving)
        # It should NOT contain customer churn details since customer agent was bypassed
        assert "Customer Segment & Churn Insights" not in report
        assert "Customer Agent was bypassed" in report or "bypassed" in report.lower() or "Customer Segment" not in report
        
        # 3. Assertions on Visualizations Mismatch (Only show revenue, not customer demographics)
        chart_types = [hint["type"] for hint in ui_hints]
        # It should not suggest a customer tier demographics chart (pie_chart)
        assert "pie_chart" not in chart_types
        # It should suggest a revenue card/chart
        assert any(t in chart_types for t in ["kpi_card", "bar_chart"])
        
        # 4. Assertions on Evaluation Estimate Labels
        assert "Estimate" in report or "estimate" in report.lower()
        
    print("Integration Flow Tests Passed!")

if __name__ == "__main__":
    test_intent_detection()
    test_integration_flow()
    print("All Intent Orchestration Tests Passed successfully!")
