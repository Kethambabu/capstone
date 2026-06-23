# 🏛️ BOARDROOM AI — COMPLETE SYSTEM ARCHITECTURE
### From Data Ingestion → Multi-Agent Analysis → Executive Report Output

---

## 📌 TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Directory Structure](#3-directory-structure)
4. [Layer 1: Frontend (Streamlit UI)](#4-layer-1-frontend-streamlit-ui)
5. [Layer 2: Backend API (FastAPI)](#5-layer-2-backend-api-fastapi)
6. [Layer 3: Context Assembly Pipeline](#6-layer-3-context-assembly-pipeline)
7. [Layer 4: Multi-Agent Orchestration (Google ADK)](#7-layer-4-multi-agent-orchestration-google-adk)
8. [Layer 5: MCP Server (Model Context Protocol)](#8-layer-5-mcp-server-model-context-protocol)
9. [Layer 6: Agent-to-Agent (A2A) Communication](#9-layer-6-agent-to-agent-a2a-communication)
10. [Layer 7: Memory System (3-Tier)](#10-layer-7-memory-system-3-tier)
11. [Layer 8: Database & Persistence](#11-layer-8-database--persistence)
12. [Layer 9: Observability & AgentOps](#12-layer-9-observability--agentops)
13. [Layer 10: Security & RBAC](#13-layer-10-security--rbac)
14. [Complete Data Flow — End-to-End](#14-complete-data-flow--end-to-end)
15. [Configuration & Environment](#15-configuration--environment)
16. [Technology Stack Summary](#16-technology-stack-summary)
17. [State Machine Lifecycle](#17-state-machine-lifecycle)
18. [Error Handling & Fallback Chain](#18-error-handling--fallback-chain)

---

## 1. PROJECT OVERVIEW

**Boardroom AI** is a capstone-grade, production-inspired, multi-agent AI advisory platform designed for executive decision-making. It ingests enterprise CSV datasets, orchestrates a fleet of specialized AI agents, and generates structured strategic reports covering revenue diagnostics, customer churn, business risk, and revenue forecasting.

### Core Capabilities

| Capability | Technology |
|---|---|
| Multi-Agent Orchestration | Google Agent Development Kit (ADK) |
| LLM Reasoning Engine | Gemini 2.5 Flash / Gemini 1.5 Flash (fallback) |
| Tool Protocol | Model Context Protocol (MCP via FastMCP) |
| Inter-Agent Messaging | Agent-to-Agent (A2A) Protocol |
| Data Analytics | DuckDB + Pandas |
| Persistence | Supabase (cloud) / SQLite (local fallback) |
| API Layer | FastAPI (REST) |
| UI Dashboard | Streamlit |
| Observability | Custom AgentOps telemetry |

---

## 2. HIGH-LEVEL ARCHITECTURE DIAGRAM

```
+-------------------------------------------------------------------------+
|                        USER / EXECUTIVE                                  |
|                  (Web Browser via Streamlit UI)                          |
+---------------------------+---------------------------------------------+
                            |  HTTP (port 8501)
                            v
+-------------------------------------------------------------------------+
|                    FRONTEND LAYER                                         |
|               frontend/app.py  (Streamlit)                               |
|  +--------------+  +-----------------------+  +---------------------+  |
|  | Dataset Tab  |  | Multi-Agent Insights   |  | AgentOps Dashboard  |  |
|  |  (Viewer)    |  |     Tab (Analysis)     |  |  (Observability)    |  |
|  +--------------+  +-----------------------+  +---------------------+  |
+---------------------------+---------------------------------------------+
                            |  REST API calls (HTTP port 8000)
                            v
+-------------------------------------------------------------------------+
|                     BACKEND API LAYER                                     |
|                  backend/app.py  (FastAPI + Uvicorn)                     |
|  +------------------------+    +----------------------------------+      |
|  |  POST /upload          |    |  POST /analyze                   |      |
|  |  GET  /datasets        |    |  GET  /api/observability/stats   |      |
|  |  GET  /datasets/{id}   |    |  GET  /api/observability/runs    |      |
|  |       /content         |    |  GET  /api/observability/events  |      |
|  +------------------------+    +----------------------------------+      |
+---------------------------+---------------------------------------------+
                            |
           +----------------+------------------+
           v                                   v
+----------------------+         +--------------------------------------+
| CONTEXT ASSEMBLY     |         |    SECURITY CHECK (A2A)               |
| PIPELINE             |         |    security_agent (RBAC filter)       |
| - Skill Loader       |         |    allowed / blocked                   |
| - Working Memory     |         +--------------------------------------+
| - Episodic Memory    |
| - Semantic Memory    |
+----------+-----------+
           |  enriched context prompt
           v
+-------------------------------------------------------------------------+
|               ORCHESTRATION LAYER (Google ADK)                           |
|           executive_orchestrator  (gemini-2.5-flash)                     |
|              fallback: executive_orchestrator_fallback                   |
|                          (gemini-1.5-flash)                              |
|                                                                           |
|  +--------------+ +--------------+ +--------------+ +--------------+    |
|  | revenue_agent| |customer_agent| |  risk_agent  | | report_agent |    |
|  | (gemini-2.5) | | (gemini-2.5) | | (gemini-2.5) | | (gemini-2.5) |    |
|  +------+-------+ +------+-------+ +------+-------+ +------+-------+    |
|         |                |                |                |            |
|         +-----------+----+----------------+                |            |
|                     | (findings collected)                 |            |
|                     +--------------------------------------+            |
+-----------------------------------+-------------------------------------+
                                    |  MCP Tool Calls
                                    v
+-------------------------------------------------------------------------+
|                   MCP SERVER (FastMCP)                                   |
|                 mcp_server/server.py  (stdio transport)                  |
|  +------------+ +--------------+ +-------------------+ +-------------+ |
|  | query_data | | run_analysis | | generate_artifact  | |   memory    | |
|  |  tool      | |    tool      | |      tool          | |    tool     | |
|  +------------+ +--------------+ +-------------------+ +-------------+ |
+-----------------------------------+-------------------------------------+
                                    |
              +---------------------+--------------------+
              v                     v                    v
  +--------------------+ +------------------+ +----------------------+
  |  DuckDB + Pandas   | | A2A Messaging    | |   Memory System      |
  |  (Analytics Engine)| | forecast_agent   | |  Working / Episodic  |
  |  analytics_tools.py| | evaluation_agent | |  / Semantic          |
  +--------------------+ +------------------+ +----------+-----------+
                                                          |
                                                          v
                                         +----------------------------+
                                         |   DATABASE LAYER           |
                                         |  Supabase (cloud)          |
                                         |  SQLite  (local fallback)  |
                                         |  datasets.db               |
                                         +----------------------------+
                                                          |
                                                          v
                                         +----------------------------+
                                         |   FINAL OUTPUT             |
                                         |  Executive Report (MD)     |
                                         |  + Forecast Card (A2A)     |
                                         |  + Evaluation Score        |
                                         |  Rendered in Streamlit UI  |
                                         +----------------------------+
```

---

## 3. DIRECTORY STRUCTURE

```
capstone/
└── boardroom-ai/
    ├── balu.md                        <- THIS DOCUMENT
    ├── README.md
    ├── adk_ui_traces_guide.md
    ├── .gitignore
    |
    ├── frontend/
    |   └── app.py                     <- Streamlit dashboard (UI)
    |
    ├── backend/
    |   ├── app.py                     <- FastAPI application entry point
    |   ├── config.py                  <- Env vars, paths, mock mode flag
    |   ├── datasets.db                <- SQLite local database file
    |   ├── .env                       <- API keys (Gemini, Supabase)
    |   |
    |   ├── agents/
    |   |   ├── orchestrator/
    |   |   |   ├── agent.py           <- ADK entry point (root_agent)
    |   |   |   └── executive_orchestrator.py
    |   |   ├── revenue/
    |   |   |   └── revenue_agent.py   <- Revenue analysis sub-agent
    |   |   ├── customer/
    |   |   |   └── customer_agent.py  <- Customer churn sub-agent
    |   |   ├── risk/
    |   |   |   └── risk_agent.py      <- Risk/anomaly detection sub-agent
    |   |   ├── report/
    |   |   |   └── report_agent.py    <- Report compilation sub-agent
    |   |   ├── forecast/
    |   |   |   └── forecast_agent.py  <- Revenue forecasting (A2A)
    |   |   ├── security/
    |   |   |   └── security_agent.py  <- RBAC + security filter (A2A)
    |   |   └── evaluation/
    |   |       └── evaluation_agent.py <- Report quality evaluator (A2A)
    |   |
    |   ├── api/
    |   |   ├── upload.py              <- POST /upload endpoint
    |   |   └── analysis.py            <- POST /analyze + observability
    |   |
    |   ├── services/
    |   |   ├── a2a_service.py         <- Agent-to-Agent communication hub
    |   |   ├── agentops_service.py    <- AgentOps telemetry wrapper
    |   |   ├── dataset_service.py     <- Dataset retrieval helpers
    |   |   ├── memory_manager.py      <- Context Assembly Pipeline
    |   |   ├── skill_manager.py       <- Skill loading system
    |   |   └── storage_service.py     <- File storage helpers
    |   |
    |   ├── database/
    |   |   └── supabase.py            <- DB abstraction (Supabase + SQLite)
    |   |
    |   ├── tools/
    |   |   ├── analytics_tools.py     <- DuckDB/Pandas analysis functions
    |   |   ├── dataset_tools.py       <- Dataset query helpers
    |   |   ├── mcp_client.py          <- MCP toolset connector
    |   |   └── report_tools.py        <- Report generation tools
    |   |
    |   ├── uploads/                   <- File storage for uploaded CSVs
    |   └── tests/                     <- Test suite
    |
    ├── mcp_server/
    |   ├── server.py                  <- FastMCP server (tool definitions)
    |   └── capabilities/
    |       ├── query_data.py          <- query_data tool
    |       ├── run_analysis.py        <- run_analysis tool
    |       ├── generate_artifact.py   <- generate_artifact tool
    |       └── memory.py              <- memory tool
    |
    ├── data/
    |   ├── sales_large.csv            <- Primary sales dataset
    |   ├── customers_large.csv        <- Customer segments dataset
    |   ├── forecast_enterprise.csv    <- Forecast data
    |   ├── inventory_large.csv        <- Inventory data
    |   └── marketing_large.csv        <- Marketing data
    |
    └── skills/                        <- Skill definition YAMLs
```

---

## 4. LAYER 1: FRONTEND (STREAMLIT UI)

**File:** `frontend/app.py`
**Port:** `http://localhost:8501`
**Framework:** Streamlit with custom glassmorphic CSS (dark theme, electric-blue accents)

### UI Tabs

| Tab | Purpose |
|---|---|
| Dataset Viewer | Preview uploaded CSV data + summary statistics |
| Multi-Agent Insights | Submit strategic questions, trigger analysis, view executive report |
| Observability & AgentOps | Live telemetry: agent run logs, investigation states, security events |

### Sidebar Controls
- **CSV Uploader** — multipart upload to `POST /upload` per file
- **Role Selector (RBAC)** — Admin / Executive / Analyst / Viewer
- **Dataset Selector** — selects which uploaded dataset to analyze

### Key UI Flows

**1. CSV Upload:**
```
User selects CSV -> POST /upload -> backend assigns dataset_id
-> stored in session_state["datasets"] -> success toast shown
```

**2. Analysis:**
```
User types question -> selects dataset + role
-> "Compile Executive Report" clicked
-> POST /analyze {dataset_id, question, role}
-> spinner shown -> response rendered as markdown report
```

**3. Observability Polling:**
```
GET /api/observability/stats          -> KPI metrics row
GET /api/observability/runs           -> Agent execution logs table
GET /api/observability/investigations -> State machine monitor table
GET /api/observability/security_events -> Security audit logs table
```

---

## 5. LAYER 2: BACKEND API (FASTAPI)

**File:** `backend/app.py`
**Port:** `http://localhost:8000`
**Framework:** FastAPI + Uvicorn

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/upload` | Ingest CSV -> save to uploads/ -> register in DB |
| GET | `/datasets` | List all registered datasets |
| GET | `/datasets/{id}/content` | Download raw dataset bytes |
| POST | `/analyze` | Full multi-agent analysis orchestration |
| GET | `/api/observability/stats` | Aggregated agent run stats |
| GET | `/api/observability/runs` | All agent runs list |
| GET | `/api/observability/investigations` | All investigations with state |
| GET | `/api/observability/security_events` | All security events |

### Middleware
- **CORS:** All origins allowed (for Streamlit <-> FastAPI cross-origin)
- **Startup Event:** `db_init()` — creates all SQLite tables on boot

### /analyze Request Model
```python
class AnalysisRequest(BaseModel):
    dataset_id: str     # UUID of the uploaded dataset
    question: str       # Natural language business question
    role: str           # RBAC role string (default: "Executive")
```

---

## 6. LAYER 3: CONTEXT ASSEMBLY PIPELINE

**File:** `backend/services/memory_manager.py`

Before any agent runs, the system builds a rich context prompt prepended to the user's question.

### Pipeline Steps (Sequential)

```
Step 1: QUESTION RECEIVED
  [ADK TRACE] Question Received: 'Why did revenue drop in May?'

Step 2: SKILL LOADER
  skill_manager.find_required_skill(question)
  -> identifies which skill profile applies
  -> loads skill instructions from SQLite skills table
  [ADK TRACE] Skill Loaded: 'revenue_analysis'

Step 3: WORKING MEMORY (Session-scoped)
  db_retrieve_memory("working", session_id)
  -> fetches current session state
  -> if none: initializes fresh working memory

Step 4: EPISODIC MEMORY (Investigation-scoped)
  db_retrieve_memory("episodic", investigation_id)
  -> fetches past findings for this investigation
  -> if none: records 'No prior findings — new investigation'

Step 5: SEMANTIC MEMORY (Global KPI definitions)
  db_retrieve_memory("semantic", "Revenue Growth KPI")
  db_retrieve_memory("semantic", "Customer Churn KPI")
  db_retrieve_memory("semantic", "Risk Alert Tolerances")

Step 6: BUILD CONTEXT PROMPT
  === CONTEXT ASSEMBLY PIPELINE ===
  [ACTIVE SKILL] ...
  [WORKING MEMORY] ...
  [EPISODIC MEMORY (PAST FINDINGS)] ...
  [SEMANTIC MEMORY (BUSINESS RULES & KPIS)] ...
  =================================
```

### Semantic Memory Seed Data (Pre-loaded KPIs)

| KPI | Formula |
|---|---|
| Revenue Growth | `MoM Growth = ((Current - Prior) / Prior) * 100` |
| Customer Churn | `Churn Rate = (Churned / Total) * 100` |
| Risk Tolerances | Revenue decline > -10%, Regional decline > -20% |

---

## 7. LAYER 4: MULTI-AGENT ORCHESTRATION (GOOGLE ADK)

**Framework:** Google Agent Development Kit (ADK)
**Runner:** `InMemoryRunner` (per-request ephemeral session)

### Agent Hierarchy

```
executive_orchestrator  (Root Agent - gemini-2.5-flash)
  fallback: executive_orchestrator_fallback (gemini-1.5-flash)
  |
  +-- ask_revenue_agent()  -> revenue_agent
  |     tools: [mcp_toolset]
  |     uses: query_data + run_analysis(type='revenue')
  |
  +-- ask_customer_agent() -> customer_agent
  |     tools: [mcp_toolset]
  |     uses: query_data + run_analysis(type='customer')
  |
  +-- ask_risk_agent()     -> risk_agent
  |     tools: [mcp_toolset]
  |     uses: query_data + run_analysis(type='risk')
  |
  +-- ask_report_agent()   -> report_agent
        tools: [mcp_toolset]
        uses: generate_artifact(revenue, customer, risk findings)
```

### Orchestrator Instruction Flow
```
1. Analyze revenue  -> call ask_revenue_agent(question)
2. Analyze customers-> call ask_customer_agent(question)
3. Detect risks     -> call ask_risk_agent(question)
4. Compile report   -> call ask_report_agent(revenue_findings, customer_findings, risk_findings)
5. Return final report to caller
```

### Sub-Agent Instructions

| Agent | Steps |
|---|---|
| **revenue_agent** | 1. query_data('sales') 2. run_analysis(type='revenue') 3. Summarize MoM % change + regional/product breakdown |
| **customer_agent** | 1. query_data('customers') 2. run_analysis(type='customer') 3. Summarize churn rates by segment |
| **risk_agent** | 1. query_data('sales') 2. run_analysis(type='risk') 3. Summarize anomaly alerts vs tolerance thresholds |
| **report_agent** | 1. Receive 3 findings 2. generate_artifact() 3. Return structured markdown executive report |

### Retry Configuration
```python
retry_config = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(initial_delay=2.0, attempts=3)
    )
)
```

---

## 8. LAYER 5: MCP SERVER (MODEL CONTEXT PROTOCOL)

**File:** `mcp_server/server.py`
**Framework:** FastMCP
**Transport:** stdio (subprocess)

The MCP Server exposes 4 tools called by all agents via `mcp_toolset` (`backend/tools/mcp_client.py`).

### MCP Tools

#### `query_data(dataset, filters)`
```
Purpose: Retrieve raw records from an uploaded dataset
Input:   dataset name (e.g. 'sales'), optional filters dict
Output:  dict of records
Source:  mcp_server/capabilities/query_data.py
```

#### `run_analysis(analysis_type, dataset_name, question)`
```
Purpose: Execute quantitative analysis on a dataset
Types:   'revenue' | 'customer' | 'risk'
Output:  dict with formatted analytics results
Engine:  DuckDB SQL + Pandas (analytics_tools.py)
Source:  mcp_server/capabilities/run_analysis.py
```

#### `generate_artifact(revenue_findings, customer_findings, risk_findings)`
```
Purpose: Compile analysis findings into final executive report markdown
Input:   3 text strings (one per sub-agent findings)
Output:  dict with {report: markdown_string}
Source:  mcp_server/capabilities/generate_artifact.py
```

#### `memory(action, category, key, data)`
```
Purpose: Store/retrieve/search the 3-tier memory system
Actions: 'store' | 'retrieve' | 'search'
Categories: 'working' | 'episodic' | 'semantic'
Source:  mcp_server/capabilities/memory.py
```

### Analytics Engine (DuckDB + Pandas)

| Function | Purpose |
|---|---|
| `run_revenue_analysis()` | Monthly revenue grouping, MoM % change, regional/product breakdown |
| `run_customer_analysis()` | Churn rates by segment, risk segmentation |
| `run_risk_analysis()` | Anomaly detection: MoM declines exceeding tolerance thresholds |

**DuckDB Registered Tables:** `df`, `sales`, `revenue`

---

## 9. LAYER 6: AGENT-TO-AGENT (A2A) COMMUNICATION

**File:** `backend/services/a2a_service.py`

A2A routes structured JSON messages between the orchestrator and specialized agents running **outside** the main orchestration chain.

### A2A Message Format
```json
{
    "sender": "executive_orchestrator",
    "receiver": "forecast_agent",
    "task": "forecast_revenue",
    "dataset": "sales"
}
```

### A2A Routing Table

| Receiver | Trigger | Purpose | Response Keys |
|---|---|---|---|
| `security_agent` | BEFORE analysis starts | RBAC + content safety check | `allowed`, `reason` |
| `forecast_agent` | AFTER report compilation | Revenue trend forecasting | `forecast_growth`, `confidence` |
| `evaluation_agent` | AFTER report is generated | Report quality scoring | `evaluated_report`, `confidence`, `accuracy`, `completeness` |

### A2A Execution Flow

```
POST /analyze received
  |
  +-- [A2A] -> security_agent
  |     check: role + question safety
  |     if blocked: return 403 + reason immediately
  |
  +-- [ORCHESTRATOR RUNS] (produces report_text)
  |
  +-- [A2A] -> forecast_agent
  |     runs: InMemoryRunner(forecast_agent)
  |     response: {forecast_growth: 8.2, confidence: 91}
  |     appended to report as "Forecast Card"
  |
  +-- [A2A] -> evaluation_agent
        receives: full report_text
        scores: accuracy, completeness, confidence
        returns: {evaluated_report: <report with eval card>}
        final_report returned to frontend
```

---

## 10. LAYER 7: MEMORY SYSTEM (3-TIER)

**File:** `backend/services/memory_manager.py`, `backend/database/supabase.py`

### Memory Tiers

```
+----------------------------------------------------------------------+
|                    MEMORY ARCHITECTURE                                |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  | SEMANTIC MEMORY (Long-term, Global)                             |  |
|  | - KPI formulas and business rules                               |  |
|  | - Pre-seeded: Revenue Growth, Churn Rate, Risk Tolerances       |  |
|  | - Scope: shared across ALL sessions and investigations           |  |
|  | - DB Table: semantic_memory                                     |  |
|  +-----------------------------------------------------------------+  |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  | EPISODIC MEMORY (Medium-term, Per-Investigation)                |  |
|  | - Past findings and compiled reports                            |  |
|  | - Keyed by investigation_id (UUID)                              |  |
|  | - Scope: per analysis run -- feeds into next run                |  |
|  | - DB Table: episodic_memory                                     |  |
|  +-----------------------------------------------------------------+  |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  | WORKING MEMORY (Short-term, Per-Session)                        |  |
|  | - Current question, status, active skill                        |  |
|  | - Keyed by session_id (generated per request)                   |  |
|  | - Scope: single API call lifecycle                              |  |
|  | - DB Table: working_memory                                      |  |
|  +-----------------------------------------------------------------+  |
+----------------------------------------------------------------------+
```

### Memory Operations
```python
# Store
supabase.db_store_memory("working", session_id, {"current_question": ..., "status": "running"})
supabase.db_store_memory("episodic", investigation_id, {"findings": final_report})
supabase.db_store_memory("semantic", "Revenue Growth KPI", {"formula": ..., "description": ...})

# Retrieve
supabase.db_retrieve_memory("working", session_id)
supabase.db_retrieve_memory("episodic", investigation_id)
supabase.db_retrieve_memory("semantic", "Revenue Growth KPI")
```

---

## 11. LAYER 8: DATABASE & PERSISTENCE

**File:** `backend/database/supabase.py`

### Database Strategy
- **Primary:** Supabase (PostgreSQL cloud) — if `SUPABASE_URL` and `SUPABASE_KEY` are set
- **Fallback:** SQLite (local file `backend/datasets.db`) — always available

### Database Schema

| Table | Key Columns | Purpose |
|---|---|---|
| `datasets` | id, name, uploaded_at, file_path | Registered CSV datasets |
| `investigations` | id, state, status, question, created_at | State machine per analysis run |
| `agent_runs` | id, agent_name, status, start_time, end_time, duration | AgentOps execution logs |
| `working_memory` | id, session_id, data | Short-term session memory |
| `episodic_memory` | id, investigation_id, findings | Per-run findings history |
| `semantic_memory` | id, concept, content | KPI definitions + business rules |
| `skills` | id, name, instructions | Agent skill profiles |
| `security_events` | id, created_at, event_type, severity, message | Security audit log |
| `observability_metrics` | id, metric_name, value, timestamp | Performance telemetry |

---

## 12. LAYER 9: OBSERVABILITY & AGENTOPS

**File:** `backend/services/agentops_service.py`

Every agent invocation is wrapped in `run_agent_with_ops()` which provides automatic telemetry:

### AgentOps Wrapper Logic
```python
async def run_agent_with_ops(agent_name, agent_coro):
    run_id = uuid4()
    start_time = utcnow()
    db_store_agent_run(run_id, agent_name, "RUNNING", ...)
    try:
        result = await agent_coro()
        status = "COMPLETED"
        return result
    except Exception:
        status = "FAILED"
        raise
    finally:
        duration = time.time() - start_ts
        db_store_agent_run(run_id, agent_name, status, end_time, duration)
        db_store_observability_metric(f"{agent_name}_duration", duration)
        db_store_observability_metric(f"{agent_name}_status_{status}", 1.0)
```

### Agents Tracked
`executive_orchestrator`, `revenue_agent`, `customer_agent`, `risk_agent`, `report_agent`, `forecast_agent`, `security_agent`, `evaluation_agent`

### Observability Dashboard Metrics

| Metric | Calculation |
|---|---|
| Total Agent Invocations | COUNT(*) from agent_runs |
| Avg Latency (seconds) | AVG(duration) from observability_metrics |
| Fleet Success Rate | COMPLETED / TOTAL from agent_runs |
| Security Alerts Blocked | COUNT(*) from security_events |

---

## 13. LAYER 10: SECURITY & RBAC

**File:** `backend/agents/security/security_agent.py`

### Security Flow
```
POST /analyze called
  |
  v
a2a_send_message(receiver="security_agent", task=question, dataset=role)
  |
  v
security_agent evaluates:
  - Is the role permitted for this question type?
  - Does the question contain sensitive/blocked content?
  |
  v
Response: {allowed: True/False, reason: "..."}
  |
  +-- if True:  proceed to analysis
  +-- if False: update_investigation_state("FAILED")
                return {status: "blocked", report: "Security Block: ..."}
                Frontend shows red error + warning banner
```

### RBAC Roles
| Role | Access Level |
|---|---|
| Admin | Full access |
| Executive | Full reporting (default) |
| Analyst | Data analysis access |
| Viewer | Read-only |

---

## 14. COMPLETE DATA FLOW — END-TO-END

```
STEP 1: DATA INGESTION
  User uploads sales_large.csv in Streamlit sidebar
  -> POST /upload (multipart)
  -> backend saves to backend/uploads/
  -> registers in datasets table with UUID
  -> returns dataset_id to frontend

STEP 2: ANALYSIS REQUEST
  User types: "Why did revenue drop in May?"
  User role: "Executive"
  User clicks: "Compile Executive Report"
  -> POST /analyze {dataset_id, question, role}

STEP 3: STATE MACHINE — PENDING
  investigation_id = uuid4()
  supabase.insert_investigation(id, question, "PENDING")
  supabase.update_investigation_state(id, "RUNNING")

STEP 4: SECURITY CHECK (A2A)
  a2a_send_message(-> security_agent)
  -> {allowed: True}  -> proceed
  -> {allowed: False} -> return blocked response immediately

STEP 5: CONTEXT ASSEMBLY
  seed_semantic_memory()  <- load KPIs into DB if not present
  assemble_context_pipeline(question, session_id, investigation_id)
  -> loads: skill + working memory + episodic memory + semantic memory
  -> returns: context_string
  supabase.update_investigation_state(id, "INVESTIGATING")

STEP 6: ORCHESTRATOR RUNS (Google ADK)
  InMemoryRunner(executive_orchestrator) created
  Prompt sent: context_string + dataset_id + question

  executive_orchestrator:
    -> ask_revenue_agent(question)
         InMemoryRunner(revenue_agent)
         revenue_agent: query_data('sales') -> run_analysis(type='revenue')
         DuckDB: monthly revenue grouping + MoM growth %
         Pandas: regional + product breakdown
         returns: revenue findings text
         AgentOps: revenue_agent COMPLETED in X.XXs

    -> ask_customer_agent(question)
         InMemoryRunner(customer_agent)
         customer_agent: query_data('customers') -> run_analysis(type='customer')
         DuckDB: churn rate by segment
         returns: customer findings text
         AgentOps: customer_agent COMPLETED

    -> ask_risk_agent(question)
         InMemoryRunner(risk_agent)
         risk_agent: query_data('sales') -> run_analysis(type='risk')
         DuckDB: anomaly detection vs tolerance thresholds
         returns: risk findings text
         AgentOps: risk_agent COMPLETED

    -> ask_report_agent(revenue, customer, risk findings)
         InMemoryRunner(report_agent)
         report_agent: generate_artifact(rev, cust, risk)
         returns: compiled markdown executive report
         AgentOps: report_agent COMPLETED

  executive_orchestrator returns: report_text
  AgentOps: executive_orchestrator COMPLETED

STEP 7: FORECAST AGENT (A2A)
  a2a_send_message(-> forecast_agent)
  -> InMemoryRunner(forecast_agent)
  -> forecast_agent: query_data -> calculate growth trend
  -> returns: {forecast_growth: 8.2, confidence: 91}
  Appended to report:
  "Forecast: +8.2% projected growth | 91% confidence"

STEP 8: STATE MACHINE — EVALUATING
  supabase.update_investigation_state(id, "EVALUATING")

STEP 9: EVALUATION AGENT (A2A)
  a2a_send_message(-> evaluation_agent, task=report_text)
  -> evaluation_agent: score accuracy, completeness, confidence
  -> appends evaluation card to report
  -> returns: {evaluated_report: <final_report>, confidence: 90}

STEP 10: MEMORY STORAGE
  supabase.db_store_memory("episodic", investigation_id, {findings: final_report})
  supabase.db_store_memory("working", session_id, {status: "completed"})

STEP 11: STATE MACHINE — COMPLETED
  supabase.update_investigation_state(id, "COMPLETED")
  return {report: final_report}

STEP 12: OUTPUT RENDERED IN STREAMLIT
  Frontend receives response.json()["report"]
  Rendered inside <div class="report-box"> with st.markdown()
  User sees:
  - Revenue diagnostics section
  - Customer churn analysis
  - Risk & anomaly alerts
  - Revenue forecast card (A2A)
  - Evaluation quality score card
```

---

## 15. CONFIGURATION & ENVIRONMENT

**File:** `backend/config.py` + `backend/.env`

### Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API access | Yes (or MOCK_MODE activates) |
| `SUPABASE_URL` | Supabase project URL | No (falls back to SQLite) |
| `SUPABASE_KEY` | Supabase anon/service key | No (falls back to SQLite) |

### Config Constants

| Constant | Value | Description |
|---|---|---|
| `MOCK_MODE` | `not bool(GEMINI_API_KEY)` | True = skip Gemini, use analytical mock report |
| `DB_PATH` | `backend/datasets.db` | Local SQLite database path |
| `UPLOAD_DIR` | `backend/uploads/` | Uploaded CSV storage directory |
| `BASE_DIR` | `backend/` | Backend base directory |

### Mock Mode Behavior
When `GEMINI_API_KEY` is absent:
- Skip all Gemini LLM calls
- Return a pre-built structured mock report
- A2A calls still execute (with fallback default values)
- State machine transitions still run
- AgentOps telemetry still logged

---

## 16. TECHNOLOGY STACK SUMMARY

| Category | Technology | Notes |
|---|---|---|
| LLM Primary | Google Gemini 2.5 Flash | Main model for all agents |
| LLM Fallback | Google Gemini 1.5 Flash | On API 429/503 failure |
| Agent Framework | Google ADK | `google-adk` package |
| Tool Protocol | MCP (Model Context Protocol) | via `fastmcp` |
| Analytics SQL | DuckDB | SQL on in-memory dataframes |
| Data Processing | Pandas | CSV parsing, statistical analysis |
| API Server | FastAPI + Uvicorn | REST API, port 8000 |
| UI | Streamlit | Dashboard, port 8501 |
| Database (cloud) | Supabase (PostgreSQL) | Optional |
| Database (local) | SQLite | Always available fallback |
| HTTP Client | requests | Frontend -> Backend calls |
| Python | 3.12 | Runtime |

---

## 17. STATE MACHINE LIFECYCLE

Every analysis request is tracked as an **Investigation** with the following state machine:

```
                     +---------------+
                     |    PENDING    |  <- investigation created
                     +-------+-------+
                             |
                             v
                     +---------------+
                     |    RUNNING    |  <- security check + context assembly
                     +-------+-------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
       [security          [valid]      [mock mode]
        blocked]             |
              |              |
              v              v
           FAILED      INVESTIGATING   <- orchestrator + sub-agents running
                             |
                             v
                       EVALUATING      <- forecast + evaluation A2A calls
                             |
                     +-------+-------+
                     |   COMPLETED   |  <- report returned to frontend
                     +---------------+
```

---

## 18. ERROR HANDLING & FALLBACK CHAIN

The system has a robust 4-level fallback strategy:

```
Level 1: GEMINI PRIMARY MODEL (gemini-2.5-flash)
  |
  v if 429/503/timeout error (after 3 retries with 2s delay)
  |
Level 2: GEMINI FALLBACK MODEL (gemini-1.5-flash)
  |
  v if that also fails
  |
Level 3: ANALYTICAL FALLBACK (per sub-agent)
  - Each ask_*_agent() has try/except with hardcoded analytical values
  - Revenue: returns hardcoded MoM percentages
  - Customer: returns hardcoded churn rate text
  - Risk: returns hardcoded anomaly alerts
  |
  v if outer analysis.py raises
  |
Level 4: GLOBAL FALLBACK REPORT
  - analysis.py catch block generates full structured mock report
  - A2A forecast/evaluation still attempted with default values
  - State machine marks investigation as COMPLETED (not FAILED)
  - User receives formatted fallback report (not a raw error)
```

### Rate Limit Handling (429 RESOURCE_EXHAUSTED)
The error seen in your ADK web server logs (`429 RESOURCE_EXHAUSTED: generate_content_free_tier_requests limit: 5`) occurs because:
- Free Gemini API tier: 5 requests/minute per model
- Multiple agents fire in parallel (revenue + customer + risk)
- **Solution:** Use a paid API key with higher quota, or add explicit sleep delays between sub-agent calls

---

## DATASET SUPPORT

| Dataset File | Content | Primary Agent |
|---|---|---|
| `sales_large.csv` | Monthly revenue by region/product | Revenue Agent, Risk Agent |
| `customers_large.csv` | Customer segments, churn flag | Customer Agent |
| `forecast_enterprise.csv` | Historical forecasting data | Forecast Agent |
| `inventory_large.csv` | Inventory levels | (future expansion) |
| `marketing_large.csv` | Marketing spend/campaigns | (future expansion) |

**DuckDB Column Auto-Detection:**
- Revenue columns: `revenue`, `sales`, `amount`
- Date columns: `date`, `month`, `timestamp`
- Region columns: `region`, `country`
- Product columns: `product category`, `product_category`, `product`, `category`

---

## HOW TO RUN

Always use the **Streamlit Web UI** dashboard at `http://localhost:8501` for uploading datasets, running analysis, and verifying features.

```bash
# 1. Start the MCP Server
python -m mcp_server.server

# 2. Start the Backend API (new terminal)
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# 3. Start the Frontend Dashboard (new terminal)
streamlit run frontend/app.py --server.port 8501

# 4. (Optional) ADK Web UI for agent tracing
adk web --port 8001 backend/agents
```

Then open **http://localhost:8501** to access the Boardroom AI dashboard.

---

*Architecture documented for Boardroom AI Capstone Project — 2026-06-23*
