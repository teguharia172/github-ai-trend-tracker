#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Streamlit Dashboard
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime

# Check and import duckdb
try:
    import duckdb
except ImportError:
    st.error("DuckDB not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "duckdb", "--quiet"])
    import duckdb

# Page configuration
st.set_page_config(
    page_title="GitHub AI Trend Tracker",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    div[data-testid="stMetric"] .css-1xarl3l {
        color: #f8fafc !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    h2, h3 { color: #f8fafc !important; font-weight: 600 !important; }
    
    .repo-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .repo-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6366f1;
        margin-bottom: 4px;
    }
    
    .repo-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    
    .repo-meta {
        display: flex;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .lang-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
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


def main():
    # Sidebar
    with st.sidebar:
        st.title("🚀 GitHub AI")
        st.markdown("---")
        st.markdown("### About")
        st.markdown("Tracking AI/ML open source repositories from GitHub.")
        st.markdown("---")
    
    # Main content
    st.title("GitHub AI Trend Tracker")
    st.markdown("Real-time analytics on AI open source projects")
    
    # Load data
    try:
        repos, lang_trends, trending = load_data()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.info("Please check MOTHERDUCK_TOKEN is set in Streamlit Cloud secrets.")
        return
    
    # Update sidebar
    with st.sidebar:
        languages = sorted(repos['primary_language'].dropna().unique())
        lang_filter = st.multiselect("Language", options=languages, default=[])
        
        status_filter = st.multiselect(
            "Status",
            options=["Very Active", "Active", "Moderate", "Stale"],
            default=["Very Active", "Active", "Moderate"]
        )
        
        min_stars = st.slider("Min Stars", 0, 100000, 0, 1000)
    
    # Apply filters
    filtered = repos.copy()
    if lang_filter:
        filtered = filtered[filtered['primary_language'].isin(lang_filter)]
    if status_filter:
        filtered = filtered[filtered['activity_status'].isin(status_filter)]
    filtered = filtered[filtered['stars_count'] >= min_stars]
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Repositories", f"{len(filtered):,}")
    c2.metric("Stars", format_number(filtered['stars_count'].sum()))
    c3.metric("Forks", format_number(filtered['forks_count'].sum()))
    c4.metric("Languages", filtered['primary_language'].nunique())
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔥 Trending", "📊 Analytics", "📋 All Repos"])
    
    with tab1:
        st.subheader("Top Trending by Stars/Day")
        for _, r in trending.head(10).iterrows():
            st.markdown(f"""
            <div class="repo-card">
                <div class="repo-name">{r['full_name']}</div>
                <div class="repo-desc">{r.get('description', '') or 'No description'}</div>
                <div class="repo-meta">
                    <span class="lang-badge">{r['primary_language'] or 'N/A'}</span>
                    <span>⭐ {format_number(r['stars_count'])}</span>
                    <span>📈 {r['stars_per_day']:.1f}/day</span>
                    <span>{r['activity_status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Top Languages by Stars")
            st.bar_chart(lang_trends.head(10).set_index('language')['total_stars'])
        with c2:
            st.subheader("Repo Count by Language")
            st.bar_chart(lang_trends.head(10).set_index('language')['repo_count'])
        
        st.subheader("Language Stats")
        st.dataframe(lang_trends[['language', 'repo_count', 'total_stars', 'avg_stars']].head(15), 
                     use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader(f"All Repositories ({len(filtered)})")
        display = filtered[['full_name', 'primary_language', 'stars_count', 'forks_count', 'activity_status']]
        display.columns = ['Repository', 'Language', 'Stars', 'Forks', 'Status']
        st.dataframe(display, use_container_width=True, hide_index=True)
    
    st.markdown(f"<p style='text-align:center;color:#64748b'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>", 
                unsafe_allow_html=True)


if __name__ == '__main__':
    main()
