"""
GitHub AI Repositories Pipeline

This pipeline ingests AI-related open source repositories from GitHub
using the GitHub Search API and GraphQL API.

Data sources:
- Repository metadata (stars, forks, language, created_at, etc.)
- Issues (open/closed counts, labels)
- Pull requests
- Contributors
- Release information

AI Topics covered: machine-learning, deep-learning, llm, ai, 
artificial-intelligence, neural-network, nlp, computer-vision, etc.
"""

import dlt
from dlt.sources.rest_api import rest_api_source
from dlt.sources.rest_api.typing import RESTAPIConfig
from datetime import datetime, timedelta
import requests
from typing import Iterator, Dict, Any, List
import os

# AI-related search queries
# These are GitHub search queries (NOT regex). Supports GitHub search qualifiers:
#   stars:>100        - repos with >100 stars
#   language:python   - Python repos only
#   created:>2024-01  - created after Jan 2024
#   pushed:>2024-06   - active since June 2024
#   topic:llm         - tagged with 'llm' topic
# See: https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories
AI_QUERIES = [
    # Core AI/ML topics
    "machine-learning",
    "deep-learning",
    "llm",
    "large-language-model",
    "artificial-intelligence",
    "neural-network",
    "nlp",
    "natural-language-processing",
    "computer-vision",
    "multimodal-ai",  # Handles text, image, video, audio

    # Large Language Models (updated with 2026 leaders)
    "gpt-5",
    "claude-opus",
    "gemini-pro",
    "grok-xai",
    "kimi-k2.5",  # Latest version: trillion-param multimodal agentic model
    "deepseek-v3",
    "qwen3",
    "llama-4",
    "glm-4",
    "mistral-lechat",  # Includes rising Chinese/open models
    "open-source-llm",

    # Frameworks & Tools (expanded for agentic/RAG/MLOps)
    "transformers",
    "pytorch",
    "tensorflow",
    "keras",  # High-level DL prototyping
    "jax",  # Research/performance
    "langchain",
    "langgraph",  # Agent orchestration
    "llamaindex",  # RAG/data frameworks
    "openai-api",
    "huggingface",
    "ollama",
    "autogen",  # Multi-agent
    "crewai",  # Agentic workflows
    "openclaw",  # Autonomous agent framework for local task execution
    "vector-database",
    "rag",  # Retrieval-augmented generation
    "agentic-ai",  # Autonomous agents, top 2026 trend

    # Emerging Trends (2026-specific)
    "mlops",  # Production pipelines
    "fine-tuning",
    "lora-peft",  # Efficient tuning
    "open-source-llm"  # Granite, Olmo, etc.
]


def get_github_headers():
    """Get GitHub API headers with authentication."""
    token = os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-ai-trend-tracker",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def search_repositories(
    query: str, 
    sort: str = "stars", 
    order: str = "desc", 
    per_page: int = 100,
    min_stars: int = 100,           # Minimum stars filter
    language: str = None,            # Filter by language (e.g., "python", "go")
    created_after: str = None,       # Filter by creation date (e.g., "2024-01-01")
    pushed_after: str = None,        # Filter by last push date
) -> Iterator[Dict[str, Any]]:
    """
    Search GitHub repositories by query.
    
    Args:
        query: Search term (topic, keyword, etc.)
        sort: Sort field (stars, forks, updated, etc.)
        order: Sort order (desc, asc)
        per_page: Results per page (max 100)
        min_stars: Minimum star count (default 100)
        language: Filter by programming language (e.g., "python")
        created_after: Only repos created after this date (YYYY-MM-DD)
        pushed_after: Only repos pushed after this date (YYYY-MM-DD)
    
    GitHub Search API has rate limits:
    - Authenticated: 30 requests per minute
    - Unauthenticated: 10 requests per minute
    
    Full search syntax: https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories
    """
    url = "https://api.github.com/search/repositories"
    headers = get_github_headers()
    
    # Build the search query with qualifiers
    search_query = f"{query} stars:>{min_stars}"
    if language:
        search_query += f" language:{language}"
    if created_after:
        search_query += f" created:>{created_after}"
    if pushed_after:
        search_query += f" pushed:>{pushed_after}"
    
    params = {
        "q": search_query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
    }
    
    page = 1
    max_pages = 10  # Limit to 1000 results (GitHub's max)
    
    while page <= max_pages:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 403:
            # Rate limited
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(reset_time - int(datetime.now().timestamp()), 0) + 1
            print(f"Rate limited. Waiting {wait_time} seconds...")
            import time
            time.sleep(wait_time)
            continue
        
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        if not items:
            break
        
        for item in items:
            # Enrich with query info
            item["search_query"] = query
            item["_dlt_extracted_at"] = datetime.utcnow().isoformat()
            yield item
        
        # Check if we've reached the end
        if len(items) < per_page:
            break
        
        page += 1


def get_repo_details(owner: str, repo: str) -> Dict[str, Any]:
    """Get detailed information about a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = get_github_headers()
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_repo_languages(owner: str, repo: str) -> Dict[str, Any]:
    """Get language breakdown for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    headers = get_github_headers()
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return {
        "owner": owner,
        "repo": repo,
        "languages": response.json(),
        "_dlt_extracted_at": datetime.utcnow().isoformat(),
    }


def get_repo_topics(owner: str, repo: str) -> List[Dict[str, Any]]:
    """Get topics for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    headers = get_github_headers()
    headers["Accept"] = "application/vnd.github.mercy-preview+json"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    topics = response.json().get("names", [])
    return [
        {
            "owner": owner,
            "repo": repo,
            "topic": topic,
            "_dlt_extracted_at": datetime.utcnow().isoformat(),
        }
        for topic in topics
    ]


def get_repo_contributors(owner: str, repo: str, max_pages: int = 3) -> Iterator[Dict[str, Any]]:
    """Get top contributors for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    headers = get_github_headers()
    
    params = {"per_page": 100}
    
    for page in range(1, max_pages + 1):
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 204:  # No content
            return
        
        response.raise_for_status()
        contributors = response.json()
        
        if not contributors:
            break
        
        for contributor in contributors:
            contributor["owner"] = owner
            contributor["repo"] = repo
            contributor["_dlt_extracted_at"] = datetime.utcnow().isoformat()
            yield contributor


def get_repo_releases(owner: str, repo: str, max_pages: int = 5) -> Iterator[Dict[str, Any]]:
    """Get releases for a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = get_github_headers()
    
    params = {"per_page": 100}
    
    for page in range(1, max_pages + 1):
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        releases = response.json()
        
        if not releases:
            break
        
        for release in releases:
            release["owner"] = owner
            release["repo"] = repo
            release["_dlt_extracted_at"] = datetime.utcnow().isoformat()
            yield release


@dlt.source(name="github_ai_repos")
def github_ai_source(
    queries: List[str] = None,
    max_repos_per_query: int = 100,
    min_stars: int = 100,
    language: str = None,
    created_after: str = None,
    pushed_after: str = None,
):
    """
    dlt source for GitHub AI repositories.
    
    Args:
        queries: List of search queries. Defaults to AI_QUERIES.
        max_repos_per_query: Maximum repositories to fetch per query.
        min_stars: Minimum star count for repos (default 100).
        language: Filter by programming language (e.g., "python", "go").
        created_after: Only repos created after this date (YYYY-MM-DD).
        pushed_after: Only repos pushed after this date (YYYY-MM-DD).
    """
    queries = queries or AI_QUERIES[:3]  # Default to first 3 queries
    
    @dlt.resource(name="repositories", write_disposition="merge", primary_key=["id"])
    def repositories():
        """Fetch AI repositories from GitHub."""
        for query in queries:
            print(f"Searching for: {query}")
            count = 0
            for repo in search_repositories(
                query, 
                per_page=100,
                min_stars=min_stars,
                language=language,
                created_after=created_after,
                pushed_after=pushed_after,
            ):
                yield repo
                count += 1
                if count >= max_repos_per_query:
                    break
    
    @dlt.resource(name="languages", write_disposition="merge", primary_key=["owner", "repo"])
    def languages():
        """Fetch language data for repositories."""
        # Get unique owner/repo pairs from repositories
        # In production, you'd query the loaded repositories
        # For now, we'll fetch for the first batch
        pass
    
    @dlt.resource(name="topics", write_disposition="merge", primary_key=["owner", "repo", "topic"])
    def topics():
        """Fetch topics for repositories."""
        pass
    
    @dlt.resource(name="contributors", write_disposition="merge", primary_key=["owner", "repo", "login"])
    def contributors():
        """Fetch contributors for repositories."""
        pass
    
    @dlt.resource(name="releases", write_disposition="merge", primary_key=["owner", "repo", "id"])
    def releases():
        """Fetch releases for repositories."""
        pass
    
    # Only return repositories for now (other resources need implementation)
    return repositories


def run_pipeline(
    destination: str = "duckdb",
    queries: List[str] = None,
    max_repos_per_query: int = 100,
    min_stars: int = 100,
    language: str = None,
    created_after: str = None,
    pushed_after: str = None,
):
    """
    Run the GitHub AI repos pipeline.
    
    Args:
        destination: Where to load data. Options: "duckdb", "motherduck", "bigquery"
        queries: Custom list of search queries (defaults to AI_QUERIES[:5])
        max_repos_per_query: Max repos to fetch per query (default 100)
        min_stars: Minimum star count (default 100)
        language: Filter by programming language (e.g., "python")
        created_after: Only repos created after date (YYYY-MM-DD)
        pushed_after: Only repos pushed after date (YYYY-MM-DD)
    
    Examples:
        # Default: Fetch top 5 AI queries
        run_pipeline()
        
        # Only Python repos with >1000 stars
        run_pipeline(language="python", min_stars=1000)
        
        # Recently created repos (last 6 months)
        run_pipeline(created_after="2024-08-01")
        
        # Custom search queries
        run_pipeline(queries=["generative-ai", "stable-diffusion", "whisper"])
    """
    # Configure destination
    if destination == "motherduck":
        token = os.getenv("MOTHERDUCK_TOKEN")
        if not token:
            raise ValueError("MOTHERDUCK_TOKEN environment variable not set")
        # Create MotherDuck destination with credentials
        dest = dlt.destinations.motherduck(f"md:///github_ai_analytics?token={token}")
    else:
        dest = destination
    
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="github_ai_trends",
        destination=dest,
        dataset_name="github_raw",
    )
    
    # Use default queries if none provided
    queries = queries or AI_QUERIES[:5]
    
    print(f"Running pipeline with {len(queries)} queries, max {max_repos_per_query} repos per query")
    
    # Create source with filters
    source = github_ai_source(
        queries=queries,
        max_repos_per_query=max_repos_per_query,
        min_stars=min_stars,
        language=language,
        created_after=created_after,
        pushed_after=pushed_after,
    )
    
    # Run pipeline
    info = pipeline.run(source)
    print(info)
    
    return info


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run locally with DuckDB for testing
    run_pipeline(destination="duckdb")
