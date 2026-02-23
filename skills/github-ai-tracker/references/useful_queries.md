# Useful Queries for GitHub AI Trend Tracker

## Check Data Freshness

```python
import duckdb
import os

conn = duckdb.connect(f"md:?motherduck_token={os.getenv('MOTHERDUCK_TOKEN')}")
conn.execute("USE github_ai_analytics")

# Check counts
print("Raw:", conn.execute("SELECT COUNT(*) FROM github_raw.repositories").fetchone()[0])
print("Dim:", conn.execute("SELECT COUNT(*) FROM prod_marts.dim_repositories").fetchone()[0])
print("Latest:", conn.execute("SELECT MAX(_dlt_extracted_at) FROM github_raw.repositories").fetchone()[0])
```

## Top Repos by Category

```sql
-- Top ML repos
SELECT full_name, stars_count, primary_language
FROM prod_marts.dim_repositories
WHERE search_query LIKE '%machine-learning%'
ORDER BY stars_count DESC
LIMIT 10;

-- Top LLM repos
SELECT full_name, stars_count, primary_language
FROM prod_marts.dim_repositories
WHERE search_query LIKE '%llm%'
ORDER BY stars_count DESC
LIMIT 10;
```

## Language Statistics

```sql
-- Language breakdown
SELECT 
    primary_language,
    COUNT(*) as repo_count,
    AVG(stars_count) as avg_stars,
    SUM(stars_count) as total_stars
FROM prod_marts.dim_repositories
GROUP BY primary_language
ORDER BY total_stars DESC;
```

## Activity Analysis

```sql
-- Activity status distribution
SELECT 
    activity_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM prod_marts.dim_repositories
GROUP BY activity_status
ORDER BY count DESC;

-- Recently updated repos
SELECT full_name, pushed_at, days_since_last_push
FROM prod_marts.dim_repositories
WHERE days_since_last_push < 7
ORDER BY pushed_at DESC;
```
