#!/usr/bin/env python3
"""
GitHub AI Trend Tracker - Professional Static Dashboard
Generates beautiful HTML for GitHub Pages
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

try:
    import duckdb
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
except ImportError:
    os.system("pip install plotly pandas duckdb pyarrow --quiet")
    import duckdb
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd


def get_connection():
    """Connect to MotherDuck database."""
    token = os.getenv("MOTHERDUCK_TOKEN")
    if token:
        conn = duckdb.connect(f"md:?motherduck_token={token}")
    else:
        try:
            conn = duckdb.connect("md:")
        except:
            conn = duckdb.connect("../github_ai_trends.duckdb")
    conn.execute("USE github_ai_analytics")
    return conn


def load_data():
    """Load data from database."""
    conn = get_connection()

    repos = conn.execute(
        """
        SELECT 
            repo_id, full_name, html_url, description, primary_language,
            stars_count, forks_count, open_issues_count, created_at, updated_at,
            days_since_last_push, activity_status, popularity_tier, repo_age_days,
            owner, license_name, star_to_fork_ratio
        FROM prod_marts.dim_repositories
        ORDER BY stars_count DESC
    """
    ).fetchdf()

    lang_trends = conn.execute(
        """
        SELECT 
            language, repo_count, total_stars, avg_stars, avg_stars_per_day,
            pct_of_total_stars, total_forks, language_rank_by_stars
        FROM prod_marts.fct_language_trends
        ORDER BY total_stars DESC
    """
    ).fetchdf()

    trending = conn.execute(
        """
        SELECT 
            repo_id, full_name, primary_language, stars_count, stars_per_day,
            activity_status, ai_category, rank_by_velocity, html_url
        FROM prod_marts.fct_trending_repos
        ORDER BY stars_per_day DESC
    """
    ).fetchdf()

    return repos, lang_trends, trending


def create_dashboard():
    """Generate professional dark-themed HTML dashboard."""

    repos, lang_trends, trending = load_data()

    # Metrics
    total_repos = len(repos)
    total_stars = repos["stars_count"].sum()
    total_forks = repos["forks_count"].sum()
    total_langs = repos["primary_language"].nunique()

    # Chart 1: Top Languages
    fig1 = px.bar(
        lang_trends.head(10),
        x="language",
        y="total_stars",
        color="total_stars",
        color_continuous_scale="Plasma",
        template="plotly_dark",
        title="⭐ Top Languages by Total Stars",
    )
    fig1.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0)",
        font_color="#e2e8f0",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Chart 2: Pie Chart
    fig2 = px.pie(
        lang_trends.head(8),
        values="repo_count",
        names="language",
        hole=0.5,
        template="plotly_dark",
        title="🥧 Repository Distribution",
    )
    fig2.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0)",
        font_color="#e2e8f0",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, font=dict(color="#e2e8f0")
        ),
    )

    # Chart 3: Histogram
    fig3 = px.histogram(
        repos,
        x="stars_count",
        nbins=15,
        template="plotly_dark",
        color_discrete_sequence=["#6366f1"],
        title="📊 Stars Distribution",
    )
    fig3.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0)",
        font_color="#e2e8f0",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Chart 4: Activity
    activity_counts = repos["activity_status"].value_counts().reset_index()
    fig4 = px.bar(
        activity_counts,
        x="activity_status",
        y="count",
        color="count",
        color_continuous_scale="Viridis",
        template="plotly_dark",
        title="⚡ Activity Status",
    )
    fig4.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0)",
        font_color="#e2e8f0",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Generate table rows
    table_rows = ""
    for _, row in trending.head(15).iterrows():
        status_color = (
            "#22c55e"
            if row["activity_status"] == "Very Active"
            else "#eab308" if row["activity_status"] == "Active" else "#6b7280"
        )
        table_rows += f"""
        <tr>
            <td><a href="{row['html_url']}" target="_blank">{row['full_name']}</a></td>
            <td>{row['ai_category']}</td>
            <td><span class="lang-badge">{row['primary_language']}</span></td>
            <td class="text-end">{row['stars_count']:,}</td>
            <td class="text-end">{row['stars_per_day']:.1f}</td>
            <td><span class="status-badge" style="background: {status_color}20; color: {status_color}; border: 1px solid {status_color}40;">{row['activity_status']}</span></td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub AI Trend Tracker</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: #e2e8f0;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        /* Header */
        .header {{
            text-align: center;
            padding: 60px 0 40px;
            background: linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%);
        }}
        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
        }}
        .header p {{
            color: #94a3b8;
            font-size: 1.2rem;
        }}
        /* Metrics */
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15);
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 4px;
        }}
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        /* Charts */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }}
        .chart-card {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
        }}
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }}
        /* Table */
        .table-section {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
        }}
        .table-section h2 {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            text-align: left;
            padding: 14px 12px;
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }}
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
        }}
        tr:hover td {{
            background: rgba(99, 102, 241, 0.05);
        }}
        a {{
            color: #6366f1;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            color: #8b5cf6;
            text-decoration: underline;
        }}
        .text-end {{
            text-align: right;
        }}
        .lang-badge {{
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        /* Footer */
        .footer {{
            text-align: center;
            padding: 40px 0;
            color: #64748b;
            font-size: 0.9rem;
        }}
        .footer p {{
            margin-bottom: 8px;
        }}
        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            .metric-value {{
                font-size: 1.8rem;
            }}
            table {{
                font-size: 0.85rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🚀 GitHub AI Trend Tracker</h1>
            <p>Real-time analytics on AI open source projects from GitHub</p>
        </div>
    </div>
    
    <div class="container">
        <!-- Metrics -->
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{total_repos:,}</div>
                <div class="metric-label">Repositories</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_stars:,.0f}</div>
                <div class="metric-label">Total Stars</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_forks:,.0f}</div>
                <div class="metric-label">Total Forks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_langs}</div>
                <div class="metric-label">Languages</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">⭐ Top Languages by Total Stars</div>
                <div id="chart1"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">🥧 Repository Distribution</div>
                <div id="chart2"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📊 Stars Distribution</div>
                <div id="chart3"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">⚡ Activity Status</div>
                <div id="chart4"></div>
            </div>
        </div>
        
        <!-- Table -->
        <div class="table-section">
            <h2>🔥 Trending Repositories (by Stars/Day)</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Repository</th>
                            <th>Category</th>
                            <th>Language</th>
                            <th class="text-end">Stars</th>
                            <th class="text-end">Stars/Day</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <p>Data sourced from GitHub API via MotherDuck</p>
        </div>
    </div>
    
    <script>
        var chart1 = {fig1.to_json()};
        var chart2 = {fig2.to_json()};
        var chart3 = {fig3.to_json()};
        var chart4 = {fig4.to_json()};
        
        Plotly.newPlot('chart1', chart1.data, chart1.layout, {{responsive: true}});
        Plotly.newPlot('chart2', chart2.data, chart2.layout, {{responsive: true}});
        Plotly.newPlot('chart3', chart3.data, chart3.layout, {{responsive: true}});
        Plotly.newPlot('chart4', chart4.data, chart4.layout, {{responsive: true}});
    </script>
</body>
</html>"""

    return html


def main():
    print("🔌 Connecting to MotherDuck...")
    print("📊 Fetching data...")

    html = create_dashboard()

    os.makedirs("build", exist_ok=True)
    with open("build/index.html", "w") as f:
        f.write(html)

    print("✅ Professional dashboard built: build/index.html")


if __name__ == "__main__":
    main()
