---
name: github-ai-tracker
description: Work with the GitHub AI Trend Tracker data pipeline. Use for data ingestion, dbt transformations, MotherDuck queries, Streamlit dashboard updates, and troubleshooting pipeline issues.
---

# GitHub AI Trend Tracker Skill

Specialized knowledge for maintaining and extending the GitHub AI Trend Tracker pipeline.

## Quick Commands

```bash
# Ingest data (test mode - 3 queries)
python -c "
from pipelines.github_ai_repos import run_pipeline, AI_QUERIES
run_pipeline(
    destination='motherduck',
    queries=AI_QUERIES[:3],
    max_repos_per_query=10,
    min_stars=10
)"

# Full ingestion (all 42 queries)
python -c "
from pipelines.github_ai_repos import run_pipeline, AI_QUERIES
run_pipeline(
    destination='motherduck',
    queries=AI_QUERIES,
    max_repos_per_query=100,
    min_stars=10
)"

# Run dbt
cd dbt && dbt deps && dbt build --target prod

# Run dashboard
cd dashboard && streamlit run streamlit_app.py
```

## Database Schema

### Source Tables
- `github_raw.repositories` - Raw GitHub API data

### Mart Tables
- `prod_marts.dim_repositories` - Repository dimensions
- `prod_marts.fct_trending_repos` - Trending by velocity
- `prod_marts.fct_language_trends` - Language statistics

### Key Columns
```sql
-- Common columns across tables
repo_id, full_name, html_url, description
primary_language, stars_count, forks_count
activity_status, popularity_tier
```

## Environment Setup

Required env vars:
- `GH_TOKEN` - GitHub PAT (needs `public_repo` scope)
- `MOTHERDUCK_TOKEN` - MotherDuck JWT

## Troubleshooting

### No data loaded
1. Check `MOTHERDUCK_TOKEN` is set
2. Verify GitHub API rate limit: `curl -H "Authorization: token $GH_TOKEN" https://api.github.com/rate_limit`
3. Check MotherDuck connection: `duckdb "md:?motherduck_token=$MOTHERDUCK_TOKEN"`

### dbt failures
1. Check `DUCKDB_MOTHERDUCK_TOKEN` is set (separate from ingestion token)
2. Verify sources exist: `dbt debug`
3. Check model compilation: `dbt compile`

### Dashboard not updating
1. Verify data in MotherDuck
2. Check Streamlit Cloud secrets have `MOTHERDUCK_TOKEN`
3. Restart Streamlit Cloud app

## Adding New Features

### New AI Query
1. Add to `AI_QUERIES` list in `pipelines/github_ai_repos.py`
2. Run test ingestion
3. Verify in `github_raw.repositories`

### New dbt Model
1. Create SQL file in `dbt/models/`
2. Add to appropriate folder (staging/marts)
3. Run `dbt build` to test
4. Update `dbt/docs/` if needed

### New Dashboard Widget
1. Edit `dashboard/streamlit_app.py`
2. Use `@st.cache_data(ttl=300)` for queries
3. Test locally: `streamlit run streamlit_app.py`
4. Deploy: Push to GitHub (auto-deploys to Streamlit Cloud)

## References

- See `references/` folder for:
  - `github_api.md` - GitHub Search API details
  - `dbt_models.md` - Model documentation
  - `motherduck_setup.md` - Connection examples
