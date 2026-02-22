#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Professional Streamlit Dashboard
Similar to https://demo-movies.streamlit.app/
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
    os.system("pip install duckdb pyarrow --quiet")
    import duckdb

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="GitHub AI Trend Tracker",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #e2e8f0;
    }
    
    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] .css-1xarl3l {
        color: #f8fafc !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    h2, h3 {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    
    /* Cards */
    .repo-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .repo-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.15);
    }
    
    .repo-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6366f1;
        margin-bottom: 8px;
    }
    
    .repo-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    
    .repo-meta {
        display: flex;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .repo-stat {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #e2e8f0;
        font-size: 0.85rem;
    }
    
    .lang-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-active {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
    }
    
    .status-moderate {
        background: rgba(234, 179, 8, 0.15);
        color: #eab308;
    }
    
    .status-inactive {
        background: rgba(107, 114, 128, 0.15);
        color: #9ca3af;
    }
    
    /* DataFrame */
    div[data-testid="stDataFrame"] {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Selectbox and sliders */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stSlider"] > div {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 8px;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.3) !important;
        color: #f8fafc !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0;
        color: #64748b;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_connection():
    """Connect to MotherDuck database."""
    token = os.getenv('MOTHERDUCK_TOKEN')
    if token:
        conn = duckdb.connect(f"md:?motherduck_token={token}")
    else:
        try:
            conn = duckdb.connect("md:")
        except:
            conn = duckdb.connect("../github_ai_trends.duckdb")
    conn.execute("USE github_ai_analytics")
    return conn


@st.cache_data(ttl=300)
def load_data():
    """Load data from database."""
    conn = get_connection()
    
    repos = conn.execute("""
        SELECT 
            repo_id, full_name, html_url, description, primary_language,
            stars_count, forks_count, open_issues_count, created_at, updated_at,
            days_since_last_push, activity_status, popularity_tier, repo_age_days,
            owner, license_name, star_to_fork_ratio, search_query
        FROM prod_marts.dim_repositories
        ORDER BY stars_count DESC
    """).fetchdf()
    
    lang_trends = conn.execute("""
        SELECT 
            language, repo_count, total_stars, avg_stars, avg_stars_per_day,
            pct_of_total_stars, total_forks, language_rank_by_stars
        FROM prod_marts.fct_language_trends
        ORDER BY total_stars DESC
    """).fetchdf()
    
    trending = conn.execute("""
        SELECT 
            repo_id, full_name, primary_language, stars_count, stars_per_day,
            activity_status, ai_category, rank_by_velocity, html_url, description
        FROM prod_marts.fct_trending_repos
        ORDER BY stars_per_day DESC
    """).fetchdf()
    
    return repos, lang_trends, trending


def format_number(num):
    """Format large numbers."""
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
        
        st.markdown("### Filters")
        
        # These will be populated after data load
        lang_filter = st.multiselect(
            "Language",
            options=[],
            default=[],
            help="Filter by programming language"
        )
        
        status_filter = st.multiselect(
            "Activity Status",
            options=["Very Active", "Active", "Moderate", "Stale"],
            default=["Very Active", "Active", "Moderate"],
            help="Filter by repository activity"
        )
        
        min_stars = st.slider(
            "Minimum Stars",
            min_value=0,
            max_value=100000,
            value=0,
            step=1000,
            help="Minimum star count"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        Tracking AI/ML open source repositories from GitHub.
        
        Data is updated daily via automated pipeline.
        """)
        
        st.markdown("---")
        st.markdown(f"**Last Updated:**  
{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Main content
    st.title("GitHub AI Trend Tracker")
    st.markdown("Real-time analytics on AI open source projects")
    
    # Load data
    try:
        repos, lang_trends, trending = load_data()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.info("Please ensure the data pipeline has run and MotherDuck token is configured.")
        return
    
    # Update sidebar filters with actual data
    languages = sorted(repos['primary_language'].dropna().unique())
    
    # Re-render sidebar with actual languages (hack to update options)
    with st.sidebar:
        st.markdown("### Filters")
        lang_filter = st.multiselect(
            "Language",
            options=languages,
            default=[],
            key="lang_filter_final"
        )
    
    # Apply filters
    filtered_repos = repos.copy()
    if lang_filter:
        filtered_repos = filtered_repos[filtered_repos['primary_language'].isin(lang_filter)]
    if status_filter:
        filtered_repos = filtered_repos[filtered_repos['activity_status'].isin(status_filter)]
    filtered_repos = filtered_repos[filtered_repos['stars_count'] >= min_stars]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Repositories", f"{len(filtered_repos):,}")
    with col2:
        st.metric("Total Stars", format_number(filtered_repos['stars_count'].sum()))
    with col3:
        st.metric("Total Forks", format_number(filtered_repos['forks_count'].sum()))
    with col4:
        st.metric("Languages", filtered_repos['primary_language'].nunique())
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔥 Trending", "📊 Analytics", "📋 All Repositories"])
    
    with tab1:
        st.subheader("Top Trending by Velocity")
        
        for _, repo in trending.head(10).iterrows():
            status_class = "status-active" if repo['activity_status'] == 'Very Active' else \
                          "status-moderate" if repo['activity_status'] == 'Active' else "status-inactive"
            
            st.markdown(f"""
            <div class="repo-card">
                <div class="repo-name">{repo['full_name']}</div>
                <div class="repo-desc">{repo.get('description', 'No description') or 'No description'}</div>
                <div class="repo-meta">
                    <span class="lang-badge">{repo['primary_language'] or 'Unknown'}</span>
                    <span class="repo-stat">⭐ {format_number(repo['stars_count'])}</span>
                    <span class="repo-stat">📈 {repo['stars_per_day']:.1f}/day</span>
                    <span class="status-badge {status_class}">{repo['activity_status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Languages by Stars")
            chart_data = lang_trends.head(10)
            st.bar_chart(
                data=chart_data.set_index('language')['total_stars'],
                use_container_width=True
            )
        
        with col2:
            st.subheader("Repository Count by Language")
            st.bar_chart(
                data=lang_trends.head(10).set_index('language')['repo_count'],
                use_container_width=True
            )
        
        st.subheader("Language Statistics")
        st.dataframe(
            lang_trends[['language', 'repo_count', 'total_stars', 'avg_stars', 'avg_stars_per_day']].head(15),
            use_container_width=True,
            hide_index=True
        )
    
    with tab3:
        st.subheader(f"All Repositories ({len(filtered_repos)})")
        
        display_df = filtered_repos[['full_name', 'primary_language', 'stars_count', 
                                      'forks_count', 'activity_status', 'popularity_tier']].copy()
        display_df.columns = ['Repository', 'Language', 'Stars', 'Forks', 'Status', 'Tier']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Repository": st.column_config.TextColumn(width="large"),
                "Language": st.column_config.TextColumn(width="small"),
                "Stars": st.column_config.NumberColumn(format="%d"),
                "Forks": st.column_config.NumberColumn(format="%d"),
            }
        )
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Made with ❤️ using Streamlit | Data from GitHub API via MotherDuck</p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
