# CLAUDE.md — Project Instructions for Claude Code

## Project Overview

**GitHub AI Trend Tracker** — A data pipeline that tracks AI/ML open source trends from GitHub, transforms data with dbt, and visualizes it in a Streamlit dashboard.

## Architecture

```
GitHub API → dlt (Python) → MotherDuck (DuckDB) → dbt → Streamlit Dashboard
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Ingestion | dlt + requests | Extract repos from GitHub Search API |
| Database | MotherDuck (cloud DuckDB) | Cloud data warehouse |
| Transform | dbt-core + dbt-duckdb | Clean & model data |
| Dashboard | Streamlit + Plotly | Interactive visualization |
| Orchestration | GitHub Actions | Daily scheduled runs (2 AM UTC) |

## File Organization

```
.
├── pipelines/
│   └── github_ai_repos.py    # GitHub API ingestion (dlt source/resources)
├── dbt/
│   ├── models/
│   │   ├── staging/           # stg_repositories
│   │   ├── intermediate/      # int_repo_growth_metrics
│   │   └── marts/
│   │       ├── core/          # dim_repositories
│   │       └── metrics/       # fct_language_trends, fct_trending_repos, fct_repo_star_*
│   ├── profiles.yml           # DB connection (dev=local DuckDB, prod=MotherDuck)
│   └── dbt_project.yml
├── dashboard/
│   └── streamlit_app.py       # Main Streamlit app
├── tests/                     # pytest test suite
├── .github/workflows/
│   ├── daily-ingestion.yml    # Daily pipeline + dbt build
│   └── ci.yml                 # PR quality gate (lint, test)
├── requirements.txt           # Python dependencies
├── pyproject.toml             # pytest, black, ruff config
└── Makefile                   # Dev commands
```

## Key Commands

```bash
# Setup
make setup                     # pip install + dbt deps

# Pipeline
make pipeline                  # Run ingestion locally (DuckDB)
python pipelines/github_ai_repos.py  # Same, direct

# dbt
make dbt-build                 # dbt build --target dev
make dbt-build-prod            # dbt build --target prod
make dbt-test                  # dbt test
cd dbt && dbt run --target dev # Run models only

# Dashboard
make dashboard                 # streamlit run dashboard/streamlit_app.py

# Quality
make test                      # pytest tests/ -v
make lint                      # ruff check
make format                    # black + ruff format

# Cleanup
make clean                     # Remove generated files
```

## Environment Variables

Required in `.env` or GitHub Secrets:

| Variable | Purpose | How to get |
|----------|---------|-----------|
| `GH_TOKEN` | GitHub API auth (30 req/min) | https://github.com/settings/tokens (`public_repo` scope) |
| `MOTHERDUCK_TOKEN` | MotherDuck DB access | https://app.motherduck.com → Settings → Tokens |

## Code Style

- **Python**: PEP 8, type hints preferred, f-strings for formatting
- **SQL (dbt)**: lowercase, snake_case, dbt style guide
- **Formatting**: black (line-length 88), ruff for linting
- **Imports**: stdlib → third-party → local (ruff enforces)

## dbt Model DAG

```
Sources:  github_raw.repositories
              ↓
Staging:  stg_repositories
              ↓
Intermediate: int_repo_growth_metrics
              ↓
Marts:    dim_repositories          (dimension — repo attributes)
          fct_language_trends       (fact — language stats)
          fct_repo_star_history     (incremental — daily snapshots)
          fct_repo_star_growth      (view — 1d/7d/30d growth)
          fct_trending_repos        (fact — velocity-ranked repos)
```

- **Naming**: `stg_` (staging), `int_` (intermediate), `dim_` (dimension), `fct_` (fact)
- **MotherDuck database**: `github_ai_analytics`
- **Schemas**: `github_raw` (source), `prod_marts` (transformed)

## Common Development Tasks

### Adding a new AI search query
1. Add query string to `AI_QUERIES` list in `pipelines/github_ai_repos.py`
2. Run pipeline to test: `make pipeline`

### Adding a dashboard widget
1. Edit `dashboard/streamlit_app.py`
2. Use `@st.cache_data(ttl=300)` for any new queries
3. Test locally: `make dashboard`

### Adding a dbt model
1. Create SQL file in appropriate `dbt/models/` subdirectory
2. Add to `dbt_project.yml` if custom materialization needed
3. Run: `cd dbt && dbt run --select model_name`

### Running the full pipeline (local)
```bash
source venv/bin/activate
python -c "from pipelines.github_ai_repos import run_pipeline; run_pipeline(destination='duckdb')"
cd dbt && dbt build --target dev
```

## Testing

- Tests live in `tests/` — run with `make test`
- Pipeline tests mock GitHub API responses (no real API calls)
- Dashboard tests mock the DuckDB connection
- Minimum coverage target: 80%

## GitHub Actions

- **daily-ingestion.yml**: Runs daily at 2 AM UTC — ingests data + dbt build (prod)
- **ci.yml**: Runs on PRs — lint, format check, pytest
