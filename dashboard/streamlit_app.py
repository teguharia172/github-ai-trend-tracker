#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Clean Evidence-Style Dashboard
"""

import html
import os
import sys
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
if os.path.exists(_env_path):
    from dotenv import load_dotenv

    load_dotenv(_env_path)

try:
    import duckdb
except ImportError:
    import subprocess

    # Pin to DuckDB 1.4.4 for MotherDuck compatibility
    subprocess.check_call([sys.executable, "-m", "pip", "install", "duckdb==1.4.4", "--quiet"])
    import duckdb

st.set_page_config(
    page_title="GitHub AI Trend Tracker",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# AGGRESSIVE RESET OF ALL STREAMLIT STYLES
st.markdown(
    """
<style>
    /* === FORCE WHITE BACKGROUND EVERYWHERE === */
    html, body, [class*="css"] {
        background-color: #ffffff !important;
    }
    
    .stApp {
        background-color: #ffffff !important;
    }
    
    .main {
        background-color: #ffffff !important;
    }
    
    .block-container {
        background-color: #ffffff !important;
        padding: 2rem 3rem !important;
        max-width: 1200px !important;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem !important;
        }

        .repo-card {
            flex-direction: column;
        }

        .repo-main {
            padding-right: 0 !important;
            margin-bottom: 0.75rem;
        }

        .repo-stats {
            text-align: left;
            min-width: unset;
        }
    }

    /* === HEADER === */
    .header-container {
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e5e5e5;
        background: #ffffff !important;
    }
    
    .header-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #666;
        margin-bottom: 0.5rem;
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
    }
    
    /* === METRICS - NO BLUE BACKGROUNDS === */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 0 !important;
        padding: 1.25rem !important;
    }
    
    div[data-testid="stMetric"] > div {
        background-color: transparent !important;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #888 !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetric"] .css-1xarl3l,
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #111 !important;
    }
    
    /* === REPO CARDS WITH DESCRIPTION === */
    .repo-card {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 1.25rem;
        border: 1px solid #e5e5e5;
        border-bottom: none;
        background: #ffffff;
    }
    
    .repo-card:last-child {
        border-bottom: 1px solid #e5e5e5;
    }
    
    .repo-card:hover {
        background: #fafafa;
    }
    
    .repo-main {
        flex: 1;
        min-width: 0;
        padding-right: 2rem;
    }
    
    .repo-title {
        font-size: 1rem;
        font-weight: 500;
        color: #2563eb;
        margin-bottom: 0.35rem;
    }
    
    .repo-title a {
        color: #2563eb;
        text-decoration: none;
    }
    
    .repo-title a:hover {
        text-decoration: underline;
    }
    
    .repo-desc {
        font-size: 0.9rem;
        color: #444;
        line-height: 1.5;
        margin-bottom: 0.5rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .repo-meta {
        font-size: 0.8rem;
        color: #888;
    }
    
    .repo-stats {
        text-align: right;
        min-width: 100px;
    }
    
    .repo-stat-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111;
    }
    
    .repo-stat-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .repo-velocity {
        color: #16a34a;
        font-weight: 600;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff !important;
        border-bottom: 1px solid #e5e5e5 !important;
        margin-bottom: 2rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #ffffff !important;
        color: #666 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #111 !important;
        border-bottom-color: #111 !important;
        background: #ffffff !important;
    }
    
    /* === TABLES === */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
    }

    div[data-testid="stDataFrame"] th {
        background: #fafafa !important;
        color: #333 !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        border-bottom: 1px solid #e5e5e5 !important;
    }

    div[data-testid="stDataFrame"] td {
        background: #ffffff !important;
        color: #222 !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }

    /* Force white background on dataframe container and grid cells */
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] iframe {
        background: #ffffff !important;
    }

    div[data-testid="stDataFrame"] [data-testid="glideDataEditor"],
    div[data-testid="stDataFrame"] [data-testid="glideDataEditor"] > div {
        background: #ffffff !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background-color: #fafafa !important;
        border-right: 1px solid #e5e5e5 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        background-color: transparent !important;
    }
    
    /* === CHARTS === */
    .stChart {
        background: #ffffff !important;
    }
    
    /* === SECTION HEADERS === */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    /* === FOOTER === */
    .footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e5e5;
        text-align: center;
        font-size: 0.8rem;
        color: #888;
        background: #ffffff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_connection():
    """Connect to MotherDuck database."""
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        raise ValueError("MOTHERDUCK_TOKEN not set")
    conn = duckdb.connect(f"md:?motherduck_token={token}")
    conn.execute("USE github_ai_analytics")
    return conn


@st.cache_data(ttl=300)
def load_data():
    """Load data from database."""
    conn = get_connection()

    repos = conn.execute(
        """
        SELECT * FROM prod_marts.dim_repositories
        ORDER BY stars_count DESC
    """
    ).fetchdf()

    lang_trends = conn.execute(
        """
        SELECT * FROM prod_marts.fct_language_trends
        ORDER BY total_stars DESC
    """
    ).fetchdf()

    return repos, lang_trends


@st.cache_data(ttl=300)
def load_trending(language_filter=None):
    """Load trending repos with optional language filter."""
    conn = get_connection()

    if language_filter:
        # Convert list to SQL IN clause
        placeholders = ", ".join([f"'{lang}'" for lang in language_filter])
        query = f"""
            SELECT * FROM prod_marts.fct_trending_repos
            WHERE primary_language IN ({placeholders})
            ORDER BY stars_per_day DESC
        """
    else:
        query = """
            SELECT * FROM prod_marts.fct_trending_repos
            ORDER BY stars_per_day DESC
        """

    trending = conn.execute(query).fetchdf()
    return trending


@st.cache_data(ttl=300)
def load_totals():
    """Load true totals from raw source (includes forks and archived)."""
    conn = get_connection()

    totals = conn.execute(
        """
        SELECT 
            COUNT(DISTINCT id) as total_repos,
            COALESCE(SUM(stargazers_count), 0) as total_stars,
            COALESCE(SUM(forks_count), 0) as total_forks,
            COUNT(DISTINCT language) as total_languages
        FROM github_raw.repositories
    """
    ).fetchdf()

    return totals.iloc[0]


def format_number(num):
    """Format number for display - use exact count for smaller numbers"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 10_000:
        return f"{num/1_000:.1f}K"
    elif num >= 1_000:
        # Show exact number with comma for thousands (e.g., "2,561")
        return f"{num:,}"
    return str(num)


def main():
    # Load data
    try:
        repos, lang_trends = load_data()
        totals = load_totals()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return

    # Sidebar filters
    with st.sidebar:
        st.markdown("#### Filters")

        languages = sorted(repos["primary_language"].dropna().unique())
        lang_filter = st.multiselect("Language", options=languages, default=[])

        status_opts = ["Very Active", "Active", "Moderate", "Stale"]
        status_filter = st.multiselect(
            "Activity",
            options=status_opts,
            default=["Very Active", "Active", "Moderate"],
        )

        min_stars = st.slider("Min Stars", 0, int(repos["stars_count"].max()), 0, 1000)

    # Load trending with language filter applied
    trending = load_trending(language_filter=lang_filter if lang_filter else None)
    trending_total = load_trending()  # Load unfiltered for count comparison

    # Apply filters
    filtered = repos.copy()
    if lang_filter:
        filtered = filtered[filtered["primary_language"].isin(lang_filter)]
    if status_filter:
        filtered = filtered[filtered["activity_status"].isin(status_filter)]
    filtered = filtered[filtered["stars_count"] >= min_stars]

    # Header
    st.markdown(
        f"""
    <div class="header-container">
        <div class="header-label">Analytics Dashboard</div>
        <div class="header-title">GitHub AI Trend Tracker</div>
        <div class="header-subtitle">
            Tracking {int(totals['total_repos']):,} open source AI/ML repositories across {int(totals['total_languages'])} languages
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Metrics - show TRUE TOTALS from raw source (includes forks, archived)
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("REPOSITORIES", format_number(int(totals["total_repos"])))
    m2.metric("TOTAL STARS", format_number(int(totals["total_stars"])))
    m3.metric("TOTAL FORKS", format_number(int(totals["total_forks"])))
    m4.metric("LANGUAGES", int(totals["total_languages"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Trending", "Languages", "Browse All"])

    with tab1:
        # Show filtered count if language filter is applied
        if lang_filter and len(trending) < len(trending_total):
            filter_info = f" ({len(trending)} of {len(trending_total)} repos — filtered by language)"
        else:
            filter_info = ""

        st.markdown(
            f'<div class="section-title">Trending by Velocity{filter_info}</div>',
            unsafe_allow_html=True,
        )

        for _, r in trending.head(15).iterrows():
            desc = r.get("description", "") or "No description available"
            # Truncate description if too long
            if len(desc) > 120:
                desc = desc[:117] + "..."

            # Use ACTUAL 1-day star growth if available, fallback to lifetime average
            stars_gained_1d = r.get("stars_gained_1d")
            if pd.notna(stars_gained_1d) and stars_gained_1d:
                daily_stars = stars_gained_1d
                velocity_label = "new stars today"
            else:
                daily_stars = r.get("stars_per_day", 0)
                velocity_label = "avg/day (lifetime)"

            # Escape all user-supplied strings to prevent XSS
            safe_desc = html.escape(desc)
            safe_full_name = html.escape(str(r["full_name"]))
            safe_html_url = html.escape(str(r["html_url"]))
            safe_language = html.escape(str(r["primary_language"] or "Unknown"))
            safe_activity = html.escape(str(r["activity_status"]))

            st.markdown(
                f"""
            <div class="repo-card">
                <div class="repo-main">
                    <div class="repo-title">
                        <a href="{safe_html_url}" target="_blank">{safe_full_name}</a>
                    </div>
                    <div class="repo-desc">{safe_desc}</div>
                    <div class="repo-meta">{safe_language} • {safe_activity}</div>
                </div>
                <div class="repo-stats">
                    <div class="repo-stat-value">{format_number(r['stars_count'])}</div>
                    <div class="repo-stat-label">stars</div>
                    <br><br>
                    <div class="repo-stat-value repo-velocity">+{daily_stars:.0f}</div>
                    <div class="repo-stat-label">{velocity_label}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with tab2:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                '<div class="section-title">Language Distribution</div>',
                unsafe_allow_html=True,
            )

            chart_data = lang_trends.head(10).sort_values("total_stars", ascending=True)

            fig = px.bar(
                chart_data,
                x="total_stars",
                y="language",
                orientation="h",
                labels={"total_stars": "Total Stars", "language": ""},
            )
            fig.update_traces(marker_color="#1e40af")
            fig.update_layout(
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="#333"),
                    title_font=dict(color="#333"),
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="#333"),
                    title_font=dict(color="#333"),
                ),
                font=dict(color="#333"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(
                '<div class="section-title">Top Languages</div>', unsafe_allow_html=True
            )

            for _, lang in lang_trends.head(10).iterrows():
                st.markdown(
                    f"""
                <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #f0f0f0;">
                    <span style="font-weight: 500; color: #111;">{lang['language']}</span>
                    <span style="color: #333; font-size: 0.9rem;">{lang['repo_count']} repos • {format_number(lang['total_stars'])} ★</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with tab3:
        st.markdown(
            f'<div class="section-title">All Repositories ({len(filtered):,})</div>',
            unsafe_allow_html=True,
        )

        display_df = filtered[
            [
                "full_name",
                "primary_language",
                "stars_count",
                "forks_count",
                "open_issues_count",
                "activity_status",
            ]
        ].copy()
        display_df.columns = [
            "Repository",
            "Language",
            "Stars",
            "Forks",
            "Issues",
            "Status",
        ]

        # Build HTML table for full theme control (st.dataframe ignores CSS)
        rows_html = ""
        for _, row in display_df.iterrows():
            stars = int(row["Stars"]) if pd.notna(row["Stars"]) else 0
            forks = int(row["Forks"]) if pd.notna(row["Forks"]) else 0
            issues = int(row["Issues"]) if pd.notna(row["Issues"]) else 0
            rows_html += (
                "<tr>"
                f"<td style='font-weight:500;'>{row['Repository']}</td>"
                f"<td>{row['Language'] or '—'}</td>"
                f"<td style='text-align:right;'>{stars:,}</td>"
                f"<td style='text-align:right;'>{forks:,}</td>"
                f"<td style='text-align:right;'>{issues:,}</td>"
                f"<td>{row['Status']}</td>"
                "</tr>"
            )

        st.markdown(
            f"""
            <div style="max-height:600px; overflow-y:auto; border:1px solid #e5e5e5;">
            <table style="width:100%; border-collapse:collapse; background:#ffffff;">
                <thead>
                    <tr style="position:sticky; top:0; background:#fafafa; border-bottom:2px solid #e5e5e5;">
                        <th style="text-align:left; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Repository</th>
                        <th style="text-align:left; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Language</th>
                        <th style="text-align:right; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Stars</th>
                        <th style="text-align:right; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Forks</th>
                        <th style="text-align:right; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Issues</th>
                        <th style="text-align:left; padding:0.75rem 1rem; color:#333; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Status</th>
                    </tr>
                </thead>
                <tbody style="color:#222; font-size:0.9rem;">
                    {rows_html}
                </tbody>
            </table>
            </div>
            <style>
                div.stMarkdown table tbody tr {{
                    border-bottom: 1px solid #f0f0f0;
                }}
                div.stMarkdown table tbody td {{
                    padding: 0.6rem 1rem;
                }}
                div.stMarkdown table tbody tr:hover {{
                    background: #fafafa;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Footer
    st.markdown(
        f"""
    <div class="footer">
        Last updated {datetime.now().strftime('%B %d, %Y at %H:%M UTC')} • {int(totals['total_repos']):,} repositories tracked
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
