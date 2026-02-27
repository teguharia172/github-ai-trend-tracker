"""Shared test fixtures for the GitHub AI Trend Tracker test suite."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def mock_github_search_response():
    """Mock GitHub Search API response with realistic repo data."""
    return {
        "total_count": 2,
        "incomplete_results": False,
        "items": [
            {
                "id": 123456,
                "name": "awesome-ml",
                "full_name": "user1/awesome-ml",
                "html_url": "https://github.com/user1/awesome-ml",
                "description": "An awesome ML framework",
                "language": "Python",
                "stargazers_count": 5000,
                "forks_count": 800,
                "open_issues_count": 42,
                "created_at": "2023-01-15T00:00:00Z",
                "updated_at": "2026-02-20T12:00:00Z",
                "pushed_at": "2026-02-19T08:00:00Z",
                "topics": ["machine-learning", "python", "ai"],
                "license": {"spdx_id": "MIT"},
                "owner": {
                    "login": "user1",
                    "avatar_url": "https://avatars.githubusercontent.com/u/1",
                },
            },
            {
                "id": 789012,
                "name": "llm-toolkit",
                "full_name": "org2/llm-toolkit",
                "html_url": "https://github.com/org2/llm-toolkit",
                "description": "LLM development toolkit",
                "language": "Rust",
                "stargazers_count": 12000,
                "forks_count": 1500,
                "open_issues_count": 100,
                "created_at": "2024-06-01T00:00:00Z",
                "updated_at": "2026-02-28T10:00:00Z",
                "pushed_at": "2026-02-28T09:00:00Z",
                "topics": ["llm", "rust", "inference"],
                "license": {"spdx_id": "Apache-2.0"},
                "owner": {
                    "login": "org2",
                    "avatar_url": "https://avatars.githubusercontent.com/u/2",
                },
            },
        ],
    }


@pytest.fixture()
def mock_github_empty_response():
    """Mock GitHub Search API response with no results."""
    return {
        "total_count": 0,
        "incomplete_results": False,
        "items": [],
    }


@pytest.fixture()
def mock_env_tokens(monkeypatch):
    """Set mock environment tokens for tests."""
    monkeypatch.setenv("GH_TOKEN", "ghp_test_token_123")
    monkeypatch.setenv("MOTHERDUCK_TOKEN", "md_test_token_456")


@pytest.fixture()
def mock_duckdb_connection():
    """Mock DuckDB connection for dashboard tests."""
    import pandas as pd

    conn = MagicMock()

    repos_df = pd.DataFrame(
        {
            "full_name": ["user1/awesome-ml", "org2/llm-toolkit"],
            "primary_language": ["Python", "Rust"],
            "stars_count": [5000, 12000],
            "forks_count": [800, 1500],
            "open_issues_count": [42, 100],
            "activity_status": ["Very Active", "Active"],
            "description": ["An awesome ML framework", "LLM toolkit"],
            "html_url": [
                "https://github.com/user1/awesome-ml",
                "https://github.com/org2/llm-toolkit",
            ],
        }
    )

    lang_df = pd.DataFrame(
        {
            "language": ["Python", "Rust"],
            "repo_count": [1, 1],
            "total_stars": [5000, 12000],
        }
    )

    trending_df = pd.DataFrame(
        {
            "full_name": ["org2/llm-toolkit", "user1/awesome-ml"],
            "primary_language": ["Rust", "Python"],
            "stars_count": [12000, 5000],
            "stars_per_day": [50.0, 10.0],
            "activity_status": ["Active", "Very Active"],
            "description": ["LLM toolkit", "An awesome ML framework"],
            "html_url": [
                "https://github.com/org2/llm-toolkit",
                "https://github.com/user1/awesome-ml",
            ],
            "stars_gained_1d": [120, 25],
        }
    )

    totals_df = pd.DataFrame(
        {
            "total_repos": [2],
            "total_stars": [17000],
            "total_forks": [2300],
            "total_languages": [2],
        }
    )

    def execute_side_effect(query):
        result = MagicMock()
        if "dim_repositories" in query:
            result.fetchdf.return_value = repos_df
        elif "fct_language_trends" in query:
            result.fetchdf.return_value = lang_df
        elif "fct_trending_repos" in query:
            result.fetchdf.return_value = trending_df
        elif "COUNT(DISTINCT id)" in query:
            result.fetchdf.return_value = totals_df
        else:
            result.fetchdf.return_value = pd.DataFrame()
        return result

    conn.execute = MagicMock(side_effect=execute_side_effect)
    return conn
