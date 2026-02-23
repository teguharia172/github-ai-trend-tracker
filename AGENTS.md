# AGENTS.md - Kimi Code Agent Instructions

This file provides persistent instructions for Kimi Code when working on this project.

## Project Overview

**GitHub AI Trend Tracker** - A data pipeline that tracks AI/ML open source trends from GitHub.

## Architecture

```
GitHub API → dlt (ingest) → MotherDuck → dbt (transform) → Streamlit Dashboard
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Ingestion | Python, dlt, requests |
| Database | MotherDuck (DuckDB) |
| Transform | dbt-core, dbt-duckdb |
| Dashboard | Streamlit, Plotly |
| Orchestration | GitHub Actions |

## Key Commands

```bash
# Run ingestion
python -c "from pipelines.github_ai_repos import run_pipeline, AI_QUERIES; run_pipeline(destination='motherduck', queries=AI_QUERIES, max_repos_per_query=100, min_stars=10)"

# Run dbt
cd dbt && dbt deps && dbt build --target prod

# Run dashboard
cd dashboard && streamlit run streamlit_app.py
```

## Environment Variables

Required in `.env` or GitHub Secrets:
- `GH_TOKEN` - GitHub Personal Access Token
- `MOTHERDUCK_TOKEN` - MotherDuck JWT token

## Code Style

- Python: PEP 8, type hints preferred
- SQL: dbt style, lowercase, snake_case
- Use f-strings for formatting
- Prefer explicit over implicit

## File Organization

```
.
├── .github/workflows/    # CI/CD
├── dbt/                  # dbt models
├── dashboard/            # Streamlit app
├── pipelines/            # Data ingestion
└── requirements.txt      # Dependencies
```

## Common Tasks

### Adding new data source
1. Add query to `AI_QUERIES` in `pipelines/github_ai_repos.py`
2. Run ingestion to test
3. Update dbt models if needed

### Adding dashboard widget
1. Edit `dashboard/streamlit_app.py`
2. Use st.cache_data for queries
3. Test locally before pushing

### Debugging pipeline
1. Check `github_raw.repositories` count
2. Verify `MOTHERDUCK_TOKEN` is set
3. Run with smaller query subset

## Notes

- MotherDuck database: `github_ai_analytics`
- GitHub API rate limit: 30 req/min
- Pipeline runs daily at 2 AM UTC
- Streamlit Cloud auto-redeploys on data update
