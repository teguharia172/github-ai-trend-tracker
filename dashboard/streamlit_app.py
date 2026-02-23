#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Clean Editorial Dashboard
Design: Refined Minimalism with Editorial Typography
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

# CLEAN EDITORIAL DESIGN SYSTEM
st.markdown("""
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');
    
    * { 
        font-family: 'Source Sans 3', sans-serif;
    }
    
    /* === COLOR SYSTEM === */
    :root {
        --bg-primary: #fafafa;
        --bg-secondary: #ffffff;
        --bg-tertiary: #f5f5f5;
        --text-primary: #1a1a1a;
        --text-secondary: #525252;
        --text-muted: #737373;
        --accent-primary: #0d7377;
        --accent-secondary: #14919b;
        --accent-light: #e8f4f4;
        --border-light: #e5e5e5;
        --border-medium: #d4d4d4;
        --success: #16a34a;
        --warning: #ca8a04;
    }
    
    .main {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* === HEADER === */
    .header-container {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-light);
        padding: 3rem 0 2rem;
        margin-bottom: 2rem;
    }
    
    .header-pretitle {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--accent-primary);
        margin-bottom: 0.5rem;
    }
    
    .header-title {
        font-family: 'Crimson Pro', serif;
        font-size: 3rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.75rem;
    }
    
    .header-subtitle {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1.125rem;
        font-weight: 300;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* === METRICS === */
    .metric-container {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        padding: 1.5rem;
        height: 100%;
    }
    
    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'Crimson Pro', serif;
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        color: var(--success);
        font-weight: 500;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        display: flex;
        align-items: baseline;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-light);
    }
    
    .section-title {
        font-family: 'Crimson Pro', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .section-count {
        font-size: 0.875rem;
        color: var(--text-muted);
        font-weight: 400;
    }
    
    /* === REPO CARDS === */
    .repo-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .repo-item {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        padding: 1.25rem 1.5rem;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1rem;
        align-items: start;
        transition: all 0.15s ease;
    }
    
    .repo-item:hover {
        border-color: var(--border-medium);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .repo-main {
        min-width: 0;
    }
    
    .repo-name {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .repo-name a {
        color: var(--accent-primary);
        text-decoration: none;
    }
    
    .repo-name a:hover {
        text-decoration: underline;
    }
    
    .repo-desc {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.4;
        margin-bottom: 0.5rem;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .repo-meta {
        display: flex;
        gap: 1rem;
        align-items: center;
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    .repo-lang {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    
    .lang-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-primary);
    }
    
    .repo-stats {
        display: flex;
        gap: 1.5rem;
        align-items: center;
        font-size: 0.875rem;
    }
    
    .stat-item {
        text-align: right;
    }
    
    .stat-value {
        font-family: 'Crimson Pro', serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .velocity {
        color: var(--accent-primary);
        font-weight: 600;
    }
    
    /* === TABLES === */
    .data-table {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
    }
    
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-light);
    }
    
    div[data-testid="stDataFrame"] th {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        background: var(--bg-tertiary);
        border-bottom: 1px solid var(--border-medium);
        padding: 0.75rem 1rem;
    }
    
    div[data-testid="stDataFrame"] td {
        font-size: 0.9rem;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border-light);
        padding: 0.875rem 1rem;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid var(--border-light);
        gap: 0;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--text-muted);
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        padding: 1rem 1.5rem;
        transition: all 0.15s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: var(--bg-tertiary);
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-primary) !important;
        border-bottom-color: var(--accent-primary) !important;
        background: var(--accent-light) !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-light);
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
    }
    
    /* === FOOTER === */
    .footer {
        margin-top: 4rem;
        padding: 2rem 0;
        border-top: 1px solid var(--border-light);
        text-align: center;
    }
    
    .footer-text {
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    /* === UTILITY === */
    .text-muted { color: var(--text-muted); }
    .text-secondary { color: var(--text-secondary); }
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
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Filters")
        
        languages = sorted(repos['primary_language'].dropna().unique())
        lang_filter = st.multiselect("Language", options=languages, default=[])
        
        status_filter = st.multiselect(
            "Activity",
            options=["Very Active", "Active", "Moderate", "Stale"],
            default=["Very Active", "Active", "Moderate"]
        )
        
        min_stars = st.slider("Min Stars", 0, int(repos['stars_count'].max()), 0, 1000)
    
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
        <div class="header-pretitle">Analytics Dashboard</div>
        <div class="header-title">GitHub AI Trend Tracker</div>
        <div class="header-subtitle">Tracking {0:,} open source AI/ML repositories across {1} programming languages</div>
    </div>
    """.format(len(repos), repos['primary_language'].nunique()), unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Repositories</div>
            <div class="metric-value">{format_number(len(filtered))}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Stars</div>
            <div class="metric-value">{format_number(filtered['stars_count'].sum())}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Forks</div>
            <div class="metric-value">{format_number(filtered['forks_count'].sum())}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Languages</div>
            <div class="metric-value">{filtered['primary_language'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Trending", "Languages", "Browse All"])
    
    with tab1:
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Trending by Velocity</span>
            <span class="section-count">Top performers by stars per day</span>
        </div>
        """, unsafe_allow_html=True)
        
        for _, r in trending.head(15).iterrows():
            st.markdown(f"""
            <div class="repo-item">
                <div class="repo-main">
                    <div class="repo-name">
                        <a href="{r['html_url']}" target="_blank">{r['full_name']}</a>
                    </div>
                    <div class="repo-desc">{r.get('description', '') or 'No description'}</div>
                    <div class="repo-meta">
                        <span class="repo-lang"><span class="lang-dot"></span>{r['primary_language'] or 'Unknown'}</span>
                        <span>{r['activity_status']}</span>
                    </div>
                </div>
                <div class="repo-stats">
                    <div class="stat-item">
                        <div class="stat-value">{format_number(r['stars_count'])}</div>
                        <div class="stat-label">stars</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value velocity">+{r['stars_per_day']:.1f}</div>
                        <div class="stat-label">per day</div>
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
            st.bar_chart(chart_data[['total_stars', 'repo_count']], use_container_width=True, height=400)
        
        with col2:
            st.markdown("""
            <div class="section-header">
                <span class="section-title">Statistics</span>
            </div>
            """, unsafe_allow_html=True)
            
            for _, lang in lang_trends.head(8).iterrows():
                st.markdown(f"""
                <div style="padding: 0.75rem 0; border-bottom: 1px solid #e5e5e5;">
                    <div style="font-weight: 600; color: #1a1a1a; margin-bottom: 0.25rem;">
                        {lang['language']}
                    </div>
                    <div style="font-size: 0.85rem; color: #737373;">
                        {lang['repo_count']} repos · {format_number(lang['total_stars'])} stars
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"""
        <div class="section-header">
            <span class="section-title">All Repositories</span>
            <span class="section-count">{len(filtered):,} results</span>
        </div>
        """, unsafe_allow_html=True)
        
        display_df = filtered[['full_name', 'primary_language', 'stars_count', 'forks_count', 'open_issues_count', 'activity_status']].copy()
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
        <div class="footer-text">
            Last updated {datetime.now().strftime('%B %d, %Y at %H:%M UTC')} · 
            {len(repos):,} repositories tracked
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
