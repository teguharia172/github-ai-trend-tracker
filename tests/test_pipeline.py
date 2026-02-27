"""Tests for the GitHub AI repos pipeline."""

from unittest.mock import MagicMock, patch

import pytest

from pipelines.github_ai_repos import (
    AI_QUERIES,
    get_github_headers,
    search_repositories,
)


class TestAIQueries:
    """Tests for the AI_QUERIES configuration."""

    def test_queries_is_nonempty_list(self):
        assert isinstance(AI_QUERIES, list)
        assert len(AI_QUERIES) > 0

    def test_queries_are_strings(self):
        for query in AI_QUERIES:
            assert isinstance(query, str)
            assert len(query) > 0

    def test_core_topics_present(self):
        core_topics = ["machine-learning", "deep-learning", "llm", "nlp"]
        for topic in core_topics:
            assert topic in AI_QUERIES, f"Missing core topic: {topic}"

    def test_framework_topics_present(self):
        frameworks = ["pytorch", "tensorflow", "langchain", "huggingface"]
        for fw in frameworks:
            assert fw in AI_QUERIES, f"Missing framework: {fw}"


class TestGetGitHubHeaders:
    """Tests for get_github_headers."""

    def test_headers_without_token(self, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        headers = get_github_headers()
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert "Authorization" not in headers

    def test_headers_with_token(self, monkeypatch):
        monkeypatch.setenv("GH_TOKEN", "ghp_test123")
        headers = get_github_headers()
        assert headers["Authorization"] == "token ghp_test123"
        assert "Accept" in headers
        assert "User-Agent" in headers


class TestSearchRepositories:
    """Tests for search_repositories."""

    @patch("pipelines.github_ai_repos.requests.get")
    def test_basic_search(self, mock_get, mock_github_search_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_search_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = list(search_repositories("machine-learning", per_page=10))

        assert len(results) == 2
        assert results[0]["name"] == "awesome-ml"
        assert results[1]["name"] == "llm-toolkit"
        # Verify enrichment fields added
        assert results[0]["search_query"] == "machine-learning"
        assert "_dlt_extracted_at" in results[0]

    @patch("pipelines.github_ai_repos.requests.get")
    def test_search_with_language_filter(self, mock_get, mock_github_search_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_search_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        list(search_repositories("llm", language="python"))

        call_params = mock_get.call_args[1]["params"]
        assert "language:python" in call_params["q"]

    @patch("pipelines.github_ai_repos.requests.get")
    def test_search_with_date_filters(self, mock_get, mock_github_search_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_search_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        list(
            search_repositories(
                "ai",
                created_after="2024-01-01",
                pushed_after="2025-06-01",
            )
        )

        call_params = mock_get.call_args[1]["params"]
        assert "created:>2024-01-01" in call_params["q"]
        assert "pushed:>2025-06-01" in call_params["q"]

    @patch("pipelines.github_ai_repos.requests.get")
    def test_search_with_min_stars(self, mock_get, mock_github_search_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_search_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        list(search_repositories("ml", min_stars=500))

        call_params = mock_get.call_args[1]["params"]
        assert "stars:>500" in call_params["q"]

    @patch("pipelines.github_ai_repos.requests.get")
    def test_empty_results(self, mock_get, mock_github_empty_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_empty_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = list(search_repositories("nonexistent-topic-xyz"))
        assert results == []

    @patch("pipelines.github_ai_repos.requests.get")
    def test_pagination_stops_on_partial_page(self, mock_get):
        """When a page returns fewer items than per_page, stop paginating."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 1,
            "items": [{"id": 1, "name": "repo1"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = list(search_repositories("test", per_page=100))
        assert len(results) == 1
        # Should only make 1 request (partial page = stop)
        assert mock_get.call_count == 1

    @patch("pipelines.github_ai_repos.requests.get")
    def test_http_error_raises(self, mock_get):
        """Non-rate-limit HTTP errors should propagate."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Server Error"):
            list(search_repositories("ml"))


class TestRunPipeline:
    """Tests for run_pipeline."""

    def test_motherduck_requires_token(self, monkeypatch):
        monkeypatch.delenv("MOTHERDUCK_TOKEN", raising=False)
        from pipelines.github_ai_repos import run_pipeline

        with pytest.raises(ValueError, match="MOTHERDUCK_TOKEN"):
            run_pipeline(destination="motherduck")
