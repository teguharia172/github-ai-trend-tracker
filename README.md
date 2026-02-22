# 🚀 GitHub AI Trend Tracker

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.10-orange.svg)](https://getdbt.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B.svg)](https://streamlit.io)
[![MotherDuck](https://img.shields.io/badge/MotherDuck-🦆-yellow.svg)](https://motherduck.com)

A complete data pipeline that tracks AI/ML open source trends from GitHub, transforms the data with dbt, and visualizes it in a beautiful Streamlit dashboard.

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ GitHub API  │────▶│  dlt (load)  │────▶│  MotherDuck │────▶│  Streamlit   │
│             │     │              │     │   (DuckDB)  │     │  Dashboard   │
└─────────────┘     └──────────────┘     └──────┬──────┘     └──────────────┘
                                                 │
                                          ┌──────┴──────┐
                                          │ dbt (transform)
                                          └─────────────┘
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Ingestion** | dlt + Python | Extract from GitHub API |
| **Database** | MotherDuck (DuckDB) | Cloud data warehouse |
| **Transform** | dbt | Clean & model data |
| **Dashboard** | Streamlit | Interactive visualization |
| **Orchestration** | GitHub Actions | Daily scheduled runs |

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/teguharia172/github-ai-trend-tracker.git
cd github-ai-trend-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Secrets

Create `.env` file:
```bash
GH_TOKEN=your_github_personal_access_token
MOTHERDUCK_TOKEN=your_motherduck_token
```

Get tokens:
- **GitHub Token**: https://github.com/settings/tokens (needs `public_repo` scope)
- **MotherDuck Token**: https://app.motherduck.com → Settings → Tokens

### 3. Run Pipeline Locally

```bash
# Ingest data
python -c "
from pipelines.github_ai_repos import run_pipeline, AI_QUERIES
run_pipeline(
    destination='motherduck',
    queries=AI_QUERIES,
    max_repos_per_query=100,
    min_stars=10
)
"

# Transform data
cd dbt
dbt deps
dbt build --target prod
cd ..

# Run dashboard
cd dashboard
streamlit run streamlit_app.py
```

Open http://localhost:8501

## 📊 Dashboard Features

- **🔥 Trending**: Top repositories by velocity (stars/day)
- **📊 Analytics**: Language statistics and interactive charts
- **📋 Browse All**: Full repository list with filters
- **🎨 Modern UI**: Dark theme with gradient accents

## 📁 Repository Structure

```
.
├── .github/workflows/      # CI/CD automation
├── dbt/                    # dbt transformations
│   ├── models/             # SQL models
│   └── profiles.yml        # DB connection
├── dashboard/              # Streamlit dashboard
│   ├── streamlit_app.py    # Main app
│   └── requirements.txt    # Dashboard deps
├── pipelines/              # Data ingestion
│   └── github_ai_repos.py  # GitHub API pipeline
├── requirements.txt        # Main dependencies
└── README.md               # This file
```

## 🔄 Automated Pipeline

The pipeline runs daily at 2 AM UTC via GitHub Actions:

1. **Ingest** → Fetches AI repos from GitHub Search API
2. **Transform** → dbt models clean & aggregate data
3. **Deploy** → Streamlit Cloud auto-updates

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Ingestion | dlt, requests |
| Warehouse | MotherDuck (DuckDB) |
| Transform | dbt-core, dbt-duckdb |
| Dashboard | Streamlit, Plotly, Pandas |
| Orchestration | GitHub Actions |

## 📝 Data Models

### Source Tables (raw)
- `github_raw.repositories` → Fetched from GitHub API

### Mart Tables (transformed)
- `dim_repositories` → Repository dimensions
- `fct_language_trends` → Language statistics
- `fct_trending_repos` → Trending repositories

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in Streamlit Cloud dashboard
4. Deploy!

### GitHub Actions
Already configured in `.github/workflows/daily-ingestion.yml`

## 🤝 Contributing

Issues and PRs welcome!

## 📄 License

MIT License - see LICENSE file
