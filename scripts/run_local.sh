#!/bin/bash

# Quick script to run the full pipeline locally

set -e

echo "🚀 Running GitHub AI Trend Tracker - Local Mode"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Run ./scripts/setup.sh first"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Step 1: Extract
echo "📥 Step 1: Extracting data from GitHub..."
python pipelines/github_ai_repos.py

# Step 2: Transform
echo ""
echo "🔧 Step 2: Running dbt transformations..."
cd dbt
dbt build --target local
cd ..

# Step 3: Summary
echo ""
echo "✅ Pipeline complete!"
echo ""
echo "Summary:"
python -c "
import duckdb
conn = duckdb.connect('github_ai_trends.duckdb')
result = conn.execute('''
    select 
        count(*) as repos,
        sum(stargazers_count) as stars,
        count(distinct language) as languages
    from github_raw.repositories
''').fetchone()
print(f'  Repositories: {result[0]}')
print(f'  Total Stars: {result[1]:,}')
print(f'  Languages: {result[2]}')
conn.close()
"

echo ""
echo "View your data:"
echo "  - Database: github_ai_trends.duckdb"
echo "  - Dashboard: cd dashboard && npm run dev"
