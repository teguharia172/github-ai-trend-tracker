# 🚀 GitHub AI Trend Tracker

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.10-orange.svg)](https://getdbt.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-FF4B4B.svg)](https://streamlit.io)
[![MotherDuck](https://img.shields.io/badge/MotherDuck-🦆-yellow.svg)](https://motherduck.com)

A complete data pipeline that tracks AI/ML open source trends from GitHub, transforms the data with dbt, and visualizes it in a beautiful Streamlit dashboard.

**[View Live Dashboard](https://gh-ai-trend-tracker.streamlit.app/)**

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph Sources["📡 Data Sources"]
        GH[GitHub API]
    end
    
    subgraph Ingestion["📥 Ingestion Layer"]
        DLT[dlt Python]
    end
    
    subgraph Storage["💾 Storage Layer"]
        MD[MotherDuck<br/>Cloud DuckDB]
    end
    
    subgraph Transform["🔧 Transform Layer"]
        DBT[dbt Models]
    end
    
    subgraph Serve["📊 Serving Layer"]
        ST[Streamlit Dashboard]
    end
    
    GH -->|REST API| DLT
    DLT -->|Load| MD
    MD -->|Read| DBT
    DBT -->|Write| MD
    MD -->|Query| ST
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

- **🔥 Trending**: Top repositories by actual daily star velocity (not lifetime average)
- **📊 Analytics**: Language statistics and interactive charts
- **📋 Browse All**: Full repository list with filters (language, activity status, stars)
- **🎨 Clean UI**: Evidence-style minimalist white theme

## ⭐ Star Tracking Feature

The dashboard shows **actual** daily star growth instead of lifetime averages.

```mermaid
flowchart TD
    A[Daily Pipeline Run] --> B[Snapshot Star Counts]
    B --> C[Calculate Growth]
    C --> D[1-Day Growth]
    C --> E[7-Day Growth]
    C --> F[30-Day Growth]
    D --> G[Trending Ranking]
    E --> G
    F --> G
    G --> H[Dashboard Display]
```

| Metric | Description |
|--------|-------------|
| `stars_gained_1d` | Actual stars gained yesterday |
| `stars_gained_7d` | Stars gained in last 7 days |
| `stars_gained_30d` | Stars gained in last 30 days |

## 📁 Repository Structure

```
.
├── .github/workflows/      # CI/CD automation
├── dbt/                    # dbt transformations
│   ├── models/             # SQL models (staging, intermediate, marts)
│   ├── profiles.yml        # DB connection
│   └── dbt_project.yml     # dbt configuration
├── dashboard/              # Streamlit dashboard
│   ├── streamlit_app.py    # Main app
│   └── requirements.txt    # Dashboard deps
├── pipelines/              # Data ingestion
│   └── github_ai_repos.py  # GitHub API pipeline
├── requirements.txt        # Main dependencies
├── README.md               # This file
├── AGENTS.md               # Developer guide
└── DEPLOYMENT.md           # Deployment guide
```

## 🔄 Automated Pipeline

```mermaid
flowchart TB
    subgraph Schedule["⏰ Daily at 2 AM UTC"]
        direction TB
        A[GitHub Actions Trigger] --> B[Fetch from GitHub API]
        B --> C[Load to MotherDuck]
        C --> D[Run dbt Transformations]
        D --> E[Streamlit Auto-Refresh]
    end
```

The pipeline runs daily at 2 AM UTC via GitHub Actions:

1. **Ingest** → Fetches AI repos from GitHub Search API
2. **Transform** → dbt models clean & aggregate data
3. **Deploy** → Streamlit Cloud auto-updates on data refresh

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Ingestion | dlt, requests |
| Warehouse | MotherDuck (DuckDB) |
| Transform | dbt-core, dbt-duckdb |
| Dashboard | Streamlit, Plotly, Pandas |
| Orchestration | GitHub Actions |

## 🗄️ Data Models

### dbt Model Hierarchy

```mermaid
flowchart BT
    subgraph Sources["📥 Sources"]
        SRC[github_raw.repositories]
    end
    
    subgraph Staging["🛠️ Staging"]
        STG[stg_repositories]
    end
    
    subgraph Intermediate["⚙️ Intermediate"]
        INT[int_repo_growth_metrics]
    end
    
    subgraph Marts["📊 Marts"]
        DIM[dim_repositories]
        FCT1[fct_language_trends]
        FCT2[fct_repo_star_history<br/>⭐ Incremental]
        FCT3[fct_repo_star_growth<br/>📈 View]
        FCT4[fct_trending_repos]
    end
    
    SRC --> STG
    STG --> INT
    INT --> DIM
    INT --> FCT2
    FCT2 --> FCT3
    INT --> FCT4
    FCT3 --> FCT4
    STG --> FCT1
```

### Source Tables (raw)
| Table | Description |
|-------|-------------|
| `github_raw.repositories` → Fetched from GitHub Search API |

### Mart Tables (transformed)
| Table | Type | Purpose |
|-------|------|---------|
| `dim_repositories` | Dimension | Repository attributes & metadata |
| `fct_language_trends` | Fact | Language statistics & rankings |
| `fct_repo_star_history` | Incremental | Daily star count snapshots |
| `fct_repo_star_growth` | View | Calculated growth metrics (1d/7d/30d) |
| `fct_trending_repos` | Fact | Trending repos with actual velocity |

## 🌐 Deployment

### Streamlit Cloud (Recommended)
1. Push to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Add `MOTHERDUCK_TOKEN` secret in Streamlit Cloud dashboard
4. Deploy!

### GitHub Actions
Already configured in `.github/workflows/daily-ingestion.yml`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

Issues and PRs welcome!

## 📄 License

MIT License - see LICENSE file
