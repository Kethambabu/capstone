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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global styles */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, p {
        font-family: 'Outfit', 'Inter', sans-serif;
    }

    /* Executive header */
    .header-container {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }

    /* Report box */
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

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #e2e8f0 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* Buttons */
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

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 28px !important;
        border-bottom: 2px solid #1e293b !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px !important;
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
        font-family: inherit;
    }
    [data-testid="stSidebar"] .stExpander summary p {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.2rem 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .kpi-blue   { color: #60a5fa; }
    .kpi-green  { color: #34d399; }
    .kpi-amber  { color: #fbbf24; }
    .kpi-red    { color: #f87171; }
    .kpi-purple { color: #a78bfa; }

    /* Section headers */
    .section-header {
        padding: 0.6rem 0;
        border-bottom: 1px solid #1e293b;
        margin: 1.5rem 0 1rem 0;
        color: #e2e8f0;
        font-weight: 700;
        font-size: 1.05rem;
    }

    /* Chart section title */
    .chart-title {
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.4rem 0;
        padding: 0.5rem 0.8rem;
        border-left: 3px solid #3b82f6;
        background: linear-gradient(90deg, rgba(59,130,246,0.08) 0%, transparent 100%);
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── App Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 style="color: #3b82f6; margin: 0; font-size: 2rem;">💼 Boardroom AI</h1>
    <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 0.5rem; margin-bottom: 0;">
        Multi-Agent Strategic Advisory &amp; Advanced Analytics Fleet
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### 📂 Dataset Management")
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV Datasets (Select Multiple)",
    type=["csv"],
    accept_multiple_files=True
)

with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
    user_role = st.selectbox(
        "Select Session Role (RBAC):",
        options=["Admin", "CEO", "Finance Manager", "Sales Manager", "Analyst", "Viewer"],
        index=1
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

mode_map = {
    "Quota-Saver Mode (Single-Query)": "quota_saver",
    "Multi-Agent Fleet (Parallel)": "parallel",
    "Multi-Agent Fleet (Sequential)": "sequential"
}
execution_mode = mode_map[execution_mode_label]

BACKEND_URL = "http://localhost:8000"

# ── Session state: datasets ───────────────────────────────────────────────────
# Initialize datasets storage in session state
if "datasets" not in st.session_state:
    st.session_state["datasets"] = {}
    try:
        response = requests.get(f"{BACKEND_URL}/datasets")
        if response.status_code == 200:
            for dataset in response.json():
                st.session_state["datasets"][dataset["name"]] = dataset["id"]
    except Exception as e:
        st.sidebar.error(f"Failed to fetch datasets list from database: {e}")

# Track telemetry refresh state
if "last_query_ts" not in st.session_state:
    st.session_state["last_query_ts"] = None
if "telemetry_refreshed" not in st.session_state:
    st.session_state["telemetry_refreshed"] = True

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

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Dataset Explorer", "🔍 Strategic Advisory Portal", "📈 Fleet Telemetry & Ops"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Dataset Explorer
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Strategic Advisory Portal
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if selected_filename and selected_dataset_id:
        st.markdown("### 🧠 Strategic Advisory Hub")
        st.write(
            "Ask strategic business questions. The Orchestrator will activate specialized analyst agents "
            "(Revenue, Customer, Risk, Forecast) to generate a synthesized, evaluated advisory report."
        )
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

                            # Parse active agents comment
                            import re
                            active_agents = []
                            if "<!-- ACTIVE_AGENTS:" in report:
                                match = re.search(r"<!-- ACTIVE_AGENTS:\s*([a-zA-Z0-9,_-]+)\s*-->", report)
                                if match:
                                    active_agents = [a.strip() for a in match.group(1).split(",")]
                                    report = re.sub(r"<!-- ACTIVE_AGENTS:.*?-->", "", report).strip()

                            # Active agents badges
                            if active_agents:
                                st.markdown("##### ⚡ Active Specialized Intelligence Modules:")
                                cols = st.columns(len(active_agents))
                                for i, agent in enumerate(active_agents):
                                    with cols[i]:
                                        st.info(f"💼 **{agent.upper()} Specialist**")

                            # Report box
                            st.markdown('<div class="report-box">', unsafe_allow_html=True)
                            st.markdown(report)
                            st.markdown('</div>', unsafe_allow_html=True)

                            # ── Dynamic Visual Analytics ───────────────────
                            ui_hints = data.get("ui_hints", [])
                            if ui_hints:
                                st.markdown("---")
                                st.markdown("### 📊 Dynamic Visual Analytics")

                                kpi_hints   = [h for h in ui_hints if h["type"] == "kpi_card"]
                                chart_hints = [h for h in ui_hints if h["type"] != "kpi_card"]

                                # KPI metric cards
                                if kpi_hints:
                                    kcols = st.columns(len(kpi_hints))
                                    for idx, card in enumerate(kpi_hints):
                                        with kcols[idx]:
                                            st.metric(
                                                label=card.get("label"),
                                                value=card.get("value"),
                                                help=card.get("description")
                                            )

                                # Chart renderer
                                import altair as alt

                                AXIS_CFG = dict(labelColor="#94a3b8", titleColor="#e2e8f0", gridColor="#1e293b")
                                VIEW_CFG = dict(strokeWidth=0)
                                LEG_CFG  = dict(labelColor="#e2e8f0", titleColor="#94a3b8")
                                PALETTE  = alt.Scale(scheme="tableau20")
                                H        = 360

                                for chart in chart_hints:
                                    chart_type = chart.get("type")
                                    title      = chart.get("title", "Data Visualization")
                                    raw_data   = chart.get("data", [])
                                    is_cur     = chart.get("is_currency", False)
                                    num_fmt    = "$,.0f" if is_cur else ",.0f"

                                    # Gauge has no dataframe
                                    if chart_type == "gauge_chart":
                                        val   = chart.get("value", 0)
                                        maxv  = chart.get("max", 100)
                                        label = chart.get("label", "Score")
                                        pct   = val / maxv if maxv else 0
                                        color = "#34d399" if pct >= 0.75 else "#fbbf24" if pct >= 0.5 else "#f87171"
                                        st.markdown(f'<div class="chart-title">🎯 {title}</div>', unsafe_allow_html=True)
                                        g1, g2, g3 = st.columns([1, 1, 1])
                                        with g2:
                                            st.markdown(f"""
<div style="background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #334155;
border-radius:16px;padding:2rem;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.4);">
  <div style="font-size:0.75rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">{label}</div>
  <div style="font-size:3.5rem;font-weight:900;color:{color};line-height:1;">{val:.0f}%</div>
  <div style="margin-top:1rem;background:#0b0f19;border-radius:8px;height:12px;overflow:hidden;">
    <div style="width:{pct*100:.1f}%;background:{color};height:100%;border-radius:8px;"></div>
  </div>
  <div style="font-size:0.75rem;color:#64748b;margin-top:0.5rem;">{pct*100:.1f}% of {maxv}</div>
</div>
""", unsafe_allow_html=True)
                                        continue

                                    # Skip empty data
                                    if not raw_data:
                                        continue

                                    chart_data = pd.DataFrame(raw_data)
                                    if chart_data.empty:
                                        continue

                                    st.markdown(f'<div class="chart-title">📈 {title}</div>', unsafe_allow_html=True)

                                    try:
                                        # ── 1. LINE CHART ───────────────────────────────
                                        if chart_type == "line_chart":
                                            x, y = chart.get("x_axis"), chart.get("y_axis")
                                            line = alt.Chart(chart_data).mark_line(
                                                interpolate="monotone", color="#3b82f6", strokeWidth=3
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                tooltip=[x, alt.Tooltip(field=y, format=num_fmt)]
                                            )
                                            pts = alt.Chart(chart_data).mark_point(
                                                color="#60a5fa", size=70, filled=True
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None),
                                                y=alt.Y(field=y, type="quantitative"),
                                                tooltip=[x, alt.Tooltip(field=y, format=num_fmt)]
                                            )
                                            st.altair_chart(
                                                (line + pts).properties(height=H)
                                                .configure_axis(**AXIS_CFG)
                                                .configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 2. AREA CHART ────────────────────────────────
                                        elif chart_type == "area_chart":
                                            x, y = chart.get("x_axis"), chart.get("y_axis")
                                            area = alt.Chart(chart_data).mark_area(
                                                interpolate="monotone",
                                                color=alt.Gradient(
                                                    gradient="linear",
                                                    stops=[
                                                        alt.GradientStop(color="#3b82f6", offset=0),
                                                        alt.GradientStop(color="#0b0f19", offset=1)
                                                    ],
                                                    x1=1, x2=1, y1=1, y2=0
                                                ),
                                                opacity=0.8
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                tooltip=[x, alt.Tooltip(field=y, format=num_fmt)]
                                            )
                                            line2 = alt.Chart(chart_data).mark_line(
                                                color="#60a5fa", strokeWidth=2, interpolate="monotone"
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None),
                                                y=alt.Y(field=y, type="quantitative")
                                            )
                                            st.altair_chart(
                                                (area + line2).properties(height=H)
                                                .configure_axis(**AXIS_CFG)
                                                .configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 3. MULTI-LINE CHART ──────────────────────────
                                        elif chart_type == "multi_line_chart":
                                            x      = chart.get("x_axis")
                                            series = chart.get("series", [])
                                            colors = ["#3b82f6", "#34d399", "#fbbf24", "#f87171", "#a78bfa"]
                                            layers = []
                                            for si, s in enumerate(series):
                                                if s in chart_data.columns:
                                                    c = colors[si % len(colors)]
                                                    layers.append(
                                                        alt.Chart(chart_data).mark_line(
                                                            color=c, strokeWidth=2.5, interpolate="monotone"
                                                        ).encode(
                                                            x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                            y=alt.Y(field=s, type="quantitative", title="Value"),
                                                            tooltip=[x, alt.Tooltip(field=s, format=",.2f")]
                                                        )
                                                    )
                                                    layers.append(
                                                        alt.Chart(chart_data).mark_point(
                                                            color=c, size=50, filled=True
                                                        ).encode(
                                                            x=alt.X(field=x, type="nominal", sort=None),
                                                            y=alt.Y(field=s, type="quantitative")
                                                        )
                                                    )
                                            if layers:
                                                st.altair_chart(
                                                    alt.layer(*layers).properties(height=H)
                                                    .configure_axis(**AXIS_CFG)
                                                    .configure_view(**VIEW_CFG),
                                                    use_container_width=True
                                                )

                                        # ── 4. BAR CHART ─────────────────────────────────
                                        elif chart_type == "bar_chart":
                                            x, y = chart.get("x_axis"), chart.get("y_axis")
                                            bar = alt.Chart(chart_data).mark_bar(
                                                cornerRadiusTopLeft=5, cornerRadiusTopRight=5
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort="-y", title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                color=alt.Color(field=x, type="nominal", scale=PALETTE, legend=None),
                                                tooltip=[x, alt.Tooltip(field=y, format=num_fmt)]
                                            ).properties(height=H)
                                            st.altair_chart(
                                                bar.configure_axis(**AXIS_CFG).configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 5. HORIZONTAL BAR ────────────────────────────
                                        elif chart_type == "horizontal_bar":
                                            x_val = chart.get("x_axis")
                                            y_cat = chart.get("y_axis")
                                            hbar = alt.Chart(chart_data).mark_bar(
                                                cornerRadiusTopRight=5, cornerRadiusBottomRight=5
                                            ).encode(
                                                y=alt.Y(field=y_cat, type="nominal", sort="-x", title=y_cat),
                                                x=alt.X(field=x_val, type="quantitative", title=x_val),
                                                color=alt.Color(field=y_cat, type="nominal", scale=PALETTE, legend=None),
                                                tooltip=[y_cat, alt.Tooltip(field=x_val, format=num_fmt)]
                                            ).properties(height=max(H, len(chart_data) * 28))
                                            st.altair_chart(
                                                hbar.configure_axis(**AXIS_CFG).configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 6. STACKED BAR ───────────────────────────────
                                        elif chart_type == "stacked_bar_chart":
                                            x       = chart.get("x_axis")
                                            y       = chart.get("y_axis")
                                            color_f = chart.get("color_field")
                                            stacked = alt.Chart(chart_data).mark_bar(
                                                cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                y=alt.Y(field=y, type="quantitative", stack="zero", title=y),
                                                color=alt.Color(field=color_f, type="nominal", scale=PALETTE),
                                                tooltip=[x, color_f, alt.Tooltip(field=y, format=num_fmt)]
                                            ).properties(height=H)
                                            st.altair_chart(
                                                stacked
                                                .configure_axis(**AXIS_CFG)
                                                .configure_view(**VIEW_CFG)
                                                .configure_legend(**LEG_CFG),
                                                use_container_width=True
                                            )

                                        # ── 7. PIE / DONUT ───────────────────────────────
                                        elif chart_type == "pie_chart":
                                            x_col = chart.get("x_axis") or chart_data.columns[0]
                                            y_col = chart.get("y_axis") or chart_data.columns[1]
                                            donut = alt.Chart(chart_data).mark_arc(
                                                innerRadius=75, stroke="#0b0f19", strokeWidth=2
                                            ).encode(
                                                theta=alt.Theta(field=y_col, type="quantitative"),
                                                color=alt.Color(
                                                    field=x_col, type="nominal",
                                                    scale=alt.Scale(scheme="tableau20")
                                                ),
                                                tooltip=[x_col, alt.Tooltip(field=y_col, format=num_fmt)]
                                            ).properties(height=H)
                                            st.altair_chart(
                                                donut
                                                .configure_legend(**LEG_CFG)
                                                .configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 8. SCATTER PLOT ──────────────────────────────
                                        elif chart_type == "scatter_plot":
                                            x     = chart.get("x_axis")
                                            y     = chart.get("y_axis")
                                            c_fld = chart.get("color_field")
                                            enc = dict(
                                                x=alt.X(field=x, type="quantitative", title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                tooltip=[
                                                    alt.Tooltip(field=x, format=",.2f"),
                                                    alt.Tooltip(field=y, format=",.2f")
                                                ]
                                            )
                                            if c_fld and c_fld in chart_data.columns:
                                                enc["color"] = alt.Color(field=c_fld, type="nominal", scale=PALETTE)
                                                enc["tooltip"].append(c_fld)
                                            scatter = alt.Chart(chart_data).mark_circle(
                                                size=90, opacity=0.85
                                            ).encode(**enc).properties(height=H)
                                            trend = alt.Chart(chart_data).transform_regression(
                                                x, y
                                            ).mark_line(
                                                color="#f87171", strokeWidth=2, strokeDash=[5, 3]
                                            ).encode(
                                                x=alt.X(field=x, type="quantitative"),
                                                y=alt.Y(field=y, type="quantitative")
                                            )
                                            st.altair_chart(
                                                (scatter + trend).properties(height=H)
                                                .configure_axis(**AXIS_CFG)
                                                .configure_view(**VIEW_CFG)
                                                .configure_legend(**LEG_CFG),
                                                use_container_width=True
                                            )

                                        # ── 9. HISTOGRAM ─────────────────────────────────
                                        elif chart_type == "histogram":
                                            x = chart.get("x_axis")
                                            hist_chart = alt.Chart(chart_data).mark_bar(
                                                color="#3b82f6", opacity=0.85,
                                                cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                                            ).encode(
                                                x=alt.X(field=x, type="quantitative",
                                                        bin=alt.Bin(maxbins=20), title=x),
                                                y=alt.Y("count()", title="Frequency"),
                                                tooltip=[
                                                    alt.Tooltip(field=x, bin=True, format=num_fmt),
                                                    alt.Tooltip("count()", title="Count")
                                                ]
                                            ).properties(height=H)
                                            st.altair_chart(
                                                hist_chart.configure_axis(**AXIS_CFG).configure_view(**VIEW_CFG),
                                                use_container_width=True
                                            )

                                        # ── 10. WATERFALL ────────────────────────────────
                                        elif chart_type == "waterfall_chart":
                                            x    = chart.get("x_axis")
                                            y    = chart.get("y_axis")
                                            wf_df = chart_data.copy()
                                            wf_df["_dir"] = wf_df[y].apply(
                                                lambda v: "Positive" if v >= 0 else "Negative"
                                            )
                                            wf = alt.Chart(wf_df).mark_bar(
                                                cornerRadiusTopLeft=4, cornerRadiusTopRight=4,
                                                cornerRadiusBottomLeft=4, cornerRadiusBottomRight=4
                                            ).encode(
                                                x=alt.X(field=x, type="nominal", sort=None, title=x),
                                                y=alt.Y(field=y, type="quantitative", title=y),
                                                color=alt.Color(
                                                    field="_dir", type="nominal",
                                                    scale=alt.Scale(
                                                        domain=["Positive", "Negative"],
                                                        range=["#34d399", "#f87171"]
                                                    ),
                                                    legend=alt.Legend(title="Direction")
                                                ),
                                                tooltip=[x, alt.Tooltip(field=y, format=",.2f")]
                                            ).properties(height=H)
                                            zero_line = alt.Chart(
                                                pd.DataFrame({"zero": [0]})
                                            ).mark_rule(
                                                color="#94a3b8", strokeWidth=1.5, strokeDash=[4, 2]
                                            ).encode(y=alt.Y("zero:Q"))
                                            st.altair_chart(
                                                (wf + zero_line)
                                                .configure_axis(**AXIS_CFG)
                                                .configure_view(**VIEW_CFG)
                                                .configure_legend(**LEG_CFG),
                                                use_container_width=True
                                            )

                                    except Exception as chart_err:
                                        st.warning(f"⚠️ Could not render chart '{title}': {chart_err}")

                    else:
                        st.error(f"Analysis failed: {response.json().get('detail', response.text)}")

                except Exception as e:
                    st.error(f"Error calling backend: {str(e)}")
    else:
        st.info("💡 Welcome to Boardroom AI! Please upload one or more CSV datasets in the sidebar to begin.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Fleet Telemetry & Ops
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    # ── Auto-refresh when a new query just completed ──────────────────────────
    if not st.session_state.get("telemetry_refreshed", True):
        st.session_state["telemetry_refreshed"] = True
        st.rerun()

    st.markdown("""
<div style="padding:1.2rem 1.5rem;background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);
border-radius:12px;border:1px solid #334155;margin-bottom:1.5rem;">
    <h2 style="color:#60a5fa;margin:0;font-size:1.6rem;">📈 Fleet Telemetry &amp; Ops Center</h2>
    <p style="color:#94a3b8;margin:0.4rem 0 0 0;font-size:0.95rem;">
        Live agent execution metrics, cost tracking, workflow states, and security audit trail.
    </p>
</div>
""", unsafe_allow_html=True)

    col_refresh, col_hint = st.columns([1, 5])
    with col_refresh:
        refresh = st.button("🔄 Refresh", type="secondary", use_container_width=True)
    with col_hint:
        last_ts = st.session_state.get("last_query_ts")
        if last_ts:
            import datetime as _dt_ui
            last_str = _dt_ui.datetime.fromtimestamp(last_ts).strftime("%H:%M:%S")
            st.caption(f"✅ Last query completed at {last_str}. Data fetched live from SQLite database.")
        else:
            st.caption("Data is fetched live from the local SQLite database. Run a query in the Strategic Portal to see real-time updates.")
    if refresh:
        st.rerun()

    try:
        stats_resp = requests.get(f"{BACKEND_URL}/api/observability/stats", timeout=5)
        runs_resp  = requests.get(f"{BACKEND_URL}/api/observability/runs", timeout=5)
        inv_resp   = requests.get(f"{BACKEND_URL}/api/observability/investigations", timeout=5)
        sec_resp   = requests.get(f"{BACKEND_URL}/api/observability/security_events", timeout=5)

        if all(r.status_code == 200 for r in [stats_resp, runs_resp, inv_resp, sec_resp]):
            stats = stats_resp.json()
            runs  = runs_resp.json()
            invs  = inv_resp.json()
            secs  = sec_resp.json()

            # ── Fleet Health KPIs ─────────────────────────────────────────
            st.markdown('<div class="section-header">⚡ Fleet Health KPIs</div>', unsafe_allow_html=True)

            df_runs_kpi = pd.DataFrame(runs) if runs else pd.DataFrame()
            if not df_runs_kpi.empty and "status" in df_runs_kpi.columns:
                completed  = len(df_runs_kpi[df_runs_kpi["status"] == "COMPLETED"])
                total_r    = len(df_runs_kpi)
                all_agents = total_r   # every logged run (RUNNING, COMPLETED, SKIPPED) counts
                success_rate_val = f"{(completed/total_r)*100:.1f}%" if total_r else "—"
            else:
                success_rate_val = "—"
                all_agents = 0

            # stats.total_agent_runs only counts COMPLETED; use live count from runs list
            total_agents = all_agents if all_agents > 0 else stats.get("total_agent_runs", 0)
            avg_latency  = stats.get("avg_agent_duration", 0.0)
            sec_alerts   = stats.get("total_security_events", 0)
            total_inv_db = len(invs)

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Agent Runs</div><div class="kpi-value kpi-blue">{total_agents}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Latency</div><div class="kpi-value kpi-amber">{avg_latency:.1f}s</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card"><div class="kpi-label">Success Rate</div><div class="kpi-value kpi-green">{success_rate_val}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="kpi-card"><div class="kpi-label">Investigations</div><div class="kpi-value kpi-purple">{total_inv_db}</div></div>', unsafe_allow_html=True)
            k5.markdown(f'<div class="kpi-card"><div class="kpi-label">Security Alerts</div><div class="kpi-value kpi-red">{sec_alerts}</div></div>', unsafe_allow_html=True)

            # ── Token & Cost Metrics ──────────────────────────────────────
            st.markdown('<div class="section-header">🪙 Token Consumption &amp; Cost Metrics</div>', unsafe_allow_html=True)
            total_input  = stats.get("total_input_tokens", 0)
            total_output = stats.get("total_output_tokens", 0)
            total_tokens = stats.get("total_tokens", total_input + total_output)
            total_cost   = stats.get("total_api_cost_usd", 0.0)

            t1, t2, t3, t4 = st.columns(4)
            t1.markdown(f'<div class="kpi-card"><div class="kpi-label">Input Tokens</div><div class="kpi-value kpi-blue">{total_input:,}</div></div>', unsafe_allow_html=True)
            t2.markdown(f'<div class="kpi-card"><div class="kpi-label">Output Tokens</div><div class="kpi-value kpi-blue">{total_output:,}</div></div>', unsafe_allow_html=True)
            t3.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Tokens</div><div class="kpi-value kpi-amber">{total_tokens:,}</div></div>', unsafe_allow_html=True)
            t4.markdown(f'<div class="kpi-card"><div class="kpi-label">API Cost (USD)</div><div class="kpi-value kpi-green">${total_cost:.5f}</div></div>', unsafe_allow_html=True)

            # ── Model Configuration ───────────────────────────────────────
            st.markdown('<div class="section-header">⚙️ Model &amp; Context Window Configuration</div>', unsafe_allow_html=True)
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.info(f"**Primary Model**\n\n`{stats.get('configured_model','N/A')}`")
            mc2.info(f"**Fallback Model**\n\n`{stats.get('configured_fallback_model','N/A')}`")
            mc3.info(f"**Max Output**\n\n`{stats.get('max_output_tokens',0):,}` tokens")
            mc4.info(f"**Skill Limit**\n\n`{stats.get('max_skill_chars',0):,}` chars")

            # ── Workflow State Transitions ────────────────────────────────
            st.markdown('<div class="section-header">🔄 Live Workflow State Transitions</div>', unsafe_allow_html=True)
            if invs:
                df_invs = pd.DataFrame(invs)
                def get_state_badge(state):
                    mapping = {
                        "COMPLETED":     "🟢 COMPLETED",
                        "FAILED":        "🔴 FAILED",
                        "PENDING":       "⚪ PENDING",
                        "RUNNING":       "🔵 RUNNING",
                        "INVESTIGATING": "🟠 INVESTIGATING",
                        "EVALUATING":    "🟣 EVALUATING",
                    }
                    return mapping.get(state.upper(), f"🔹 {state}")
                df_invs["State"] = df_invs["state"].apply(get_state_badge)
                st.dataframe(
                    df_invs[["created_at", "question", "State", "id"]].rename(columns={
                        "created_at": "Timestamp",
                        "question":   "User Query",
                        "id":         "Investigation ID"
                    }),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.info("🔄 No investigations logged yet. Run a query in the Strategic Portal to populate this table.")

            # ── Agent Run Logs ────────────────────────────────────────────
            run_count_badge = f" ({len(runs)})" if runs else ""
            st.markdown(f'<div class="section-header">📋 Specialist Agent Execution Logs{run_count_badge}</div>', unsafe_allow_html=True)
            if runs:
                df_runs_disp = pd.DataFrame(runs)

                # Status badges
                status_icons = {
                    "COMPLETED": "🟢 COMPLETED",
                    "RUNNING":   "🔵 RUNNING",
                    "FAILED":    "🔴 FAILED",
                    "SKIPPED":   "⚪ SKIPPED",
                }
                if "status" in df_runs_disp.columns:
                    df_runs_disp["Status"] = df_runs_disp["status"].apply(
                        lambda s: status_icons.get(str(s).upper(), f"🔹 {s}")
                    )
                if "duration" in df_runs_disp.columns:
                    df_runs_disp["Duration (s)"] = df_runs_disp["duration"].apply(
                        lambda d: f"{float(d):.2f}s" if d is not None else "—"
                    )

                display_cols = []
                rename_map   = {}
                for c, label in [("agent_name","Agent"), ("Status","Status"), ("Duration (s)","Duration (s)"),
                                  ("start_time","Started"), ("end_time","Ended"), ("id","Run ID")]:
                    if c in df_runs_disp.columns:
                        display_cols.append(c)
                        rename_map[c] = label

                st.dataframe(
                    df_runs_disp[display_cols].rename(columns=rename_map),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.info("📋 No agent runs logged yet. Run a query in the Strategic Advisory Portal to populate this table.")

            # ── Security Audit Trail ──────────────────────────────────────
            st.markdown('<div class="section-header">🛡️ Security Audit Trail &amp; Event Logs</div>', unsafe_allow_html=True)
            if secs:
                df_secs = pd.DataFrame(secs)
                avail_sec = [c for c in ["created_at", "event_type", "severity", "message", "id"] if c in df_secs.columns]
                rename_sec = {
                    "created_at": "Timestamp", "event_type": "Event Type",
                    "severity": "Severity", "message": "Message", "id": "Event ID"
                }
                st.dataframe(
                    df_secs[avail_sec].rename(columns=rename_sec),
                    width="stretch",
                    hide_index=True
                )
            else:
                st.success("✅ No security alerts logged. System is secure.")

        else:
            st.error(
                f"❌ Failed to retrieve telemetry from backend. "
                f"Status: stats={stats_resp.status_code}, runs={runs_resp.status_code}, "
                f"inv={inv_resp.status_code}, sec={sec_resp.status_code}"
            )

    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Cannot connect to the backend API (http://localhost:8000). Please ensure the backend server is running.")
    except Exception as e:
        st.error(f"Error fetching telemetry data: {str(e)}")
