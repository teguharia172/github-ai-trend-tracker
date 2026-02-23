#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Professional Streamlit Dashboard
Design: Retro-Futuristic / Cyber-Industrial
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime

try:
    import duckdb
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "duckdb", "--quiet"])
    import duckdb

# Page configuration
st.set_page_config(
    page_title="GitHub AI Trend Tracker",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# PROFESSIONAL DESIGN SYSTEM
# Aesthetic: Retro-Futuristic / Cyber-Industrial
st.markdown("""
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * { 
        font-family: 'Outfit', sans-serif;
    }
    
    /* === COLOR SYSTEM === */
    :root {
        --bg-primary: #0a0b0f;
        --bg-secondary: #111318;
        --bg-tertiary: #1a1d24;
        --accent-cyan: #00d9ff;
        --accent-electric: #00b4d8;
        --accent-hot: #ff3864;
        --text-primary: #f0f4f8;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-subtle: rgba(0, 217, 255, 0.1);
        --border-glow: rgba(0, 217, 255, 0.3);
    }
    
    /* === BASE STYLES === */
    .main {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* === HEADER === */
    .header-container {
        background: linear-gradient(180deg, rgba(0, 217, 255, 0.03) 0%, transparent 100%);
        border-bottom: 1px solid var(--border-subtle);
        padding: 3rem 0 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
        animation: scanline 4s linear infinite;
    }
    
    @keyframes scanline {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-cyan) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    
    /* === METRIC CARDS === */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 3rem;
    }
    
    div[data-testid="stMetric"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent-cyan);
        border-radius: 0;
        padding: 1.5rem;
        position: relative;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: var(--border-glow);
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.1);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, var(--accent-cyan), transparent);
        opacity: 0.5;
    }
    
    div[data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }
    
    div[data-testid="stMetric"] .css-1xarl3l {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 300 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }
    
    /* === SECTION HEADERS === */
    h2 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        position: relative;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 1px;
        background: var(--accent-cyan);
    }
    
    h3 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--text-secondary) !important;
        margin-bottom: 1rem;
    }
    
    /* === REPO CARDS === */
    .repo-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        position: relative;
        transition: all 0.2s ease;
    }
    
    .repo-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background: var(--accent-cyan);
        opacity: 0;
        transition: opacity 0.2s;
    }
    
    .repo-card:hover {
        background: var(--bg-tertiary);
        border-color: var(--border-glow);
        transform: translateX(4px);
    }
    
    .repo-card:hover::before {
        opacity: 1;
    }
    
    .repo-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: var(--accent-cyan);
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    .repo-name a {
        color: var(--accent-cyan);
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .repo-name a:hover {
        color: var(--text-primary);
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    .repo-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }
    
    .repo-meta {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .repo-stat {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    .repo-stat strong {
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .lang-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        background: rgba(0, 217, 255, 0.1);
        color: var(--accent-cyan);
        padding: 0.25rem 0.75rem;
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 0;
    }
    
    .velocity-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        background: rgba(255, 56, 100, 0.1);
        color: var(--accent-hot);
        padding: 0.25rem 0.75rem;
        border: 1px solid rgba(255, 56, 100, 0.2);
    }
    
    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.2rem 0.5rem;
    }
    
    .status-active {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-moderate {
        background: rgba(234, 179, 8, 0.1);
        color: #eab308;
        border: 1px solid rgba(234, 179, 8, 0.3);
    }
    
    .status-stale {
        background: rgba(100, 116, 139, 0.1);
        color: #64748b;
        border: 1px solid rgba(100, 116, 139, 0.3);
    }
    
    /* === DATA TABLE === */
    div[data-testid="stDataFrame"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 0;
    }
    
    div[data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border-subtle);
    }
    
    div[data-testid="stDataFrame"] th {
        font-family: 'Outfit', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        background: var(--bg-tertiary);
        border-bottom: 1px solid var(--border-glow);
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid var(--border-subtle);
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        padding: 1rem 1.5rem;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: rgba(0, 217, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-cyan) !important;
        border-bottom-color: var(--accent-cyan) !important;
        background: rgba(0, 217, 255, 0.08) !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: 1px solid var(--accent-cyan);
        color: var(--accent-cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-radius: 0;
        transition: all 0.2s;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--accent-cyan);
        color: var(--bg-primary);
    }
    
    /* === FOOTER === */
    .footer {
        text-align: center;
        padding: 3rem 0;
        margin-top: 3rem;
        border-top: 1px solid var(--border-subtle);
    }
    
    .footer-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-muted);
        letter-spacing: 0.1em;
    }
    
    /* === GLOW EFFECTS === */
    .glow-text {
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
    }
    
    /* === ANIMATED ELEMENTS === */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .header-title {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_connection():
    """Connect to MotherDuck database."""
    token = os.getenv('MOTHERDUCK_TOKEN')
    if not token:
        raise ValueError("MOTHERDUCK_TOKEN not set")
    conn = duckdb.connect(f"md:?motherduck_token={token}")
    conn.execute("USE github_ai_analytics")
    return conn


@st.cache_data(ttl=300)
def load_data():
    """Load data from database."""
    conn = get_connection()
    
    repos = conn.execute("""
        SELECT * FROM prod_marts.dim_repositories
        ORDER BY stars_count DESC
    """).fetchdf()
    
    lang_trends = conn.execute("""
        SELECT * FROM prod_marts.fct_language_trends
        ORDER BY total_stars DESC
    """).fetchdf()
    
    trending = conn.execute("""
        SELECT * FROM prod_marts.fct_trending_repos
        ORDER BY stars_per_day DESC
    """).fetchdf()
    
    return repos, lang_trends, trending


def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def get_status_class(status):
    if status == 'Very Active':
        return 'status-active'
    elif status == 'Active':
        return 'status-moderate'
    return 'status-stale'


def main():
    # Sidebar filters
    with st.sidebar:
        st.title("◉ CONTROL")
        st.markdown("---")
        
        # Load data for filters
        try:
            repos, lang_trends, trending = load_data()
            languages = sorted(repos['primary_language'].dropna().unique())
            
            lang_filter = st.multiselect(
                "LANGUAGE",
                options=languages,
                default=[],
                format_func=lambda x: x.upper()
            )
            
            status_filter = st.multiselect(
                "ACTIVITY",
                options=["Very Active", "Active", "Moderate", "Stale"],
                default=["Very Active", "Active", "Moderate"]
            )
            
            min_stars = st.slider(
                "MIN STARS",
                min_value=0,
                max_value=int(repos['stars_count'].max()),
                value=0,
                step=1000,
                format="%d ★"
            )
        except:
            st.error("Connection failed")
            return
    
    # Apply filters
    filtered = repos.copy()
    if lang_filter:
        filtered = filtered[filtered['primary_language'].isin(lang_filter)]
    if status_filter:
        filtered = filtered[filtered['activity_status'].isin(status_filter)]
    filtered = filtered[filtered['stars_count'] >= min_stars]
    
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="header-title">GitHub AI Trend Tracker</div>
        <div class="header-subtitle">Real-time Analytics // Open Source Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("REPOSITORIES", f"{len(filtered):,}")
    with c2:
        st.metric("TOTAL STARS", format_number(filtered['stars_count'].sum()))
    with c3:
        st.metric("TOTAL FORKS", format_number(filtered['forks_count'].sum()))
    with c4:
        st.metric("LANGUAGES", filtered['primary_language'].nunique())
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["◉ TRENDING", "◉ ANALYTICS", "◉ DATABASE"])
    
    with tab1:
        st.markdown("<h2>Velocity Leaders</h2>", unsafe_allow_html=True)
        
        for _, r in trending.head(12).iterrows():
            status_class = get_status_class(r['activity_status'])
            
            st.markdown(f"""
            <div class="repo-card">
                <div class="repo-name">
                    <a href="{r['html_url']}" target="_blank">{r['full_name']}</a>
                </div>
                <div class="repo-desc">{r.get('description', 'No description available') or 'No description available'}</div>
                <div class="repo-meta">
                    <span class="lang-badge">{r['primary_language'] or 'N/A'}</span>
                    <span class="repo-stat"><strong>{format_number(r['stars_count'])}</strong> ★</span>
                    <span class="velocity-badge">+{r['stars_per_day']:.1f}/day</span>
                    <span class="status-badge {status_class}">{r['activity_status'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3>Language Dominance</h3>", unsafe_allow_html=True)
            chart_data = lang_trends.head(8).set_index('language')['total_stars']
            st.bar_chart(chart_data, use_container_width=True, height=300)
        
        with col2:
            st.markdown("<h3>Repository Distribution</h3>", unsafe_allow_html=True)
            chart_data = lang_trends.head(8).set_index('language')['repo_count']
            st.bar_chart(chart_data, use_container_width=True, height=300)
        
        st.markdown("<h3>Language Statistics</h3>", unsafe_allow_html=True)
        display_cols = ['language', 'repo_count', 'total_stars', 'avg_stars', 'avg_stars_per_day']
        st.dataframe(
            lang_trends[display_cols].head(12),
            use_container_width=True,
            hide_index=True,
            column_config={
                "language": st.column_config.TextColumn("LANGUAGE"),
                "repo_count": st.column_config.NumberColumn("REPOS", format="%d"),
                "total_stars": st.column_config.NumberColumn("STARS", format="%d"),
                "avg_stars": st.column_config.NumberColumn("AVG", format="%.0f"),
                "avg_stars_per_day": st.column_config.NumberColumn("VEL/DAY", format="%.1f")
            }
        )
    
    with tab3:
        st.markdown(f"<h2>Repository Database ({len(filtered)} records)</h2>", unsafe_allow_html=True)
        
        display_df = filtered[['full_name', 'primary_language', 'stars_count', 'forks_count', 'activity_status']].copy()
        display_df.columns = ['REPOSITORY', 'LANG', 'STARS', 'FORKS', 'STATUS']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "REPOSITORY": st.column_config.TextColumn(width="large"),
                "LANG": st.column_config.TextColumn(width="small"),
                "STARS": st.column_config.NumberColumn(format="%d ★"),
                "FORKS": st.column_config.NumberColumn(format="%d"),
            }
        )
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        <div class="footer-text">
            LAST SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} // 
            DATA SOURCE: GitHub API via MotherDuck // 
            {len(repos):,} REPOSITORIES TRACKED
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
