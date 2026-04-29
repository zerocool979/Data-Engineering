import os
import sys
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Path setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from upload_handler import save_uploaded_file
from pipeline_runner import run_pipeline, load_processed

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wildlife Intelligence Pipeline",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:       #0a0f0d;
    --surface:  #111a15;
    --card:     #162019;
    --border:   #1e3024;
    --accent:   #4ade80;
    --accent2:  #86efac;
    --amber:    #fbbf24;
    --red:      #f87171;
    --sky:      #38bdf8;
    --muted:    #6b7c70;
    --text:     #e2ede6;
    --text-dim: #8fa898;
}

/* ── Base ── */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stApp { background-color: var(--bg) !important; }
.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Hero header ── */
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5.5rem);
    letter-spacing: 0.06em;
    line-height: 1;
    background: linear-gradient(135deg, #4ade80 0%, #86efac 40%, #fbbf24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.hero-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
    margin: 1.5rem 0 2rem;
    border: none;
}

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--card-accent, var(--accent));
}
.stat-card:hover { border-color: var(--accent); }
.stat-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    color: var(--card-accent, var(--accent));
    line-height: 1;
}
.stat-label {
    font-size: 0.72rem;
    color: var(--text-dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.stat-icon { font-size: 1.6rem; float: right; opacity: 0.3; margin-top: -0.2rem; }

/* ── Section headers ── */
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.08em;
    color: var(--accent);
    border-left: 4px solid var(--accent);
    padding-left: 0.75rem;
    margin: 2.5rem 0 1.2rem;
}

/* ── Search card ── */
.search-result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
}
.animal-name-hero {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 1rem;
}
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; }
.detail-item {
    background: var(--surface);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    border: 1px solid var(--border);
}
.detail-label {
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.detail-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: var(--text);
    margin-top: 0.2rem;
    word-break: break-word;
}
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 99px;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}
.badge-green { background: #14532d; color: #86efac; }
.badge-amber { background: #451a03; color: #fbbf24; }
.badge-red   { background: #450a0a; color: #f87171; }
.badge-sky   { background: #0c4a6e; color: #38bdf8; }
.badge-gray  { background: #1f2937; color: #9ca3af; }

/* ── Upload zone ── */
.upload-zone {
    border: 2px dashed var(--border);
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    background: var(--card);
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: var(--accent); }

/* ── Streamlit component tweaks ── */
div[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
div[data-testid="stTextInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.15) !important;
}
div[data-testid="stSelectbox"] select {
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #166534, #14532d) !important;
    color: #86efac !important;
    border: 1px solid #4ade80 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    transition: all 0.15s !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #166534) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(74,222,128,0.25) !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e3a5f, #1e3a8a) !important;
    color: #93c5fd !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 8px !important;
}

/* Alerts */
.stSuccess { background: #14532d !important; border: 1px solid #4ade80 !important; border-radius: 8px !important; }
.stError   { background: #450a0a !important; border: 1px solid #f87171 !important; border-radius: 8px !important; }
.stWarning { background: #451a03 !important; border: 1px solid #fbbf24 !important; border-radius: 8px !important; }
.stInfo    { background: #0c4a6e !important; border: 1px solid #38bdf8 !important; border-radius: 8px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--accent) !important;
}

/* Dataframe */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }

/* Sidebar nav items */
.nav-item {
    display: block;
    padding: 0.65rem 1rem;
    border-radius: 8px;
    color: var(--text-dim) !important;
    text-decoration: none;
    font-size: 0.9rem;
    margin: 2px 0;
    transition: background 0.15s;
    cursor: pointer;
}
.nav-item:hover, .nav-item.active {
    background: var(--card);
    color: var(--accent) !important;
}

/* Chart containers */
.chart-container {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

/* Metric */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: var(--text-dim) !important; font-size: 0.72rem !important; letter-spacing: 0.1em !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)


# ── Plotly theme ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#e2ede6", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e3024", linecolor="#1e3024", zerolinecolor="#1e3024"),
    yaxis=dict(gridcolor="#1e3024", linecolor="#1e3024", zerolinecolor="#1e3024"),
    colorway=["#4ade80", "#fbbf24", "#38bdf8", "#f87171", "#a78bfa",
              "#fb923c", "#34d399", "#f472b6", "#a3e635", "#60a5fa"],
)

PALETTE = ["#4ade80", "#fbbf24", "#38bdf8", "#f87171",
           "#a78bfa", "#fb923c", "#34d399", "#f472b6"]


def conservation_badge(status: str) -> str:
    s = str(status).strip()
    if "Least" in s:     return f'<span class="badge badge-green">{s}</span>'
    if "Vulnerable" in s: return f'<span class="badge badge-amber">{s}</span>'
    if "Endangered" in s: return f'<span class="badge badge-red">{s}</span>'
    if "Extinct" in s:   return f'<span class="badge badge-gray">{s}</span>'
    return f'<span class="badge badge-sky">{s}</span>'


# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_processed()
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 0 1.5rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;
                    color:#4ade80;letter-spacing:0.1em;">🦁 WILDLIFE</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                    color:#6b7c70;letter-spacing:0.2em;margin-top:2px;">
            INTELLIGENCE PIPELINE
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1e3024;margin:0 0 1.2rem;">
    """, unsafe_allow_html=True)

    pages = {
        "Dashboard":     "📊",
        "Search Animal": "🔍",
        "Upload Data":   "📤",
    }

    for name, icon in pages.items():
        active = "active" if st.session_state.page == name else ""
        if st.button(f"{icon}  {name}", key=f"nav_{name}",
                     use_container_width=True):
            st.session_state.page = name

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem;color:#6b7c70;font-family:'JetBrains Mono',monospace;
                padding:0.8rem;background:#111a15;border-radius:8px;
                border:1px solid #1e3024;">
        <div style="color:#4ade80;margin-bottom:0.4rem;">PIPELINE STATUS</div>
        ✓ Read Master<br>
        ✓ Merge Dataset<br>
        ✓ Dedup & Clean<br>
        ✓ Feature Eng.<br>
        ✓ Dashboard Ready
    </div>
    """, unsafe_allow_html=True)


# ── Helper: get current dataframe ────────────────────────────────────────────
def get_df() -> pd.DataFrame:
    return st.session_state.df


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "Dashboard":
    # Hero
    st.markdown("""
    <h1 class="hero-title">WILDLIFE INTELLIGENCE PIPELINE</h1>
    <div class="hero-sub">Automated Data Engineering System · Animal Intelligence Platform</div>
    <hr class="hero-divider">
    """, unsafe_allow_html=True)

    df = get_df()

    if df.empty:
        st.error("⚠️ No data available. Please upload a dataset first.")
        st.stop()

    # ── Summary cards ──
    total_animals = len(df)
    total_habitats = df["Habitat"].nunique() if "Habitat" in df.columns else 0
    total_countries = df["Countries Found"].nunique() if "Countries Found" in df.columns else 0
    endangered = len(df[df["Conservation Status"].str.contains("Endangered", na=False)]) \
                 if "Conservation Status" in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="--card-accent:#4ade80">
            <div class="stat-icon">🦓</div>
            <div class="stat-number">{total_animals}</div>
            <div class="stat-label">Total Animals</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="--card-accent:#38bdf8">
            <div class="stat-icon">🏔️</div>
            <div class="stat-number">{total_habitats}</div>
            <div class="stat-label">Total Habitats</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="--card-accent:#fbbf24">
            <div class="stat-icon">🌍</div>
            <div class="stat-number">{total_countries}</div>
            <div class="stat-label">Total Countries</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card" style="--card-accent:#f87171">
            <div class="stat-icon">🚨</div>
            <div class="stat-number">{endangered}</div>
            <div class="stat-label">Endangered Animals</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row 1 ──
    st.markdown('<div class="section-header">CONSERVATION & HABITAT</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        if "Conservation Status" in df.columns:
            cs = df["Conservation Status"].value_counts().reset_index()
            cs.columns = ["Status", "Count"]
            fig = px.bar(cs, x="Count", y="Status", orientation="h",
                         title="Conservation Status Distribution",
                         color="Status", color_discrete_sequence=PALETTE)
            fig.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                              title_font=dict(family="Bebas Neue", size=18, color="#4ade80"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "Habitat" in df.columns:
            hab = df["Habitat"].value_counts().nlargest(8).reset_index()
            hab.columns = ["Habitat", "Count"]
            fig2 = px.pie(hab, values="Count", names="Habitat",
                          title="Habitat Distribution",
                          color_discrete_sequence=PALETTE, hole=0.4)
            fig2.update_layout(**PLOTLY_LAYOUT,
                               title_font=dict(family="Bebas Neue", size=18, color="#4ade80"))
            fig2.update_traces(textfont=dict(family="DM Sans"))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Charts row 2 ──
    st.markdown('<div class="section-header">SPEED & SIZE ANALYSIS</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        if "Top Speed (km/h)" in df.columns:
            speed_data = df["Top Speed (km/h)"].dropna()
            fig3 = px.histogram(df, x="Top Speed (km/h)",
                                title="Top Speed Distribution (km/h)",
                                color_discrete_sequence=["#4ade80"],
                                nbins=20, opacity=0.85)
            fig3.update_layout(**PLOTLY_LAYOUT,
                               title_font=dict(family="Bebas Neue", size=18, color="#4ade80"),
                               bargap=0.05)
            fig3.update_traces(marker_line_color="#0a0f0d", marker_line_width=0.5)
            st.plotly_chart(fig3, use_container_width=True)

    with c4:
        if "Size Category" in df.columns:
            sz = df["Size Category"].value_counts().reset_index()
            sz.columns = ["Size", "Count"]
            COLOR_MAP = {"Small": "#38bdf8", "Medium": "#fbbf24", "Large": "#f87171", "Unknown": "#6b7c70"}
            fig4 = px.bar(sz, x="Size", y="Count",
                          title="Animal Size Categories",
                          color="Size", color_discrete_map=COLOR_MAP)
            fig4.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                               title_font=dict(family="Bebas Neue", size=18, color="#4ade80"))
            fig4.update_traces(marker_line_width=0)
            st.plotly_chart(fig4, use_container_width=True)

    # ── Chart row 3: Countries ──
    st.markdown('<div class="section-header">GEOGRAPHIC DISTRIBUTION</div>', unsafe_allow_html=True)
    if "Countries Found" in df.columns:
        countries = df["Countries Found"].value_counts().nlargest(12).reset_index()
        countries.columns = ["Country", "Count"]
        fig5 = px.bar(countries, x="Country", y="Count",
                      title="Top 12 Countries by Animal Count",
                      color="Count", color_continuous_scale=["#14532d", "#4ade80"])
        fig5.update_layout(**PLOTLY_LAYOUT,
                           title_font=dict(family="Bebas Neue", size=18, color="#4ade80"),
                           coloraxis_showscale=False)
        fig5.update_traces(marker_line_width=0)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Raw data table ──
    st.markdown('<div class="section-header">DATA EXPLORER</div>', unsafe_allow_html=True)
    display_cols = [c for c in ["Animal", "Diet", "Habitat", "Conservation Status",
                                "Top Speed (km/h)", "Weight (kg)", "Size Category",
                                "Speed Category", "Countries Found"] if c in df.columns]
    st.dataframe(df[display_cols].sort_values("Animal"), use_container_width=True,
                 height=350, hide_index=True)

    # Download button
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇  Download Clean Dataset (CSV)",
        data=csv_bytes,
        file_name="wildlife_clean_data.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SEARCH ANIMAL
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Search Animal":
    st.markdown("""
    <h1 class="hero-title">ANIMAL SEARCH</h1>
    <div class="hero-sub">Query the Wildlife Intelligence Database</div>
    <hr class="hero-divider">
    """, unsafe_allow_html=True)

    df = get_df()

    if df.empty:
        st.error("⚠️ No data available. Please upload a dataset first.")
        st.stop()

    query = st.text_input("🔍  Enter animal name", placeholder="e.g. Lion, Elephant, Tiger...")

    if query:

        query_clean = query.strip().lower()

        if "Animal" in df.columns:

            animal_series = df["Animal"].str.lower()

            # 1️⃣ Exact Match
            exact_mask = animal_series == query_clean
            exact_results = df[exact_mask]

            if not exact_results.empty:

                results = exact_results

            else:

                # 2️⃣ Whole Word Match
                word_mask = df["Animal"].str.contains(
                    fr"\b{query_clean}\b",
                    case=False,
                    regex=True,
                    na=False
                )

                word_results = df[word_mask]

                if not word_results.empty:

                    results = word_results

                else:

                    # 3️⃣ Substring Match (fallback)
                    substring_mask = df["Animal"].str.contains(
                        query_clean,
                        case=False,
                        na=False
                    )

                    results = df[substring_mask]

        else:

            results = pd.DataFrame()

        if results.empty:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem;color:#6b7c70;">
                <div style="font-size:3rem;">🔭</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                            color:#f87171;margin-top:1rem;">Animal not found</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;">
                    No results for "<strong style="color:#e2ede6;">{query}</strong>"
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                        color:#6b7c70;margin-bottom:1rem;">
                {len(results)} result(s) found
            </div>""", unsafe_allow_html=True)

            for _, row in results.iterrows():
                FIELD_MAP = [
                    ("Height (cm)", "📏 Height"),
                    ("Weight (kg)", "⚖️ Weight"),
                    ("Diet", "🍃 Diet"),
                    ("Habitat", "🌿 Habitat"),
                    ("Predators", "⚠️ Predators"),
                    ("Top Speed (km/h)", "⚡ Top Speed"),
                    ("Countries Found", "🌍 Countries"),
                    ("Lifespan (years)", "⏳ Lifespan"),
                    ("Social Structure", "👥 Social"),
                    ("Offspring per Birth", "🐣 Offspring"),
                    ("Size Category", "📦 Size"),
                    ("Speed Category", "🏃 Speed Class"),
                ]

                def fmt_val(val):
                    if pd.isna(val): return "—"
                    if isinstance(val, float): return f"{val:,.1f}"
                    return str(val)

                details_html = "".join([
                    f"""<div class="detail-item">
                        <div class="detail-label">{label}</div>
                        <div class="detail-value">{fmt_val(row.get(col, "—"))}</div>
                    </div>"""
                    for col, label in FIELD_MAP if col in df.columns
                ])

                cs = str(row.get("Conservation Status", "—"))
                badge_html = conservation_badge(cs)

                st.markdown(f"""
                <div class="search-result-card">
                    <div class="animal-name-hero">{row.get('Animal','—')}</div>
                    <div style="margin-bottom:1.2rem;">{badge_html}
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                                     color:#6b7c70;margin-left:0.8rem;">
                            {row.get('Family','—')} · {row.get('Color','—')}
                        </span>
                    </div>
                    <div class="detail-grid">{details_html}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Show random suggestions
        if "Animal" in df.columns:
            suggestions = df["Animal"].dropna().sample(min(6, len(df))).tolist()
            pill_html = " ".join([
                f'<span style="background:#162019;border:1px solid #1e3024;'
                f'border-radius:99px;padding:0.3rem 0.8rem;font-size:0.8rem;'
                f'color:#86efac;cursor:pointer;">{a}</span>'
                for a in suggestions
            ])
            st.markdown(f"""
            <div style="color:#6b7c70;font-size:0.8rem;margin-bottom:0.8rem;">
                Try searching for:
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
                {pill_html}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: UPLOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Upload Data":
    st.markdown("""
    <h1 class="hero-title">UPLOAD DATA</h1>
    <div class="hero-sub">Append New Records · Auto Pipeline Execution</div>
    <hr class="hero-divider">
    """, unsafe_allow_html=True)

    # Pipeline steps visual
    st.markdown("""
    <div style="display:flex;gap:0;align-items:center;margin-bottom:2rem;
                background:#111a15;border-radius:12px;padding:1.2rem 1.5rem;
                border:1px solid #1e3024;overflow-x:auto;">
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">📂</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">UPLOAD</div>
        </div>
        <div style="flex:1;height:2px;background:linear-gradient(90deg,#4ade80,#1e3024);min-width:20px;"></div>
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">🔀</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">MERGE</div>
        </div>
        <div style="flex:1;height:2px;background:linear-gradient(90deg,#4ade80,#1e3024);min-width:20px;"></div>
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">🔍</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">DEDUP</div>
        </div>
        <div style="flex:1;height:2px;background:linear-gradient(90deg,#4ade80,#1e3024);min-width:20px;"></div>
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">🧹</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">CLEAN</div>
        </div>
        <div style="flex:1;height:2px;background:linear-gradient(90deg,#4ade80,#1e3024);min-width:20px;"></div>
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">⚙️</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">FEATURES</div>
        </div>
        <div style="flex:1;height:2px;background:linear-gradient(90deg,#4ade80,#1e3024);min-width:20px;"></div>
        <div style="text-align:center;min-width:90px;">
            <div style="font-size:1.4rem;">📊</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                        color:#4ade80;letter-spacing:0.1em;margin-top:0.3rem;">DASHBOARD</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">UPLOAD CSV FILE</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your CSV file here or click to browse",
        type=["csv"],
        help="Only CSV files are accepted. Data will be appended to the master dataset.",
    )

    if uploaded_file is not None:
        if not uploaded_file.name.endswith(".csv"):
            st.error("❌ Invalid file format. Only CSV files are accepted.")
        else:
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"""
                <div style="background:#162019;border:1px solid #1e3024;border-radius:10px;
                            padding:1rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:0.8rem;">
                    <div style="color:#6b7c70;font-size:0.65rem;letter-spacing:0.1em;">FILE READY</div>
                    <div style="color:#4ade80;margin-top:0.4rem;">📄 {uploaded_file.name}</div>
                    <div style="color:#6b7c70;margin-top:0.3rem;">
                        {uploaded_file.size / 1024:.1f} KB
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                if st.button("▶  Run Pipeline", use_container_width=True):
                    with st.spinner("Running pipeline..."):
                        try:
                            saved_path = save_uploaded_file(uploaded_file)
                            updated_df = run_pipeline(uploaded_path=saved_path)
                            st.session_state.df = updated_df

                            before = len(get_df())
                            st.success(
                                f"✅ Pipeline complete! Dataset now has **{len(updated_df)}** animals."
                            )

                            # Show preview
                            st.markdown('<div class="section-header">PREVIEW — PROCESSED DATA</div>',
                                        unsafe_allow_html=True)
                            show_cols = [c for c in ["Animal", "Diet", "Habitat",
                                                      "Conservation Status", "Size Category",
                                                      "Speed Category"] if c in updated_df.columns]
                            st.dataframe(updated_df[show_cols].head(20),
                                         use_container_width=True, hide_index=True)

                        except Exception as e:
                            st.error(f"❌ Pipeline failed: {e}")

    # Current dataset info
    df = get_df()
    if not df.empty:
        st.markdown('<div class="section-header">CURRENT MASTER DATASET</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Records", len(df))
        m2.metric("Columns", len(df.columns))
        m3.metric("Endangered", len(df[df["Conservation Status"].str.contains(
            "Endangered", na=False)]) if "Conservation Status" in df.columns else 0)
