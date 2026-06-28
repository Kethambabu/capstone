"""
Boardroom AI — Full-Stack Diagnostic: 7 Sample Queries
Run from project root:  python backend/run_diagnostics.py
"""

import requests
import json
import time
import sys

BASE = "http://localhost:8000"
TIMEOUT = 90

SAMPLE_QUERIES = [
    # (description, question, role, mode)
    ("Q1 — Revenue drop analysis",    "Why did revenue drop in May?",                          "Admin",     "quota_saver"),
    ("Q2 — Top performing region",    "Which region had the highest sales in June?",            "Executive", "quota_saver"),
    ("Q3 — Customer churn deep-dive", "What is the churn rate for premium customers?",          "Admin",     "quota_saver"),
    ("Q4 — Revenue forecast",         "What is the revenue forecast for the next quarter?",     "Executive", "quota_saver"),
    ("Q5 — Risk anomaly detection",   "Are there any anomalies or risk alerts in the dataset?", "Admin",     "quota_saver"),
    ("Q6 — Product category perf",    "Which product category performed worst in 2026?",        "Executive", "quota_saver"),
    ("Q7 — Comprehensive overview",   "Give me a complete business review of all KPIs",         "Admin",     "quota_saver"),
]


SEP = "═" * 70


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t): return color(t, "92")
def red(t):   return color(t, "91")
def yellow(t):return color(t, "93")
def cyan(t):  return color(t, "96")
def bold(t):  return color(t, "1")


def get_datasets():
    try:
        r = requests.get(f"{BASE}/datasets", timeout=10)
        datasets = r.json()
        if datasets:
            return datasets
    except Exception as e:
        print(red(f"  ✗ Could not fetch datasets: {e}"))
    return []


def check_telemetry():
    print(f"\n{bold(cyan('── Fleet Telemetry Snapshot ──────────────────────────────────'))}")
    try:
        stats = requests.get(f"{BASE}/api/observability/stats", timeout=8).json()
        runs  = requests.get(f"{BASE}/api/observability/runs",  timeout=8).json()
        invs  = requests.get(f"{BASE}/api/observability/investigations", timeout=8).json()
        secs  = requests.get(f"{BASE}/api/observability/security_events", timeout=8).json()

        print(f"  Agent Runs Logged    : {green(str(len(runs)))}")
        print(f"  Investigations       : {green(str(len(invs)))}")
        print(f"  Security Events      : {yellow(str(len(secs)))}")
        print(f"  Avg Agent Duration   : {stats.get('avg_agent_duration', 0):.2f}s")
        print(f"  Total API Cost       : ${stats.get('total_api_cost_usd', 0):.4f}")
        print(f"  Total Input Tokens   : {stats.get('total_input_tokens', 0):,}")
        print(f"  Total Output Tokens  : {stats.get('total_output_tokens', 0):,}")
        print(f"  Model                : {stats.get('configured_model', 'N/A')}")

        if runs:
            print(f"\n  {bold('Recent Agent Runs:')}")
            for r in runs[:8]:
                status_sym = "🟢" if r.get("status") == "COMPLETED" else ("⚪" if r.get("status") == "SKIPPED" else "🔵")
                dur = f"{float(r.get('duration') or 0):.2f}s"
                print(f"    {status_sym} {r.get('agent_name','?'):<22} {r.get('status','?'):<12} {dur}")
    except Exception as e:
        print(red(f"  ✗ Telemetry fetch failed: {e}"))


def run_query(label, question, dataset_id, role, mode):
    print(f"\n{SEP}")
    print(bold(f"  {label}"))
    print(f"  Question : {cyan(question)}")
    print(f"  Role     : {role}   Mode: {mode}")
    print(SEP)

    payload = {
        "dataset_id": dataset_id,
        "question":   question,
        "role":       role,
        "execution_mode": mode
    }

    t0 = time.time()
    try:
        resp = requests.post(f"{BASE}/analyze", json=payload, timeout=TIMEOUT)
        elapsed = time.time() - t0
    except requests.exceptions.Timeout:
        print(red(f"  ✗ TIMEOUT after {TIMEOUT}s"))
        return {"error": "timeout"}
    except Exception as e:
        print(red(f"  ✗ Request failed: {e}"))
        return {"error": str(e)}

    if resp.status_code != 200:
        print(red(f"  ✗ HTTP {resp.status_code}: {resp.text[:300]}"))
        return {"error": f"HTTP {resp.status_code}"}

    data = resp.json()
    elapsed_str = f"{elapsed:.1f}s"

    # ── Status ───────────────────────────────────────────────────────────
    if data.get("status") == "blocked":
        print(yellow(f"  ⚠ BLOCKED — {data.get('reason', '?')}"))
        print(f"  {data.get('report','')[:200]}")
        return data

    report    = data.get("report", "")
    ui_hints  = data.get("ui_hints", [])
    cache_hit = "[CACHE" in str(data)  # heuristic

    print(green(f"  ✓ Response received in {elapsed_str}"))

    # ── Report preview ───────────────────────────────────────────────────
    print(f"\n  {bold('Report Preview (first 500 chars):')}")
    preview = report.replace("\n", " ").strip()[:500]
    print(f"  {preview}…")

    # ── UI Hints / Charts ────────────────────────────────────────────────
    kpi_cards  = [h for h in ui_hints if h.get("type") == "kpi_card"]
    charts     = [h for h in ui_hints if h.get("type") not in ("kpi_card",)]

    print(f"\n  {bold('UI Hints:')}")
    print(f"    KPI Cards  : {green(str(len(kpi_cards)))} — {[k.get('label') for k in kpi_cards]}")
    print(f"    Charts     : {green(str(len(charts)))} — {[c.get('type') for c in charts]}")

    if not charts:
        print(yellow("    ⚠ NO CHARTS generated — fallback may have failed"))

    # ── Chart data sample ────────────────────────────────────────────────
    for c in charts[:3]:
        data_rows = c.get("data", [])
        print(f"    [{c.get('type')}] '{c.get('title')}' — {len(data_rows)} rows")
        if data_rows:
            print(f"      Sample row: {data_rows[0]}")

    # ── Key KPI values ───────────────────────────────────────────────────
    if kpi_cards:
        print(f"\n  {bold('KPI Values:')}")
        for k in kpi_cards:
            print(f"    {k.get('label'):<30} = {green(str(k.get('value')))}")

    return {"ok": True, "charts": len(charts), "kpis": len(kpi_cards), "elapsed": elapsed}


def main():
    print(f"\n{bold(cyan(SEP))}")
    print(bold(cyan("  BOARDROOM AI — FULL DIAGNOSTIC: 7 SAMPLE QUERIES")))
    print(bold(cyan(SEP)))

    # 1. Health check
    print(f"\n{bold('Step 1: Backend health check')}")
    try:
        h = requests.get(f"{BASE}/health", timeout=5)
        print(green(f"  ✓ Backend alive — {h.text[:80]}"))
    except Exception:
        # try root
        try:
            h = requests.get(f"{BASE}/", timeout=5)
            print(green(f"  ✓ Backend alive (root) — status {h.status_code}"))
        except Exception as e:
            print(red(f"  ✗ Backend not reachable: {e}"))
            sys.exit(1)

    # 2. Dataset check
    print(f"\n{bold('Step 2: Available datasets')}")
    datasets = get_datasets()
    if not datasets:
        print(red("  ✗ No datasets found. Please upload a CSV first."))
        sys.exit(1)

    sales_id = None
    sales_name = None
    customers_id = None
    customers_name = None
    
    for d in datasets:
        d_name = d.get("name", "").lower()
        if "sales" in d_name and not sales_id:
            sales_id = d.get("id")
            sales_name = d.get("name")
        elif "customer" in d_name and not customers_id:
            customers_id = d.get("id")
            customers_name = d.get("name")
            
    # Fallback to the first available if not found
    if not sales_id:
        sales_id = datasets[0]["id"]
        sales_name = datasets[0]["name"]
    if not customers_id:
        customers_id = datasets[0]["id"]
        customers_name = datasets[0]["name"]
        
    print(green(f"  ✓ Found Sales Dataset: '{sales_name}' (ID: {sales_id[:8]}…)"))
    print(green(f"  ✓ Found Customers Dataset: '{customers_name}' (ID: {customers_id[:8]}…)"))

    # 3. Intent service check (quick local test)
    print(f"\n{bold('Step 3: Intent service local check')}")
    import os, sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from backend.services.intent_service import detect_intent_local
        for q, expected_cat in [
            ("Why did revenue drop in May?", "revenue"),
            ("What is the churn rate for premium customers?", "customer"),
            ("What is the revenue forecast for next quarter?", "forecast"),
            ("Are there any risk anomalies?", "risk"),
        ]:
            res = detect_intent_local(q)
            cat = res["primary_category"]
            ctx = res["need_more_context"]
            ok  = cat == expected_cat
            sym = green("✓") if ok else red("✗")
            print(f"  {sym} '{q[:50]}' → {cat} (need_context={ctx})")
    except Exception as e:
        print(yellow(f"  ⚠ Intent service test skipped: {e}"))

    # 4. Run 7 queries
    print(f"\n{bold('Step 4: Running 7 sample queries')}")
    results = []
    for label, question, role, mode in SAMPLE_QUERIES:
        q_lower = question.lower()
        if "customer" in q_lower or "churn" in q_lower:
            ds_id = customers_id
        else:
            ds_id = sales_id
        r = run_query(label, question, ds_id, role, mode)
        results.append((label, r))
        time.sleep(0.5)  # small pause between queries

    # 5. Telemetry after all queries
    check_telemetry()

    # 6. Summary
    print(f"\n{SEP}")
    print(bold("  DIAGNOSTIC SUMMARY"))
    print(SEP)
    ok_count    = sum(1 for _, r in results if r.get("ok"))
    chart_total = sum(r.get("charts", 0) for _, r in results if r.get("ok"))
    errors      = [(l, r.get("error")) for l, r in results if r.get("error")]

    print(f"  Queries passed  : {green(str(ok_count))}/{len(results)}")
    print(f"  Charts generated: {green(str(chart_total))} total across all queries")

    if errors:
        print(f"\n  {red('FAILURES:')}")
        for label, err in errors:
            print(f"    ✗ {label}: {err}")
    else:
        print(green("  All 7 queries responded successfully!"))

    print(f"\n{SEP}\n")


if __name__ == "__main__":
    main()
