# Boardroom AI 💼
### Multi-Agent Strategic Advisory & Advanced Analytics Fleet

Boardroom AI is a production-ready, multi-agent fleet designed to automatically ingest raw business datasets (e.g. Sales, Customers, Churn) and compile executive-ready analytical advisory reports. By utilizing **Google ADK (Agent Development Kit)**, **FastMCP (Model Context Protocol)**, structured **Agent-to-Agent (A2A)** messaging, and comprehensive **AgentOps & Observability**, the system moves beyond simple linear delegation into a resilient, self-correcting corporate brain.

---

## 📋 Table of Contents
1. [Day-by-Day Whitepaper Mapping](#-day-by-day-whitepaper-mapping)
2. [Problem Statement](#-problem-statement)
3. [Architecture Overview](#-architecture-overview)
4. [Agent Fleet Roles](#-agent-fleet-roles)
5. [Installation & Local Setup](#-installation--local-setup)
6. [E2E Testing & Verification](#-e2e-testing--verification)
7. [Dashboard Features](#-dashboard-features)

---

## 🗓️ Day-by-Day Whitepaper Mapping

Our capstone project is explicitly structured around the concepts covered in the course whitepapers:

| Whitepaper | Course Day | Implementation Details |
| :--- | :--- | :--- |
| **Day 1: Agent Architectures** | Orchestrator + Specialist Agents | The parent `Executive Orchestrator` coordinates a fleet of sub-agents (`Revenue Agent`, `Customer Agent`, `Risk Agent`, and `Report Agent`) to synthesize diagnostics. |
| **Day 2: MCP Protocol** | MCP Server & Client | Custom FastMCP server exposes SQL database querying, specialized analytical functions, and markdown report compiling as tools. |
| **Day 3: Context & Memory** | Skill Loader + Memory Managers | System retrieves task-specific recipes (skills) and utilizes Working (session state), Episodic (historical findings), and Semantic (KPI concepts) memory layers. |
| **Day 4: Security & Eval** | Safety Guardrails & Model Evaluations | Safety Agent acts as a front door checking for prompt injection, policy violations, and user role RBAC. Evaluation Agent grades accuracy/consistency. |
| **Day 5: Production & Ops** | A2A Protocol, AgentOps & Observability | Structured inter-agent messaging, SQLite AgentOps execution tables, State Machine tracker, and real-time Streamlit Telemetry Dashboard. |

---

## 🎯 Problem Statement

Traditional business reporting is slow, siloed, and prone to human error. Analysts spend hours copying spreadsheet data, executing separate SQL queries, compiling charts, and writing summaries. 

**Boardroom AI** automates this end-to-end pipeline:
1. **Security & RBAC Guard**: Stops unauthorized users or prompt injection vectors at the door.
2. **Contextual Memory Assembly**: Retrieves similar previous business patterns and loads the exact analytical instructions (skills) required.
3. **Federated Specialist Fleet**: Multiple specialized agents analyze the data simultaneously.
4. **Structured A2A Messaging**: Agents collaborate dynamically (e.g. Orchestrator prompts the Forecast Agent and receives structured growth metrics).
5. **Rigorous Quality Check**: A separate evaluation agent checks calculations for hallucinations and consistency before publication.

---

## 🏗️ Architecture Overview

```
                        +----------------------+
                        |   Streamlit Web UI   | (Dashboard, Data preview, Observability)
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |   FastAPI Backend    | (Router, Security Check, Telemetry APIs)
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |     ADK Runtime      |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        | ExecutiveOrchestrator|
                        +----+-----+------+----+
                             |     |      |
         +-------------------+     |      +---------------------+
         | (A2A Message)           | (A2A Message)              | (A2A Message)
         v                         v                            v
  +--------------+          +--------------+             +--------------+
  |Security Agent|          |Forecast Agent|             |Evaluation Agt|
  +--------------+          +--------------+             +--------------+
         |                         |                            |
         |                         v                            |
         |                  +--------------+                    |
         +----------------->| Boardroom    |<-------------------+
                            | MCP Server   |
                            +------+-------+
                                   |
                         +---------+---------+
                         |                   |
                         v                   v
                  +--------------+   +---------------+
                  | SQLite DB    |   | Local Storage | (CSV Datasets)
                  +--------------+   +---------------+
```

---

## 💼 Agent Fleet Roles

1. **Executive Orchestrator**: The central planner that delegates analysis sub-tasks and synthesizes the findings into an executive brief.
2. **Revenue Agent**: Specialist in assessing monthly growth trends, regional sales splits, and category shifts using the MCP query tools.
3. **Customer Agent**: Analyzes demographics, standard segments, and customer churn metrics.
4. **Risk Agent**: Monitors anomaly alerts and alerts the executive if MoM performance drops below standard tolerances.
5. **Forecast Agent**: Uses A2A structured parameters to run regression forecasts on future monthly trends.
6. **Security Agent**: Validates queries against heuristic patterns and model security guidelines to prevent prompt injection and RBAC bypasses.
7. **Evaluation Agent**: Analyzes report output and computes scores for accuracy, completeness, consistency, and hallucination risk.

---

## 💻 Installation & Local Setup

### Prerequisites
* Python 3.10+
* SQLite 3

### Step 1: Clone & Navigate
```bash
git clone <repository_url>
cd capstone/boardroom-ai
```

### Step 2: Set Environment Variables
Create a `.env` file inside `boardroom-ai/backend/` and provide your Gemini API credentials:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```
*(If no API Key is provided, the backend falls back automatically to zero-config local mock calculations, enabling seamless evaluation)*

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Run the Backend & MCP Server
Start the FastAPI server (this will automatically launch the FastMCP server inside the Python process):
```bash
python backend/app.py
```
*(Runs on `http://localhost:8000`)*

### Step 5: Start the Streamlit Frontend Dashboard
In a separate terminal tab/window:
```bash
streamlit run frontend/app.py
```
*(Runs on `http://localhost:8501`)*

---

## 🧪 E2E Testing & Verification

We include an automated integration test script that seeds local mock data, registers datasets, runs security validation, performs A2A orchestration, runs evaluation, and validates database writes.

Run it using:
```bash
python backend/test_e2e.py
```
A successful run will output `E2E Verification SUCCESS!` and print the compiled markdown report.

---

## 📊 Dashboard Features

Open `http://localhost:8501` in your browser. The Streamlit Web UI provides:

* **📊 Dataset Viewer**: Select and inspect uploaded CSV datasets (such as `sales.csv` and `customers.csv`), complete with preview tables and summary statistics.
* **🔍 Multi-Agent Insights**: Enter strategic questions (e.g. *"Why did revenue drop in May?"*), choose access roles (RBAC), and compile professional executive reports.
* **📈 Observability & AgentOps**:
  * **System KPI Cards**: Real-time display of total invocations, average duration, fleet success rate, and blocked security actions.
  * **State Machine Monitor**: Track investigations through active status nodes: `PENDING` ➔ `RUNNING` ➔ `INVESTIGATING` ➔ `EVALUATING` ➔ `COMPLETED`.
  * **Detailed Agent Runs**: List of agent execution durations, start/end timestamps, and success logs.
  * **Security Audit Trail**: Logs security severity, event types, and descriptions.
