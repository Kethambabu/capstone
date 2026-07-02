# Boardroom AI 💼
### Multi-Agent Strategic Advisory & Advanced Analytics Fleet

Boardroom AI is an advanced multi-agent system built on **Google ADK (Agent Development Kit)**. It ingests raw business datasets and compiles executive-ready advisory reports. The system securely accesses your data and provides actionable business insights via an easy-to-use **Streamlit web dashboard**.

---

## 📋 Table of Contents
1. [What does it do?](#-what-does-it-do)
2. [Prerequisites](#-prerequisites)
3. [Quick Start](#-quick-start)
4. [How to Run](#-how-to-run)
5. [Troubleshooting](#-troubleshooting)

---

## 🎯 What does it do?

Traditional business reporting is slow and prone to errors. **Boardroom AI** automates this pipeline for you:
1. **Security Guard**: Ensures data access is secure and stops unauthorized queries.
2. **Specialist Agents**: Analyzes your business data (Revenue, Customers, Risks) simultaneously.
3. **Executive Orchestrator**: Compiles findings from specialist agents into a clean, easy-to-read executive brief.
4. **Dashboard**: An interactive web interface to view your data and ask strategic questions.

---

## 🛠️ Prerequisites
* Python 3.11 or newer
* `uv` (Python package installer and runner)
* Gemini API Key (Generate one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

---

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd boardroom-ai
   ```

2. **Set up environment variables**
   Copy the example environment files and add your `GOOGLE_API_KEY`:
   ```bash
   cp .env.example .env
   cp .env backend/.env
   ```

3. **Install all dependencies**
   ```bash
   make install
   ```

---

## ⚙️ How to Run

Use the provided `Makefile` to easily run Boardroom AI:

* **Run the Full Web Application**:
  ```bash
  make run
  ```
  *(Starts the FastAPI Backend on `http://localhost:8000` and Streamlit dashboard on `http://localhost:8501`)*

* **Run ADK Playground** (for interactive testing):
  ```bash
  make playground
  ```
  *(Opens the playground server on `http://localhost:18081`)*

---

## 🩺 Troubleshooting

### 1. `404 Model Not Found`
- **Fix:** Ensure you have `GEMINI_MODEL=gemini-2.0-flash` set in both `backend/.env` and your root `.env` files.

### 2. Windows server doesn't pick up code edits
- **Fix:** If you modify code on Windows while the server is running, you must restart the server. Run this in PowerShell to stop it:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 18081, 8090 -ErrorAction SilentlyContinue).OwningProcess | Stop-Process -Force
  ```
  Then relaunch using `make run` or `make playground`.

---
