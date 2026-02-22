#!/usr/bin/env python3
"""
GitHub AI Trend Tracker Dashboard
A simple Plotly Dash dashboard deployed to GitHub Pages as static HTML.
"""

import os
import sys
import json
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import duckdb
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
except ImportError:
    print("Installing dependencies...")
    os.system("pip install plotly pandas duckdb pyarrow --quiet")
    import duckdb
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd


def get_connection():
    """Connect to MotherDuck database."""
    token = os.getenv('MOTHERDUCK_TOKEN')
    if token:
        conn = duckdb.connect(f"md:?motherduck_token={token}")
    else:
        # Try local token
        try:
            conn = duckdb.connect("md:")
        except:
            conn = duckdb.connect("../github_ai_trends.duckdb")
    conn.execute("USE github_ai_analytics")
    return conn


def fetch_data(conn):
    """Fetch data from MotherDuck."""
    # Repositories data
    repos = conn.execute("""
        SELECT 
            repo_id,
            full_name,
            html_url,
            description,
            primary_language,
            stars_count,
            forks_count,
            open_issues_count,
            created_at,
            updated_at,
            pushed_at,
            days_since_last_push,
            activity_status,
            popularity_tier,
            repo_age_days
        FROM prod_marts.dim_repositories
        ORDER BY stars_count DESC
    """).fetchdf()
    
    # Language trends
    lang_trends = conn.execute("""
        SELECT 
            language,
            repo_count,
            total_stars,
            avg_stars,
            avg_stars_per_day,
            pct_of_total_stars
        FROM prod_marts.fct_language_trends
        ORDER BY total_stars DESC
    """).fetchdf()
    
    # Trending repos
    trending = conn.execute("""
        SELECT 
            repo_id,
            full_name,
            primary_language,
            stars_count,
            stars_per_day,
            activity_status,
            days_since_last_push,
            repo_age_days,
            ai_category
        FROM prod_marts.fct_trending_repos
        ORDER BY stars_per_day DESC
    """).fetchdf()
    
    return repos, lang_trends, trending


def create_dashboard_html(repos, lang_trends, trending):
    """Generate static HTML dashboard."""
    
    # Key metrics
    total_repos = len(repos)
    total_stars = repos['stars_count'].sum()
    total_forks = repos['forks_count'].sum()
    total_languages = repos['primary_language'].nunique()
    
    # Top languages chart
    lang_chart = px.bar(
        lang_trends.head(10),
        x='language',
        y='total_stars',
        title='Top Languages by Total Stars',
        color='total_stars',
        color_continuous_scale='viridis',
        template='plotly_white'
    )
    lang_chart.update_layout(height=400, showlegend=False)
    
    # Repo count by language
    lang_count_chart = px.pie(
        lang_trends.head(8),
        values='repo_count',
        names='language',
        title='Repository Count by Language',
        template='plotly_white'
    )
    lang_count_chart.update_layout(height=400)
    
    # Stars distribution
    stars_dist = px.histogram(
        repos,
        x='stars_count',
        nbins=20,
        title='Stars Distribution',
        template='plotly_white',
        color_discrete_sequence=['#636EFA']
    )
    stars_dist.update_layout(height=350)
    
    # Activity status
    activity_counts = repos['activity_status'].value_counts().reset_index()
    activity_chart = px.bar(
        activity_counts,
        x='activity_status',
        y='count',
        title='Repositories by Activity Status',
        template='plotly_white',
        color='count',
        color_continuous_scale='RdYlGn'
    )
    activity_chart.update_layout(height=350, showlegend=False)
    
    # Trending repos table data
    top_trending = trending.head(10)[['full_name', 'primary_language', 'stars_count', 'stars_per_day', 'ai_category']]
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub AI Trend Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; }}
        .metric-card {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-value {{ font-size: 2.5rem; font-weight: bold; }}
        .metric-label {{ font-size: 0.9rem; opacity: 0.9; }}
        .chart-container {{ 
            background: white; 
            border-radius: 15px; 
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }}
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        .last-updated {{
            text-align: center;
            color: #6c757d;
            margin-top: 2rem;
            padding: 1rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1 class="display-4">🚀 GitHub AI Trend Tracker</h1>
            <p class="lead">Real-time analytics on AI open source projects from GitHub</p>
        </div>
    </div>
    
    <div class="container">
        <!-- Key Metrics -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{total_repos:,}</div>
                    <div class="metric-label">Repositories</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{total_stars:,.0f}</div>
                    <div class="metric-label">Total Stars</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{total_forks:,.0f}</div>
                    <div class="metric-label">Total Forks</div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{total_languages}</div>
                    <div class="metric-label">Languages</div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row 1 -->
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    {lang_chart.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    {lang_count_chart.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
        </div>
        
        <!-- Charts Row 2 -->
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    {stars_dist.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    {activity_chart.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
        </div>
        
        <!-- Top Trending Repositories -->
        <div class="row">
            <div class="col-12">
                <div class="table-container">
                    <h3 class="mb-3">🔥 Top Trending Repositories (by Stars/Day)</h3>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Repository</th>
                                    <th>Category</th>
                                    <th>Language</th>
                                    <th class="text-end">Stars</th>
                                    <th class="text-end">Stars/Day</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(f"<tr><td><a href='https://github.com/{row['full_name']}' target='_blank'>{row['full_name']}</a></td><td>{row['ai_category']}</td><td>{row['primary_language']}</td><td class='text-end'>{row['stars_count']:,}</td><td class='text-end'>{row['stars_per_day']:.1f}</td></tr>" for _, row in top_trending.iterrows())}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="last-updated">
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    return html_content


def main():
    """Build dashboard."""
    print("🔌 Connecting to MotherDuck...")
    conn = get_connection()
    
    print("📊 Fetching data...")
    repos, lang_trends, trending = fetch_data(conn)
    
    print(f"✅ Loaded {len(repos)} repositories, {len(lang_trends)} languages")
    
    print("🎨 Generating dashboard...")
    html = create_dashboard_html(repos, lang_trends, trending)
    
    # Ensure build directory exists
    os.makedirs('build', exist_ok=True)
    
    # Write HTML
    with open('build/index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard built: build/index.html")


if __name__ == '__main__':
    main()
