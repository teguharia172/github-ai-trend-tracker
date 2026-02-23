#!/usr/bin/env python3
"""Validate the GitHub AI Trend Tracker pipeline data."""

import os
import sys
import duckdb
from dotenv import load_dotenv

load_dotenv()

def validate():
    token = os.getenv('MOTHERDUCK_TOKEN')
    if not token:
        print("❌ MOTHERDUCK_TOKEN not set")
        sys.exit(1)
    
    conn = duckdb.connect(f"md:?motherduck_token={token}")
    conn.execute("USE github_ai_analytics")
    
    checks = []
    
    # Check 1: Raw data exists
    raw_count = conn.execute("SELECT COUNT(*) FROM github_raw.repositories").fetchone()[0]
    checks.append(("Raw repositories", raw_count > 0, raw_count))
    
    # Check 2: Mart data exists
    dim_count = conn.execute("SELECT COUNT(*) FROM prod_marts.dim_repositories").fetchone()[0]
    checks.append(("Dim repositories", dim_count > 0, dim_count))
    
    trending_count = conn.execute("SELECT COUNT(*) FROM prod_marts.fct_trending_repos").fetchone()[0]
    checks.append(("Trending repos", trending_count > 0, trending_count))
    
    lang_count = conn.execute("SELECT COUNT(*) FROM prod_marts.fct_language_trends").fetchone()[0]
    checks.append(("Language trends", lang_count > 0, lang_count))
    
    # Check 3: Data freshness (last 24 hours)
    last_load = conn.execute("SELECT MAX(_dlt_extracted_at) FROM github_raw.repositories").fetchone()[0]
    from datetime import datetime, timedelta
    is_fresh = last_load and (datetime.now() - last_load.replace(tzinfo=None)) < timedelta(hours=24)
    checks.append(("Data freshness (< 24h)", is_fresh, str(last_load)))
    
    # Check 4: Top repos have expected structure
    sample = conn.execute("SELECT full_name, stars_count FROM prod_marts.dim_repositories ORDER BY stars_count DESC LIMIT 1").fetchone()
    checks.append(("Sample repo structure", sample and len(sample) == 2, sample))
    
    conn.close()
    
    # Print results
    print("\n=== Pipeline Validation ===\n")
    all_passed = True
    for name, passed, value in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {value}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed")
        sys.exit(1)

if __name__ == '__main__':
    validate()
