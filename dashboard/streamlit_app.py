#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Evidence-Style Clean Dashboard
Design: Ultra-minimal, data-first aesthetic
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

st.set_page_config(
    page_title="GitHub AI Trend Tracker",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# MINIMAL DESIGN - Override ALL Streamlit defaults
st.markdown("""
<style>
    /* === RESET ALL STREAMLIT DEFAULTS === */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* === BASE === */
    .main {
        background: #ffffff;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* === HEADER === */
    .dashboard-header {
        margin-bottom: 3rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .header-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #666;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 600;
        color: #111;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #666;
        font-weight: 400;
    }
    
    /* === METRICS ROW === */
    .metrics-row {
        display: flex;
        gap: 2rem;
        margin-bottom: 3rem;
    }
    
    .metric-box {
        flex: 1;
    }
    
    .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #111;
        line-height: 1;
    }
    
    /* === SECTIONS === */
    .section {
        margin-bottom: 3rem;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111;
    }
    
    .section-subtitle {
        font-size: 0.85rem;
        color: #888;
    }
    
    /* === DATA TABLE / LIST === */
    .data-list {
        border: 1px solid #e5e5e5;
        background: #fff;
    }
    
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid #f0f0f0;
        transition: background 0.1s;
    }
    
    .data-row:last-child {
        border-bottom: none;
    }
    
    .data-row:hover {
        background: #fafafa;
    }
    
    .row-main {
        flex: 1;
        min-width: 0;
    }
    
    .row-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: #2563eb;
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .row-title a {
        color: #2563eb;
        text-decoration: none;
    }
    
    .row-title a:hover {
        text-decoration: underline;
    }
    
    .row-meta {
        font-size: 0.8rem;
        color: #888;
    }
    
    .row-stats {
        display: flex;
        gap: 2rem;
        text-align: right;
    }
    
    .stat-group {
        min-width: 80px;
    }
    
    .stat-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stat-highlight {
        color: #16a34a;
        font-weight: 600;
    }
    
    /* === LANGUAGE LIST === */
    .lang-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.875rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .lang-name {
        font-weight: 500;
        color: #111;
    }
    
    .lang-count {
        font-size: 0.85rem;
        color: #666;
    }
    
    /* === OVERRIDE STREAMLIT WIDGETS === */
    div[data-testid="stMetric"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    div[data-testid="stMetric"] > div {
        background: transparent !important;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #888 !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetric"] .css-1xarl3l {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #111 !important;
    }
    
    /* Tabs - minimal */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #e5e5e5;
        gap: 0;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem;
        font-weight: 500;
        color: #666;
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        padding: 0.75rem 1.25rem;
        margin: 0;
    }
    
    .stTabs [aria-selected="true"] {
        color: #111 !important;
        border-bottom-color: #111 !important;
        background: transparent !important;
    }
    
    /* DataFrame - clean */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e5e5e5;
    }
    
    div[data-testid="stDataFrame"] th {
        background: #fafafa;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #666;
        border-bottom: 1px solid #e5e5e5;
        padding: 0.75rem 1rem;
    }
    
    div[data-testid="stDataFrame"] td {
        font-size: 0.9rem;
        color: #444;
        border-bottom: 1px solid #f0f0f0;
        padding: 0.75rem 1rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #fafafa;
        border-right: 1px solid #e5e5e5;
    }
    
    /* Footer */
    .footer {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e5e5;
        text-align: center;
        font-size: 0.8rem;
        color: #888;
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
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def main():
    # Load data
    try:
        repos, lang_trends, trending = load_data()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("#### Filters")
        
        languages = sorted(repos['primary_language'].dropna().unique())
        lang_filter = st.multiselect("Language", options=languages, default=[])
        
        status_opts = ["Very Active", "Active", "Moderate", "Stale"]
        status_filter = st.multiselect("Activity", options=status_opts, default=["Very Active", "Active"])
        
        min_stars = st.slider("Min Stars", 0, int(repos['stars_count'].max()), 0, 1000)
    
    # Apply filters
    filtered = repos.copy()
    if lang_filter:
        filtered = filtered[filtered['primary_language'].isin(lang_filter)]
    if status_filter:
        filtered = filtered[filtered['activity_status'].isin(status_filter)]
    filtered = filtered[filtered['stars_count'] >= min_stars]
    
    # Header
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-label">Analytics Dashboard</div>
        <div class="header-title">GitHub AI Trend Tracker</div>
        <div class="header-subtitle">
            Tracking {len(repos):,} open source AI/ML repositories across {repos['primary_language'].nunique()} languages
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics - using columns but styled cleanly
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Repositories", format_number(len(filtered)))
    m2.metric("Total Stars", format_number(filtered['stars_count'].sum()))
    m3.metric("Total Forks", format_number(filtered['forks_count'].sum()))
    m4.metric("Languages", filtered['primary_language'].nunique())
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Trending", "Languages", "Browse"])
    
    with tab1:
        st.markdown("""
        <div class="section">
            <div class="section-header">
                <span class="section-title">Trending by Velocity</span>
                <span class="section-subtitle">Top performers by stars per day</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for _, r in trending.head(20).iterrows():
            st.markdown(f"""
            <div class="data-row">
                <div class="row-main">
                    <div class="row-title">
                        <a href="{r['html_url']}" target="_blank">{r['full_name']}</a>
                    </div>
                    <div class="row-meta">
                        {r['primary_language'] or 'Unknown'} • {r['activity_status']}
                    </div>
                </div>
                <div class="row-stats">
                    <div class="stat-group">
                        <div class="stat-value">{format_number(r['stars_count'])}</div>
                        <div class="stat-label">Stars</div>
                    </div>
                    <div class="stat-group">
                        <div class="stat-value stat-highlight">+{r['stars_per_day']:.1f}</div>
                        <div class="stat-label">/day</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="section-header">
                <span class="section-title">Language Distribution</span>
            </div>
            """, unsafe_allow_html=True)
            
            chart_data = lang_trends.head(10).set_index('language')
            st.bar_chart(
                chart_data[['total_stars']], 
                use_container_width=True,
                height=350
            )
        
        with col2:
            st.markdown("""
            <div class="section-header">
                <span class="section-title">Top Languages</span>
            </div>
            <div class="data-list">
            """, unsafe_allow_html=True)
            
            for _, lang in lang_trends.head(10).iterrows():
                st.markdown(f"""
                <div class="lang-item">
                    <span class="lang-name">{lang['language']}</span>
                    <span class="lang-count">{lang['repo_count']} repos</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"""
        <div class="section-header">
            <span class="section-title">All Repositories</span>
            <span class="section-subtitle">{len(filtered):,} results</span>
        </div>
        """, unsafe_allow_html=True)
        
        display_df = filtered[[
            'full_name', 'primary_language', 'stars_count', 
            'forks_count', 'open_issues_count', 'activity_status'
        ]].copy()
        display_df.columns = ['Repository', 'Language', 'Stars', 'Forks', 'Issues', 'Status']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Repository": st.column_config.TextColumn(width="large"),
                "Language": st.column_config.TextColumn(width="small"),
                "Stars": st.column_config.NumberColumn(format="%d", width="small"),
                "Forks": st.column_config.NumberColumn(format="%d", width="small"),
                "Issues": st.column_config.NumberColumn(format="%d", width="small"),
            }
        )
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        Last updated {datetime.now().strftime('%B %d, %Y at %H:%M UTC')} • 
        {len(repos):,} repositories tracked
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
