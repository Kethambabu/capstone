import streamlit as st
import pandas as pd
import requests

# Page setup for premium executive branding
st.set_page_config(
    page_title="Boardroom AI - Multi-Agent Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphic look
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    h1, h2, h3, p, span, label {
        font-family: 'Outfit', 'Inter', sans-serif !important;
    }
    
    /* Executive styling */
    .header-container {
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
    }
    
    .report-box {
        background-color: #0f172a;
        padding: 2rem;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        border-right: 1px solid #1e293b;
        border-top: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        margin-top: 1.5rem;
    }

    /* High-contrast Metric Card Styling */
    div[data-testid="stMetricValue"] {
        color: #60a5fa !important; /* Premium electric blue */
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #e2e8f0 !important; /* Premium light white/slate */
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* Premium Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #2563eb !important;
        padding: 0.6rem 1.6rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-1px) !important;
        border-color: #60a5fa !important;
    }

    /* Premium Tab Selector Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 28px !important;
        border-bottom: 2px solid #1e293b !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px !important;
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
<div class="header-container">
    <h1 style="color: #3b82f6; margin: 0;">💼 Boardroom AI</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem; margin-bottom: 0;">
        Multi-Agent Strategic Advisory & Advanced Analytics Fleet
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.markdown("### 📂 Dataset Management")
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV Datasets (Select Multiple)", 
    type=["csv"], 
    accept_multiple_files=True
)

# Move RBAC and execution configurations to advanced settings
with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
    user_role = st.selectbox(
        "Select Session Role (RBAC):",
        options=["Admin", "CEO", "Finance Manager", "Sales Manager", "Analyst", "Viewer"],
        index=1 # Default to CEO
    )

    execution_mode_label = st.selectbox(
        "Select Execution Mode:",
        options=[
            "Quota-Saver Mode (Single-Query)",
            "Multi-Agent Fleet (Parallel)",
            "Multi-Agent Fleet (Sequential)"
        ],
        index=0,
        help="Quota-Saver is recommended for Gemini Free Tier (uses 1 request)."
    )

# Map labels to API values
mode_map = {
    "Quota-Saver Mode (Single-Query)": "quota_saver",
    "Multi-Agent Fleet (Parallel)": "parallel",
    "Multi-Agent Fleet (Sequential)": "sequential"
}
execution_mode = mode_map[execution_mode_label]

# Backend API Configuration
BACKEND_URL = "http://localhost:8000"

# Initialize datasets storage in session state
if "datasets" not in st.session_state:
    st.session_state["datasets"] = {}
    # Fetch existing datasets from backend database on startup
    try:
        response = requests.get(f"{BACKEND_URL}/datasets")
        if response.status_code == 200:
            for dataset in response.json():
                st.session_state["datasets"][dataset["name"]] = dataset["id"]
    except Exception as e:
        st.sidebar.error(f"Failed to fetch datasets list from database: {e}")

# Ingest newly uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        if filename not in st.session_state["datasets"]:
            with st.spinner(f"Ingesting {filename} into storage engine..."):
                try:
                    uploaded_file.seek(0)
                    files = {"file": (filename, uploaded_file.read(), "text/csv")}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.session_state["datasets"][filename] = response.json()["dataset_id"]
                        st.sidebar.success(f"✅ {filename} Synced!")
                    else:
                        st.sidebar.error(f"Sync failed for {filename}: {response.text}")
                except Exception as e:
                    st.sidebar.error(f"Failed to connect to backend for {filename}: {str(e)}")


# Select primary dataset
selected_filename = None
selected_dataset_id = None
dataset_options = list(st.session_state["datasets"].keys())
if dataset_options:
    selected_filename = st.sidebar.selectbox("Select Primary Dataset for analysis:", dataset_options)
    selected_dataset_id = st.session_state["datasets"][selected_filename]

# Main Workspace Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dataset Explorer", "🔍 Strategic Advisory Portal", "📈 Fleet Telemetry & Ops"])

with tab1:
    if selected_filename:
        df = None
        if uploaded_files:
            target_file = next((f for f in uploaded_files if f.name == selected_filename), None)
            if target_file:
                target_file.seek(0)
                df = pd.read_csv(target_file)
        
        if df is None:
            with st.spinner("Downloading dataset preview from storage..."):
                try:
                    response = requests.get(f"{BACKEND_URL}/datasets/{selected_dataset_id}/content")
                    if response.status_code == 200:
                        import io
                        df = pd.read_csv(io.BytesIO(response.content))
                    else:
                        st.error(f"Failed to fetch content from backend: {response.text}")
                except Exception as e:
                    st.error(f"Error fetching dataset preview: {str(e)}")
                    
        if df is not None:
            st.markdown(f"### 📋 Preview: {selected_filename} (Top 10 Records)")
            st.dataframe(df.head(10), width="stretch")
            
            st.markdown("### 📊 Descriptive Analytics Summary")
            st.dataframe(df.describe(include="all").astype(str), width="stretch")
    else:
        st.info("💡 Please upload one or more CSV datasets in the sidebar to preview data.")


with tab2:
    if selected_filename and selected_dataset_id:
        st.markdown("### 🧠 Strategic Advisory Hub")
        st.write("Ask strategic business questions. The Orchestrator will activate specialized analyst agents (Revenue, Customer, Risk, Forecast) to generate a synthesized, evaluated advisory report.")
        st.write(f"Current Access Level: **{user_role}**")
        
        question = st.text_input(
            "Enter your strategic inquiry:", 
            value="Why did revenue drop in May?"
        )
        
        if st.button("⚡ Generate Advisory Report", type="primary"):
            with st.spinner("Orchestrating agent fleet and compiling sub-reports..."):
                try:
                    payload = {
                        "dataset_id": selected_dataset_id,
                        "question": question,
                        "role": user_role,
                        "execution_mode": execution_mode
                    }
                    response = requests.post(f"{BACKEND_URL}/analyze", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "blocked":
                            st.error(data.get("report"))
                            st.warning("⚠️ Request blocked by the Safety Agent and logged in security events.")
                        else:
                            report = data["report"]
                            
                            # Parse active agents comment if present
                            active_agents = []
                            if "<!-- ACTIVE_AGENTS:" in report:
                                import re
                                match = re.search(r"<!-- ACTIVE_AGENTS:\s*([a-zA-Z0-9,_-]+)\s*-->", report)
                                if match:
                                    active_agents = [a.strip() for a in match.group(1).split(",")]
                                    # Remove comment from display report
                                    report = re.sub(r"<!-- ACTIVE_AGENTS:.*?-->", "", report).strip()
                            
                            # Display active agents badge
                            if active_agents:
                                st.markdown("##### ⚡ Active Specialized Intelligence Modules:")
                                cols = st.columns(len(active_agents))
                                for i, agent in enumerate(active_agents):
                                    with cols[i]:
                                        st.info(f"💼 **{agent.upper()} Specialist**")
                                        
                            st.markdown('<div class="report-box">', unsafe_allow_html=True)
                            st.markdown(report)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Render UI Hints
                            ui_hints = data.get("ui_hints", [])
                            if ui_hints:
                                st.markdown("### 📊 Dynamic Visual Analytics")
                                kpi_hints = [h for h in ui_hints if h["type"] == "kpi_card"]
                                chart_hints = [h for h in ui_hints if h["type"] != "kpi_card"]
                                
                                # Render KPI Cards
                                if kpi_hints:
                                    kcols = st.columns(len(kpi_hints))
                                    for idx, card in enumerate(kpi_hints):
                                        with kcols[idx]:
                                            st.metric(
                                                label=card.get("label"), 
                                                value=card.get("value"), 
                                                help=card.get("description")
                                            )
                                            
                                # Render Charts
                                for chart in chart_hints:
                                    chart_type = chart.get("type")
                                    title = chart.get("title", "Data Visualization")
                                    chart_data = pd.DataFrame(chart.get("data", []))
                                    
                                    if not chart_data.empty:
                                        st.markdown(f"#### {title}")
                                        import altair as alt
                                        if chart_type == "line_chart":
                                            x = chart.get("x_axis")
                                            y = chart.get("y_axis")
                                            line = alt.Chart(chart_data).mark_line(
                                                interpolate="monotone",
                                                color="#3b82f6",
                                                strokeWidth=3
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                tooltip=[x, alt.Tooltip(field=y, format="$,.2f" if "revenue" in y.lower() or "sales" in y.lower() else ",.0f")]
                                            )
                                            points = alt.Chart(chart_data).mark_point(
                                                color="#60a5fa",
                                                size=60,
                                                filled=True
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None),
                                                y=alt.Y(field=y, type="quantitative"),
                                                tooltip=[x, alt.Tooltip(field=y, format="$,.2f" if "revenue" in y.lower() or "sales" in y.lower() else ",.0f")]
                                            )
                                            full_chart = (line + points).properties(
                                                height=350
                                            ).configure_axis(
                                                labelColor="#94a3b8",
                                                titleColor="#e2e8f0",
                                                gridColor="#1e293b"
                                            ).configure_view(
                                                strokeWidth=0
                                            )
                                            st.altair_chart(full_chart, use_container_width=True)
                                        elif chart_type == "bar_chart":
                                            x = chart.get("x_axis")
                                            y = chart.get("y_axis")
                                            bar = alt.Chart(chart_data).mark_bar(
                                                cornerRadiusTopLeft=6,
                                                cornerRadiusTopRight=6,
                                                color="#3b82f6"
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort="-y", title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                color=alt.Color(
                                                    field=x,
                                                    type="nominal",
                                                    scale=alt.Scale(scheme="tableau10"),
                                                    legend=None
                                                ),
                                                tooltip=[x, alt.Tooltip(field=y, format="$,.2f" if "revenue" in y.lower() or "sales" in y.lower() else ",.0f")]
                                            ).properties(
                                                height=350
                                            ).configure_axis(
                                                labelColor="#94a3b8",
                                                titleColor="#e2e8f0",
                                                gridColor="#1e293b"
                                            ).configure_view(
                                                strokeWidth=0
                                            )
                                            st.altair_chart(bar, use_container_width=True)
                                        elif chart_type == "pie_chart":
                                            x_col = chart_data.columns[0]
                                            y_col = chart_data.columns[1]
                                            donut_chart = alt.Chart(chart_data).mark_arc(
                                                innerRadius=70, 
                                                stroke="#0b0f19", 
                                                strokeWidth=2
                                            ).encode(
                                                theta=alt.Theta(field=y_col, type="quantitative"),
                                                color=alt.Color(
                                                    field=x_col, 
                                                    type="nominal",
                                                    scale=alt.Scale(scheme="tableau20")
                                                ),
                                                tooltip=[x_col, alt.Tooltip(field=y_col, format="$,.2f" if "revenue" in y_col.lower() or "sales" in y_col.lower() else ",.0f")]
                                            ).properties(
                                                height=350
                                            ).configure_legend(
                                                labelColor="#e2e8f0",
                                                titleColor="#e2e8f0"
                                            ).configure_view(
                                                strokeWidth=0
                                            )
                                            st.altair_chart(donut_chart, use_container_width=True)
                    else:
                        st.error(f"Analysis failed: {response.json().get('detail', response.text)}")
                except Exception as e:
                    st.error(f"Error calling backend: {str(e)}")
    else:
        st.info("💡 Welcome to Boardroom AI! Please upload one or more CSV datasets in the sidebar to begin.")

with tab3:
    st.markdown("### 📈 Agent Telemetry & Observability Dashboard")
    st.write("Monitor agent execution logs, costs, security audits, and state transitions in real time.")

    # Refresh button
    if st.button("🔄 Refresh Telemetry", type="secondary"):
        st.rerun()

    # Fetch stats and logs from backend
    try:
        stats_resp = requests.get(f"{BACKEND_URL}/api/observability/stats")
        runs_resp = requests.get(f"{BACKEND_URL}/api/observability/runs")
        inv_resp = requests.get(f"{BACKEND_URL}/api/observability/investigations")
        sec_resp = requests.get(f"{BACKEND_URL}/api/observability/security_events")
        
        if stats_resp.status_code == 200 and runs_resp.status_code == 200 and inv_resp.status_code == 200 and sec_resp.status_code == 200:
            stats = stats_resp.json()
            runs = runs_resp.json()
            invs = inv_resp.json()
            secs = sec_resp.json()
            
            # KPI Metric columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Agent Invocations", stats.get("total_agent_runs", 0))
            with col2:
                st.metric("Avg Latency (seconds)", f"{stats.get('avg_agent_duration', 0.0):.2f}s")
            with col3:
                # Calculate success rate from runs list
                df_runs = pd.DataFrame(runs)
                success_rate = "100.0%"
                if not df_runs.empty and "status" in df_runs.columns:
                    completed = len(df_runs[df_runs["status"] == "COMPLETED"])
                    total = len(df_runs)
                    success_rate = f"{(completed / total) * 100:.1f}%"
                st.metric("Fleet Success Rate", success_rate)
            with col4:
                st.metric("Security Alerts Blocked", stats.get("total_security_events", 0))

            # Cumulative Token Usage & Costs Row
            st.markdown("##### 🪙 Token Consumption & Cost Metrics")
            col_tok1, col_tok2, col_tok3 = st.columns(3)
            with col_tok1:
                st.metric("Cumulative Input Tokens", f"{stats.get('total_input_tokens', 0):,}")
            with col_tok2:
                st.metric("Cumulative Output Tokens", f"{stats.get('total_output_tokens', 0):,}")
            with col_tok3:
                st.metric("Cumulative API Cost (USD)", f"${stats.get('total_api_cost_usd', 0.0):.6f}")

            # Token Management Configuration
            st.markdown("##### ⚙️ Resource & Context Window Limits")
            conf_col1, conf_col2, conf_col3 = st.columns(3)
            with conf_col1:
                st.markdown(f"- **Primary Model:** `{stats.get('configured_model', 'N/A')}`")
                st.markdown(f"- **Fallback Model:** `{stats.get('configured_fallback_model', 'N/A')}`")
            with conf_col2:
                st.markdown(f"- **Max Output Cap:** `{stats.get('max_output_tokens', 0)}` tokens")
                st.markdown(f"- **Max Skill limit:** `{stats.get('max_skill_chars', 0)}` chars")
            with conf_col3:
                st.markdown(f"- **Max Working limit:** `{stats.get('max_working_chars', 0)}` chars")
                st.markdown(f"- **Max Episodic limit:** `{stats.get('max_episodic_chars', 0)}` chars")

            # Row 2: Workflow State Machine Monitor
            st.markdown("---")
            st.markdown("#### 🔄 Live Workflow State Transitions")
            if invs:
                df_invs = pd.DataFrame(invs)
                # Apply premium UI: colored state labels
                def get_state_badge(state):
                    state = state.upper()
                    if state == "COMPLETED":
                        return "🟢 COMPLETED"
                    elif state == "FAILED":
                        return "🔴 FAILED"
                    elif state == "PENDING":
                        return "⚪ PENDING"
                    elif state == "RUNNING":
                        return "🔵 RUNNING"
                    elif state == "INVESTIGATING":
                        return "🟠 INVESTIGATING"
                    elif state == "EVALUATING":
                        return "🟣 EVALUATING"
                    return f"🔹 {state}"
                
                df_invs["state_badge"] = df_invs["state"].apply(get_state_badge)
                
                # Show key fields
                st.dataframe(
                    df_invs[["created_at", "question", "state_badge", "id"]].rename(columns={
                        "created_at": "Timestamp",
                        "question": "User Query / Investigation",
                        "state_badge": "Current State",
                        "id": "Investigation ID"
                    }),
                    width="stretch"
                )
            else:
                st.info("No investigations logged yet.")

            # Row 3: Agent runs table
            st.markdown("---")
            st.markdown("#### 📋 Specialist Execution Telemetry")
            if runs:
                df_runs = pd.DataFrame(runs)
                st.dataframe(
                    df_runs[["agent_name", "status", "duration", "start_time", "end_time", "id"]].rename(columns={
                        "agent_name": "Agent Name",
                        "status": "Execution Status",
                        "duration": "Duration (s)",
                        "start_time": "Start Time",
                        "end_time": "End Time",
                        "id": "Run ID"
                    }),
                    width="stretch"
                )
            else:
                st.info("No agent runs logged yet.")

            # Row 4: Security Events
            st.markdown("---")
            st.markdown("#### 🛡️ Security Audit Trail & Event Logs")
            if secs:
                df_secs = pd.DataFrame(secs)
                st.dataframe(
                    df_secs[["created_at", "event_type", "severity", "message", "id"]].rename(columns={
                        "created_at": "Timestamp",
                        "event_type": "Event Type",
                        "severity": "Severity",
                        "message": "Message",
                        "id": "Event ID"
                    }),
                    width="stretch"
                )
            else:
                st.info("No security alerts logged. System secure.")
        else:
            st.error("Failed to retrieve telemetry data from backend.")
    except Exception as e:
        st.error(f"Could not connect to backend telemetry service: {str(e)}")

