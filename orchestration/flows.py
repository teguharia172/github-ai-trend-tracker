"""
Prefect flows for GitHub AI Trend Tracker

This module contains the orchestration logic for:
1. Ingesting data from GitHub API
2. Running dbt transformations
3. Running data quality tests
4. Generating reports
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.schedules import IntervalSchedule

# Add pipelines to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "pipelines"))

from github_ai_repos import github_ai_source, AI_QUERIES


@task(retries=3, retry_delay_seconds=60)
def extract_github_data(queries: list = None, max_repos: int = 100):
    """
    Extract data from GitHub API using dlt.
    
    Args:
        queries: List of search queries
        max_repos: Maximum repos per query
    """
    import dlt
    
    logger = get_run_logger()
    logger.info("Starting GitHub data extraction...")
    
    queries = queries or AI_QUERIES[:5]
    
    # Determine destination
    destination = os.getenv("MOTHERDUCK_TOKEN") and "motherduck" or "duckdb"
    logger.info(f"Using destination: {destination}")
    
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="github_ai_trends",
        destination=destination,
        dataset_name="github_raw",
    )
    
    # Create source
    source = github_ai_source(
        queries=queries,
        max_repos_per_query=max_repos,
    )
    
    # Run pipeline
    info = pipeline.run(source)
    
    logger.info(f"Extracted {len(info.loads)} loads")
    logger.info(f"Destination: {info.destination}")
    
    return info


@task
def run_dbt_transformations(models: str = None, full_refresh: bool = False):
    """
    Run dbt models.
    
    Args:
        models: Specific models to run (optional)
        full_refresh: Whether to do a full refresh
    """
    logger = get_run_logger()
    logger.info("Running dbt transformations...")
    
    dbt_dir = Path(__file__).parent.parent / "dbt"
    
    cmd = ["dbt", "run"]
    
    if models:
        cmd.extend(["--select", models])
    
    if full_refresh:
        cmd.append("--full-refresh")
    
    cmd.extend(["--profiles-dir", str(dbt_dir)])
    
    result = subprocess.run(
        cmd,
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    logger.info(f"dbt stdout: {result.stdout}")
    if result.stderr:
        logger.warning(f"dbt stderr: {result.stderr}")
    
    result.check_returncode()
    
    return {"status": "success", "models": models}


@task
def run_dbt_tests(models: str = None):
    """
    Run dbt tests.
    
    Args:
        models: Specific models to test (optional)
    """
    logger = get_run_logger()
    logger.info("Running dbt tests...")
    
    dbt_dir = Path(__file__).parent.parent / "dbt"
    
    cmd = ["dbt", "test"]
    
    if models:
        cmd.extend(["--select", models])
    
    cmd.extend(["--profiles-dir", str(dbt_dir)])
    
    result = subprocess.run(
        cmd,
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    logger.info(f"dbt test stdout: {result.stdout}")
    if result.stderr:
        logger.warning(f"dbt test stderr: {result.stderr}")
    
    result.check_returncode()
    
    return {"status": "success", "tests_run": True}


@task
def generate_elementary_report():
    """Generate Elementary data observability report."""
    logger = get_run_logger()
    logger.info("Generating Elementary report...")
    
    dbt_dir = Path(__file__).parent.parent / "dbt"
    
    cmd = [
        "edr", "monitor", "report",
        "--profiles-dir", str(dbt_dir),
        "--project-dir", str(dbt_dir)
    ]
    
    result = subprocess.run(
        cmd,
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )
    
    logger.info(f"Elementary stdout: {result.stdout}")
    if result.stderr:
        logger.warning(f"Elementary stderr: {result.stderr}")
    
    # Don't fail if elementary isn't fully configured
    return {"status": "completed"}


@task
def generate_summary_stats():
    """Generate summary statistics for monitoring."""
    logger = get_run_logger()
    logger.info("Generating summary stats...")
    
    import duckdb
    
    # Connect to database
    if os.getenv("MOTHERDUCK_TOKEN"):
        conn = duckdb.connect("md:github_ai_analytics")
    else:
        conn = duckdb.connect("github_ai_analytics.duckdb")
    
    # Get summary stats
    result = conn.execute("""
        select
            count(*) as total_repos,
            sum(stars_count) as total_stars,
            count(distinct primary_language) as unique_languages,
            max(extracted_at) as last_extracted
        from github_raw.repositories
    """).fetchone()
    
    stats = {
        "total_repos": result[0],
        "total_stars": result[1],
        "unique_languages": result[2],
        "last_extracted": result[3],
    }
    
    logger.info(f"Summary stats: {stats}")
    
    conn.close()
    
    return stats


@flow(name="github-ai-etl-pipeline", log_prints=True)
def github_ai_etl_pipeline(
    queries: list = None,
    max_repos: int = 100,
    full_refresh: bool = False,
    run_tests: bool = True
):
    """
    Main ETL pipeline for GitHub AI Trend Tracker.
    
    This flow:
    1. Extracts data from GitHub API
    2. Runs dbt transformations
    3. Runs data quality tests
    4. Generates observability reports
    
    Args:
        queries: List of AI-related search queries
        max_repos: Maximum repositories to fetch per query
        full_refresh: Whether to do a full refresh
        run_tests: Whether to run dbt tests
    """
    logger = get_run_logger()
    logger.info("🚀 Starting GitHub AI ETL Pipeline")
    
    # Step 1: Extract
    extract_result = extract_github_data(
        queries=queries,
        max_repos=max_repos
    )
    
    # Step 2: Transform
    transform_result = run_dbt_transformations(
        full_refresh=full_refresh
    )
    
    # Step 3: Test
    if run_tests:
        test_result = run_dbt_tests()
    
    # Step 4: Generate stats
    stats = generate_summary_stats()
    
    logger.info("✅ Pipeline completed successfully!")
    logger.info(f"Stats: {stats}")
    
    return {
        "extract": extract_result,
        "transform": transform_result,
        "stats": stats,
    }


@flow(name="daily-refresh", log_prints=True)
def daily_refresh():
    """Daily refresh flow - runs the full pipeline."""
    return github_ai_etl_pipeline(
        queries=AI_QUERIES[:5],
        max_repos=100,
        full_refresh=False,
        run_tests=True
    )


@flow(name="weekly-full-refresh", log_prints=True)
def weekly_full_refresh():
    """Weekly full refresh flow."""
    return github_ai_etl_pipeline(
        queries=AI_QUERIES,
        max_repos=200,
        full_refresh=True,
        run_tests=True
    )


if __name__ == "__main__":
    # Run locally for testing
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the pipeline
    result = github_ai_etl_pipeline(
        queries=AI_QUERIES[:2],  # Just 2 queries for testing
        max_repos=50,  # Small batch for testing
        full_refresh=True,
        run_tests=False
    )
    
    print(f"Result: {result}")
