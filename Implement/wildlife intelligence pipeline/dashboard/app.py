"""
dashboard/app.py - Wildlife Intelligence Monitoring System
Main Streamlit Dashboard

Run: streamlit run dashboard/app.py
"""
import sys
import time
import io
from pathlib import Path
from datetime import datetime

# Ensure project root in path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import func

from backend.database.connection import init_db, get_session
from backend.database.models import Animal, Upload, PipelineLog
from pipeline.pipeline_runner import PipelineRunner
from pipeline.exporter import DataExporter

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wildlife Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize DB
init_db()

# ── CSS Theme ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0a0e0f;
    --bg-secondary: #0f1517;
    --bg-card: #141b1d;
    --bg-card-hover: #1a2326;
    --accent-green: #00d97e;
    --accent-teal: #00b8a9;
    --accent-amber: #f5a623;
    --accent-red: #ff4d6d;
    --accent-blue: #4fc3f7;
    --text-primary: #e8f4f0;
    --text-secondary: #8aaba2;
    --text-muted: #4a6560;
    --border: #1e2d2a;
    --border-accent: #00d97e33;
    --glow: 0 0 20px #00d97e22;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding: 1.5rem 2rem; max-width: 100%;}

/* Global background */
.stApp {
    background: var(--bg-primary);
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container {padding: 1.5rem 1rem;}

/* Metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
.metric-card:hover {
    border-color: var(--accent-green);
    box-shadow: var(--glow);
    transform: translateY(-2px);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-teal));
}
.metric-label {
    color: var(--text-secondary);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-value {
    color: var(--text-primary);
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.metric-sub {
    color: var(--accent-green);
    font-size: 0.75rem;
    margin-top: 0.4rem;
    font-weight: 500;
}

/* Section headers */
.section-header {
    color: var(--text-primary);
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0f1e1a 0%, #0a1912 50%, #071410 100%);
    border: 1px solid var(--border-accent);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 40%;
    height: 200%;
    background: radial-gradient(ellipse, #00d97e08 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-title span {color: var(--accent-green);}
.hero-subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 0.4rem;
}

/* Nav pills in sidebar */
.nav-pill {
    display: block;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    margin-bottom: 0.25rem;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
}
.nav-pill:hover, .nav-pill.active {
    background: var(--bg-card-hover);
    color: var(--accent-green);
    border-color: var(--border-accent);
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-danger {background: #ff4d6d22; color: #ff4d6d;}
.badge-warning {background: #f5a62322; color: #f5a623;}
.badge-success {background: #00d97e22; color: #00d97e;}
.badge-info {background: #4fc3f722; color: #4fc3f7;}

/* Quality bar */
.quality-bar-bg {
    background: var(--border);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin-top: 0.5rem;
}
.quality-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-teal));
    transition: width 1s ease;
}

/* Tables */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border-radius: 8px;
    border: 1px solid var(--border) !important;
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.stTextInput input:focus {border-color: var(--accent-green) !important;}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-teal));
    color: #0a0e0f !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em;
    transition: all 0.2s !important;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px #00d97e44 !important;
}

/* Download buttons */
.stDownloadButton button {
    background: var(--bg-card) !important;
    color: var(--accent-green) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}
.stDownloadButton button:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--accent-green) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-secondary);
    border-radius: 7px;
    border: none;
    font-weight: 500;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card-hover) !important;
    color: var(--accent-green) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-card);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-green);
}

/* Divider */
hr {border-color: var(--border) !important; margin: 1.5rem 0;}

/* Logo area */
.logo-text {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--accent-green);
    letter-spacing: -0.01em;
}
.logo-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* Info box */
.info-box {
    background: var(--bg-card);
    border-left: 3px solid var(--accent-teal);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Toast-like success */
.toast-success {
    background: #00d97e15;
    border: 1px solid var(--accent-green);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: var(--accent-green);
    font-weight: 500;
    font-size: 0.85rem;
}

/* Scrollbar */
::-webkit-scrollbar {width: 5px; height: 5px;}
::-webkit-scrollbar-track {background: var(--bg-primary);}
::-webkit-scrollbar-thumb {background: var(--text-muted); border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# ── Plotly Chart Theme ────────────────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk", color="#8aaba2", size=11),
    margin=dict(l=20, r=20, t=35, b=20),
    colorway=["#00d97e", "#00b8a9", "#4fc3f7", "#f5a623", "#ff4d6d",
               "#a78bfa", "#fb923c", "#34d399", "#60a5fa", "#f472b6"],
)


def apply_chart_theme(fig):
    fig.update_layout(**CHART_THEME)
    fig.update_xaxes(gridcolor="#1e2d2a", linecolor="#1e2d2a", tickcolor="#4a6560")
    fig.update_yaxes(gridcolor="#1e2d2a", linecolor="#1e2d2a", tickcolor="#4a6560")
    return fig


# ── Data Helpers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_animals() -> pd.DataFrame:
    session = get_session()
    try:
        animals = session.query(Animal).filter(Animal.is_active == True).all()
        if not animals:
            return pd.DataFrame()
        return pd.DataFrame([a.to_dict() for a in animals])
    finally:
        session.close()


def get_kpis():
    session = get_session()
    try:
        total = session.query(Animal).filter(Animal.is_active == True).count()
        endangered = session.query(Animal).filter(
            Animal.is_active == True,
            Animal.conservation_status.in_(["Endangered", "Critically Endangered"])
        ).count()
        habitats_raw = session.query(Animal.habitat).filter(Animal.is_active == True).all()
        habitats = set()
        for (h,) in habitats_raw:
            if h:
                for hh in str(h).split(","):
                    habitats.add(hh.strip())
        return {"total": total, "endangered": endangered, "habitats": len(habitats)}
    finally:
        session.close()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem'>
        <div class='logo-text'>🌿 Wildlife Intel</div>
        <div class='logo-sub'>Monitoring System v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "Navigate",
        ["📊 Dashboard", "📁 Upload & Pipeline", "🔍 Search & Browse",
         "✏️ CRUD Manager", "📤 Export Center", "📋 Pipeline Logs"],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    kpis = get_kpis()
    st.markdown(f"""
    <div style='padding: 0.3rem 0'>
        <div style='color: #4a6560; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem;'>Live Stats</div>
        <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
            <span style='color: #8aaba2; font-size: 0.8rem;'>Total Animals</span>
            <span style='color: #00d97e; font-weight: 700; font-family: monospace;'>{kpis['total']}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
            <span style='color: #8aaba2; font-size: 0.8rem;'>Endangered</span>
            <span style='color: #ff4d6d; font-weight: 700; font-family: monospace;'>{kpis['endangered']}</span>
        </div>
        <div style='display: flex; justify-content: space-between;'>
            <span style='color: #8aaba2; font-size: 0.8rem;'>Habitats</span>
            <span style='color: #4fc3f7; font-weight: 700; font-family: monospace;'>{kpis['habitats']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='color: #4a6560; font-size: 0.7rem; text-align: center;'>{datetime.now().strftime('%d %b %Y · %H:%M')}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>Wildlife <span>Intelligence</span> Monitoring</div>
        <div class='hero-subtitle'>Real-time analytics · Conservation tracking · Biodiversity insights</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_animals()

    if df.empty:
        st.warning("⚠️ No data loaded yet. Go to **Upload & Pipeline** to load your datasets.")
        st.stop()

    # KPI Cards
    total = len(df)
    endangered_count = len(df[df["conservation_status"].isin(["Endangered", "Critically Endangered"])])
    vulnerable_count = len(df[df["conservation_status"] == "Vulnerable"])
    avg_speed = df["top_speed_kmh"].replace(0, None).dropna().mean()
    avg_risk = df["risk_score"].dropna().mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "TOTAL SPECIES", f"{total:,}", "In database", ""),
        (c2, "ENDANGERED", f"{endangered_count}", "Critical + Endangered", "danger"),
        (c3, "VULNERABLE", f"{vulnerable_count}", "At-risk species", "warning"),
        (c4, "AVG SPEED", f"{avg_speed:.0f} km/h", "Across all animals", ""),
        (c5, "AVG RISK SCORE", f"{avg_risk:.1f}", "Out of 100", ""),
    ]
    for col, label, value, sub, style in cards:
        with col:
            color = {"danger": "#ff4d6d", "warning": "#f5a623"}.get(style, "#00d97e")
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value' style='color: {color};'>{value}</div>
                <div class='metric-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Conservation + Diet ────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section-header'>🛡️ Conservation Status</div>", unsafe_allow_html=True)
        cons = df["conservation_status"].value_counts().reset_index()
        cons.columns = ["Status", "Count"]
        color_map = {
            "Least Concern": "#00d97e", "Near Threatened": "#4fc3f7",
            "Vulnerable": "#f5a623", "Endangered": "#fb923c",
            "Critically Endangered": "#ff4d6d", "Extinct": "#8b0000", "Unknown": "#4a6560"
        }
        fig = px.bar(cons, x="Count", y="Status", orientation="h",
                     color="Status", color_discrete_map=color_map,
                     title="Animals by Conservation Status")
        apply_chart_theme(fig)
        fig.update_layout(showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        st.markdown("<div class='section-header'>🍃 Diet Distribution</div>", unsafe_allow_html=True)
        diet = df["diet"].value_counts().reset_index()
        diet.columns = ["Diet", "Count"]
        fig = px.pie(diet, values="Count", names="Diet",
                     title="Diet Type Distribution", hole=0.45)
        apply_chart_theme(fig)
        fig.update_layout(height=280, legend=dict(
            orientation="v", x=1.0, font=dict(size=10)
        ))
        fig.update_traces(textfont_color="white", textposition="inside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2: Speed + Risk ───────────────────────────────────────────────────
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown("<div class='section-header'>⚡ Top Speed Animals</div>", unsafe_allow_html=True)
        speed_df = df[df["top_speed_kmh"] > 0].nlargest(12, "top_speed_kmh")[["name", "top_speed_kmh", "speed_category"]]
        fig = px.bar(speed_df, x="top_speed_kmh", y="name", orientation="h",
                     color="top_speed_kmh", color_continuous_scale=["#00d97e", "#f5a623", "#ff4d6d"],
                     title="Fastest Animals (km/h)")
        apply_chart_theme(fig)
        fig.update_layout(height=320, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r2:
        st.markdown("<div class='section-header'>⚠️ Risk Score Distribution</div>", unsafe_allow_html=True)
        fig = px.histogram(df.dropna(subset=["risk_score"]),
                           x="risk_score", nbins=20,
                           title="Risk Score Distribution",
                           color_discrete_sequence=["#00d97e"])
        apply_chart_theme(fig)
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Row 3: Size + Social ──────────────────────────────────────────────────
    col_l3, col_r3 = st.columns(2)

    with col_l3:
        st.markdown("<div class='section-header'>📏 Size Category</div>", unsafe_allow_html=True)
        size = df["size_category"].value_counts().reset_index()
        size.columns = ["Size", "Count"]
        fig = px.bar(size, x="Size", y="Count", color="Size",
                     title="Animals by Size Category",
                     color_discrete_sequence=CHART_THEME["colorway"])
        apply_chart_theme(fig)
        fig.update_layout(height=270, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r3:
        st.markdown("<div class='section-header'>👥 Social Structure</div>", unsafe_allow_html=True)
        social = df["social_structure"].value_counts().reset_index()
        social.columns = ["Structure", "Count"]
        fig = px.pie(social.head(7), values="Count", names="Structure",
                     title="Social Structure Distribution", hole=0.4)
        apply_chart_theme(fig)
        fig.update_layout(height=270)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Top Endangered ────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🚨 Highest Risk Animals</div>", unsafe_allow_html=True)
    top_risk = df.nlargest(10, "risk_score")[
        ["name", "conservation_status", "risk_score", "survival_probability", "habitat"]
    ].copy()

    fig = px.scatter(top_risk, x="survival_probability", y="risk_score",
                     size="risk_score", color="conservation_status",
                     text="name", title="Risk vs Survival Probability",
                     color_discrete_map={
                         "Critically Endangered": "#ff4d6d",
                         "Endangered": "#fb923c",
                         "Vulnerable": "#f5a623",
                         "Least Concern": "#00d97e",
                     })
    apply_chart_theme(fig)
    fig.update_traces(textposition="top center", textfont=dict(size=10))
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD & PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📁 Upload & Pipeline":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>Upload & <span>Pipeline</span></div>
        <div class='hero-subtitle'>Auto ETL · Validate → Clean → Engineer → Load</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>📂 Upload CSV Dataset</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='info-box'>
    Upload any wildlife CSV. The pipeline will auto-validate, clean, apply feature engineering,
    and load to the database — deduplicating against existing data.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop CSV here or click to browse",
        type=["csv"],
        accept_multiple_files=False,
    )

    if uploaded:
        df_preview = pd.read_csv(uploaded)
        st.markdown(f"**Preview** — {len(df_preview)} rows, {len(df_preview.columns)} columns")
        st.dataframe(df_preview.head(5), use_container_width=True)

        if st.button("🚀 Run ETL Pipeline", use_container_width=True):
            with st.spinner("Running pipeline..."):
                runner = PipelineRunner()
                df_upload = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                result = runner.run(df_upload, source_file=uploaded.name)
                load_animals.clear()

            if result["status"] == "success":
                st.markdown(f"""
                <div class='toast-success'>
                ✅ Pipeline completed successfully!<br>
                Inserted: <strong>{result['rows_inserted']}</strong> ·
                Skipped: <strong>{result['rows_skipped']}</strong> ·
                Quality: <strong>{result['quality_score']}%</strong> ·
                Time: <strong>{result['elapsed_seconds']}s</strong>
                </div>
                """, unsafe_allow_html=True)
                if result.get("warnings"):
                    for w in result["warnings"]:
                        st.warning(f"⚠️ {w}")
            else:
                st.error(f"❌ Pipeline failed: {result.get('error')}")

    st.markdown("<div class='section-header'>📜 Upload History</div>", unsafe_allow_html=True)
    session = get_session()
    try:
        uploads = session.query(Upload).order_by(Upload.uploaded_at.desc()).limit(20).all()
    finally:
        session.close()

    if uploads:
        upload_data = []
        for u in uploads:
            status_badge = {
                "success": "🟢", "failed": "🔴", "pending": "🟡"
            }.get(u.status, "⚪")
            upload_data.append({
                "Status": f"{status_badge} {u.status.title()}",
                "File": u.filename,
                "Rows": u.rows_total,
                "Inserted": u.rows_inserted,
                "Skipped": u.rows_duplicate,
                "Quality %": u.quality_score,
                "Uploaded": str(u.uploaded_at)[:16] if u.uploaded_at else "-",
            })
        st.dataframe(pd.DataFrame(upload_data), use_container_width=True, hide_index=True)
    else:
        st.info("No uploads yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH & BROWSE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Search & Browse":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>Search & <span>Browse</span></div>
        <div class='hero-subtitle'>Real-time filtering · Multi-dimensional search</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_animals()
    if df.empty:
        st.warning("No data loaded yet.")
        st.stop()

    # Search bar + filters
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        q = st.text_input("🔍 Search animals...", placeholder="Name, habitat, country...")
    with col2:
        habitats = ["All"] + sorted(df["habitat"].dropna().unique().tolist())
        habitat_filter = st.selectbox("Habitat", habitats)
    with col3:
        statuses = ["All"] + sorted(df["conservation_status"].dropna().unique().tolist())
        status_filter = st.selectbox("Conservation", statuses)
    with col4:
        diets = ["All"] + sorted(df["diet"].dropna().unique().tolist())
        diet_filter = st.selectbox("Diet", diets)

    # Apply filters
    filtered = df.copy()
    if q:
        mask = (
            filtered["name"].str.contains(q, case=False, na=False) |
            filtered["habitat"].str.contains(q, case=False, na=False) |
            filtered["countries_found"].str.contains(q, case=False, na=False)
        )
        filtered = filtered[mask]
    if habitat_filter != "All":
        filtered = filtered[filtered["habitat"].str.contains(habitat_filter, case=False, na=False)]
    if status_filter != "All":
        filtered = filtered[filtered["conservation_status"] == status_filter]
    if diet_filter != "All":
        filtered = filtered[filtered["diet"] == diet_filter]

    st.markdown(f"<div style='color: #8aaba2; font-size: 0.85rem; margin: 0.5rem 0;'>Showing <strong style='color: #00d97e;'>{len(filtered)}</strong> of {len(df)} animals</div>", unsafe_allow_html=True)

    # Display columns
    display_cols = ["name", "habitat", "diet", "top_speed_kmh", "conservation_status",
                    "countries_found", "size_category", "risk_score", "survival_probability"]
    available_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(
        filtered[available_cols].rename(columns={
            "name": "Animal", "habitat": "Habitat", "diet": "Diet",
            "top_speed_kmh": "Speed (km/h)", "conservation_status": "Status",
            "countries_found": "Countries", "size_category": "Size",
            "risk_score": "Risk Score", "survival_probability": "Survival Prob."
        }),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CRUD MANAGER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ CRUD Manager":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>CRUD <span>Manager</span></div>
        <div class='hero-subtitle'>Create · Read · Update · Delete wildlife records</div>
    </div>
    """, unsafe_allow_html=True)

    tab_create, tab_edit, tab_delete = st.tabs(["➕ Create", "✏️ Update", "🗑️ Delete"])

    with tab_create:
        st.markdown("### Add New Animal")
        with st.form("create_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Animal Name *", placeholder="e.g. Snow Leopard")
            conservation = c2.selectbox("Conservation Status",
                ["Unknown", "Least Concern", "Near Threatened", "Vulnerable",
                 "Endangered", "Critically Endangered", "Extinct"])
            c3, c4 = st.columns(2)
            habitat = c3.text_input("Habitat", placeholder="e.g. Mountain, Forest")
            diet = c4.selectbox("Diet", ["Unknown", "Carnivore", "Herbivore", "Omnivore",
                                          "Insectivore", "Piscivore"])
            c5, c6 = st.columns(2)
            speed = c5.number_input("Top Speed (km/h)", min_value=0.0, step=0.5)
            weight = c6.text_input("Weight (kg)", placeholder="e.g. 40-65")
            height = c1.text_input("Height (cm)", placeholder="e.g. 100-120")
            color = c2.text_input("Color", placeholder="e.g. Orange-Black")
            countries = c3.text_input("Countries Found", placeholder="e.g. India, Nepal")
            social = c4.selectbox("Social Structure",
                ["Unknown", "Solitary", "Pair", "Group", "Pack", "Herd"])
            submitted = st.form_submit_button("➕ Create Animal", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Animal name is required.")
            else:
                from pipeline.feature_engineering import FeatureEngineer
                session = get_session()
                try:
                    # Check duplicate
                    existing = session.query(Animal).filter(
                        Animal.name.ilike(name.strip())
                    ).first()
                    if existing:
                        st.error(f"'{name}' already exists.")
                    else:
                        import pandas as _pd
                        fe = FeatureEngineer()
                        row = {"name": name, "weight_kg": weight, "top_speed_kmh": speed,
                               "conservation_status": conservation, "social_structure": social}
                        row_df = _pd.DataFrame([row])
                        row_df = fe.engineer(row_df)

                        animal = Animal(
                            name=name.strip().title(), habitat=habitat, diet=diet,
                            top_speed_kmh=speed if speed > 0 else None,
                            weight_kg=weight, height_cm=height, color=color,
                            countries_found=countries, social_structure=social,
                            conservation_status=conservation, source_file="manual",
                            size_category=row_df["size_category"].iloc[0],
                            speed_category=row_df["speed_category"].iloc[0],
                            risk_score=float(row_df["risk_score"].iloc[0]),
                            endangered_level=int(row_df["endangered_level"].iloc[0]),
                            survival_probability=float(row_df["survival_probability"].iloc[0]),
                        )
                        session.add(animal)
                        session.commit()
                        load_animals.clear()
                        st.success(f"✅ '{name}' added successfully! (ID: {animal.id})")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    session.close()

    with tab_edit:
        st.markdown("### Update Animal Record")
        df_edit = load_animals()
        if not df_edit.empty:
            animal_names = df_edit["name"].sort_values().tolist()
            selected_name = st.selectbox("Select Animal to Edit", animal_names)
            if selected_name:
                row = df_edit[df_edit["name"] == selected_name].iloc[0]
                with st.form("edit_form"):
                    c1, c2 = st.columns(2)
                    new_name = c1.text_input("Name", value=str(row["name"]))
                    new_status = c2.selectbox("Conservation Status",
                        ["Unknown", "Least Concern", "Near Threatened", "Vulnerable",
                         "Endangered", "Critically Endangered", "Extinct"],
                        index=["Unknown", "Least Concern", "Near Threatened", "Vulnerable",
                               "Endangered", "Critically Endangered", "Extinct"].index(
                            str(row["conservation_status"]) if str(row["conservation_status"]) in
                            ["Unknown", "Least Concern", "Near Threatened", "Vulnerable",
                             "Endangered", "Critically Endangered", "Extinct"] else "Unknown"))
                    c3, c4 = st.columns(2)
                    new_habitat = c3.text_input("Habitat", value=str(row["habitat"] or ""))
                    new_speed = c4.number_input("Top Speed (km/h)",
                                                value=float(row["top_speed_kmh"] or 0))
                    update_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

                if update_btn:
                    session = get_session()
                    try:
                        animal = session.query(Animal).filter(Animal.id == int(row["id"])).first()
                        if animal:
                            animal.name = new_name
                            animal.conservation_status = new_status
                            animal.habitat = new_habitat
                            animal.top_speed_kmh = new_speed if new_speed > 0 else None
                            session.commit()
                            load_animals.clear()
                            st.success(f"✅ Updated '{new_name}' successfully!")
                    finally:
                        session.close()

    with tab_delete:
        st.markdown("### Delete Animal Record")
        df_del = load_animals()
        if not df_del.empty:
            del_names = df_del["name"].sort_values().tolist()
            del_name = st.selectbox("Select Animal to Delete", del_names, key="del_select")
            if del_name:
                del_row = df_del[df_del["name"] == del_name].iloc[0]
                st.markdown(f"""
                <div class='info-box'>
                    <strong>{del_row['name']}</strong> · {del_row['conservation_status']} ·
                    {del_row['habitat']} · Risk: {del_row['risk_score']}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Delete '{del_name}'", type="secondary"):
                    session = get_session()
                    try:
                        animal = session.query(Animal).filter(
                            Animal.id == int(del_row["id"])
                        ).first()
                        if animal:
                            animal.is_active = False
                            session.commit()
                            load_animals.clear()
                            st.success(f"✅ '{del_name}' removed from database.")
                    finally:
                        session.close()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT CENTER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Export Center":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>Export <span>Center</span></div>
        <div class='hero-subtitle'>Download your data in any format — real-time</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_animals()
    if df.empty:
        st.warning("No data to export.")
        st.stop()

    # Filter before export
    st.markdown("<div class='section-header'>🎯 Export Filters</div>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter_exp = st.selectbox(
            "Conservation Status Filter",
            ["All"] + sorted(df["conservation_status"].dropna().unique().tolist())
        )
    with col_f2:
        col_select = st.multiselect(
            "Columns to include",
            options=df.columns.tolist(),
            default=["name", "habitat", "diet", "conservation_status", "top_speed_kmh",
                     "countries_found", "risk_score", "size_category", "survival_probability"],
        )

    df_export = df.copy()
    if status_filter_exp != "All":
        df_export = df_export[df_export["conservation_status"] == status_filter_exp]
    if col_select:
        df_export = df_export[[c for c in col_select if c in df_export.columns]]

    st.markdown(f"<div style='color: #8aaba2; font-size:0.85rem; margin: 0.5rem 0;'>Ready to export <strong style='color:#00d97e;'>{len(df_export):,}</strong> records</div>", unsafe_allow_html=True)

    exporter = DataExporter()

    st.markdown("<div class='section-header'>📥 Download Formats</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("**CSV**\n*Spreadsheet compatible*")
        st.download_button("⬇️ Download CSV", data=exporter.to_csv(df_export),
                           file_name="wildlife_data.csv", mime="text/csv",
                           use_container_width=True)

    with c2:
        st.markdown("**JSON**\n*API / web use*")
        st.download_button("⬇️ Download JSON", data=exporter.to_json(df_export),
                           file_name="wildlife_data.json", mime="application/json",
                           use_container_width=True)

    with c3:
        st.markdown("**Excel**\n*.xlsx format*")
        st.download_button("⬇️ Download XLSX", data=exporter.to_excel(df_export),
                           file_name="wildlife_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

    with c4:
        st.markdown("**Parquet**\n*Big data format*")
        st.download_button("⬇️ Download Parquet", data=exporter.to_parquet(df_export),
                           file_name="wildlife_data.parquet",
                           mime="application/octet-stream",
                           use_container_width=True)

    with c5:
        st.markdown("**SQL Dump**\n*Database backup*")
        st.download_button("⬇️ Download SQL", data=exporter.to_sql_dump(df_export),
                           file_name="wildlife_data.sql", mime="text/plain",
                           use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📊 Export Preview")
    st.dataframe(df_export.head(20), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PIPELINE LOGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Pipeline Logs":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>Pipeline <span>Logs</span></div>
        <div class='hero-subtitle'>ETL activity · Error tracking · System health</div>
    </div>
    """, unsafe_allow_html=True)

    session = get_session()
    try:
        logs = session.query(PipelineLog).order_by(PipelineLog.created_at.desc()).limit(100).all()
    finally:
        session.close()

    if logs:
        col_filter, _ = st.columns([2, 4])
        with col_filter:
            level_filter = st.selectbox("Filter by Level", ["All", "INFO", "WARNING", "ERROR"])

        log_data = []
        for log in logs:
            if level_filter != "All" and log.level != level_filter:
                continue
            icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(log.level, "•")
            log_data.append({
                "Time": str(log.created_at)[:19] if log.created_at else "-",
                "Level": f"{icon} {log.level}",
                "Stage": log.stage or "-",
                "Message": log.message[:120] + "..." if len(log.message or "") > 120 else log.message,
            })

        st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
    else:
        st.info("No pipeline logs yet. Run the ETL pipeline to see logs here.")

    # Log file preview
    log_file = Path(__file__).parent.parent / "logs" / "pipeline.log"
    if log_file.exists():
        st.markdown("<div class='section-header'>📄 Raw Log File (last 30 lines)</div>",
                    unsafe_allow_html=True)
        lines = log_file.read_text().strip().split("\n")
        last_lines = "\n".join(lines[-30:])
        st.code(last_lines, language="text")
