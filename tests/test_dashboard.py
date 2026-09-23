"""Tests for dashboard utility functions."""

import numpy as np
import pandas as pd
import pytest

from dashboard.streamlit_app import filter_trending_by_search, format_number


class TestFormatNumber:
    """Tests for the format_number display helper."""

    def test_millions(self):
        assert format_number(1_500_000) == "1.50M"
        assert format_number(1_000_000) == "1.00M"
        assert format_number(10_000_000) == "10.00M"

    def test_tens_of_thousands(self):
        assert format_number(10_000) == "10.0K"
        assert format_number(50_000) == "50.0K"
        assert format_number(99_999) == "100.0K"

    def test_thousands(self):
        assert format_number(1_000) == "1,000"
        assert format_number(2_561) == "2,561"
        assert format_number(9_999) == "9,999"

    def test_small_numbers(self):
        assert format_number(0) == "0"
        assert format_number(1) == "1"
        assert format_number(999) == "999"
        assert format_number(42) == "42"


def _make_trending_df() -> pd.DataFrame:
    """Build a minimal trending DataFrame suitable for filter tests.

    Each row has deliberately distinct values so that column-specific tests
    can place the query substring in exactly one column without it leaking
    into another column and producing a false-positive match.
    """
    return pd.DataFrame(
        {
            "repo_name": ["llm-toolkit", "awesome-ml", "pytorch-vision"],
            "full_name": [
                "org2/llm-toolkit",
                "user1/awesome-ml",
                "org3/pytorch-vision",
            ],
            "description": [
                "LLM development toolkit",
                "An awesome ML framework",
                "Computer vision library",
            ],
            "stars_count": [12000, 5000, 8000],
            "stars_per_day": [50.0, 10.0, 30.0],
            "activity_status": ["Active", "Very Active", "Moderate"],
            "stars_gained_1d": [120, 25, 60],
        }
    )


class TestFilterTrendingBySearch:
    """Tests for filter_trending_by_search(df, query)."""

    # ------------------------------------------------------------------
    # Empty / whitespace queries -- must return the full DataFrame
    # ------------------------------------------------------------------

    def test_empty_string_returns_all_rows(self):
        df = _make_trending_df()
        result = filter_trending_by_search(df, "")
        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), df.reset_index(drop=True)
        )

    def test_whitespace_spaces_returns_all_rows(self):
        df = _make_trending_df()
        result = filter_trending_by_search(df, "   ")
        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), df.reset_index(drop=True)
        )

    def test_whitespace_tab_returns_all_rows(self):
        df = _make_trending_df()
        result = filter_trending_by_search(df, "\t")
        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), df.reset_index(drop=True)
        )

    def test_whitespace_newline_returns_all_rows(self):
        df = _make_trending_df()
        result = filter_trending_by_search(df, "\n")
        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), df.reset_index(drop=True)
        )

    # ------------------------------------------------------------------
    # Case-insensitive matching per column (each query is unique to one col)
    # ------------------------------------------------------------------

    def test_case_insensitive_match_on_repo_name_lowercase(self):
        """Query in lowercase matches repo_name regardless of stored case."""
        df = pd.DataFrame(
            {
                "repo_name": ["LLM-Toolkit", "awesome-ml"],
                "full_name": ["org2/repo-alpha", "user1/repo-beta"],
                "description": ["Alpha description", "Beta description"],
            }
        )
        result = filter_trending_by_search(df, "llm-toolkit")
        assert len(result) == 1
        assert result.iloc[0]["repo_name"] == "LLM-Toolkit"

    def test_case_insensitive_match_on_repo_name_uppercase(self):
        """Query in uppercase matches repo_name stored in lowercase."""
        df = pd.DataFrame(
            {
                "repo_name": ["llm-toolkit", "awesome-ml"],
                "full_name": ["org2/repo-alpha", "user1/repo-beta"],
                "description": ["Alpha description", "Beta description"],
            }
        )
        result = filter_trending_by_search(df, "LLM-TOOLKIT")
        assert len(result) == 1
        assert result.iloc[0]["repo_name"] == "llm-toolkit"

    def test_case_insensitive_match_on_full_name(self):
        """Query substring matches full_name; repo_name and description do not contain it."""
        df = pd.DataFrame(
            {
                "repo_name": ["alpha-repo", "beta-repo"],
                "full_name": ["org2/MyFramework", "user1/other-thing"],
                "description": ["A generic tool", "Another generic tool"],
            }
        )
        result = filter_trending_by_search(df, "myframework")
        assert len(result) == 1
        assert result.iloc[0]["full_name"] == "org2/MyFramework"

    def test_case_insensitive_match_on_description(self):
        """Query substring matches description; repo_name and full_name do not contain it."""
        df = pd.DataFrame(
            {
                "repo_name": ["alpha-repo", "beta-repo"],
                "full_name": ["org2/alpha", "user1/beta"],
                "description": ["Real-time inference engine", "Data pipeline tool"],
            }
        )
        result = filter_trending_by_search(df, "INFERENCE")
        assert len(result) == 1
        assert "inference" in result.iloc[0]["description"].lower()

    # ------------------------------------------------------------------
    # Partial / multi-row matching
    # ------------------------------------------------------------------

    def test_query_matching_subset_of_rows(self):
        """A query that matches 2 out of 3 rows returns exactly those 2."""
        df2 = pd.DataFrame(
            {
                "repo_name": ["ml-project", "ml-utils", "unrelated"],
                "full_name": ["org/ml-project", "org/ml-utils", "org/unrelated"],
                "description": ["Project for ML", "Utilities for ML", "Something else"],
            }
        )
        result = filter_trending_by_search(df2, "ml")
        assert len(result) == 2
        assert set(result["repo_name"]) == {"ml-project", "ml-utils"}

    def test_query_with_no_matches_returns_empty_dataframe(self):
        """A query that matches nothing returns a DataFrame with zero rows."""
        df = _make_trending_df()
        result = filter_trending_by_search(df, "zzz-no-match-zzz")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        # Columns must be preserved even when empty
        assert set(result.columns) == set(df.columns)

    # ------------------------------------------------------------------
    # NaN / None values must not raise and must not match
    # ------------------------------------------------------------------

    def test_nan_in_repo_name_does_not_raise(self):
        """NaN in repo_name is treated as non-matching without raising."""
        df = pd.DataFrame(
            {
                "repo_name": [np.nan, "llm-toolkit"],
                "full_name": ["org/alpha", "org/llm-toolkit"],
                "description": ["Alpha desc", "LLM desc"],
            }
        )
        result = filter_trending_by_search(df, "llm")
        assert len(result) == 1
        assert result.iloc[0]["repo_name"] == "llm-toolkit"

    def test_none_in_description_does_not_raise(self):
        """None in description is treated as non-matching without raising."""
        df = pd.DataFrame(
            {
                "repo_name": ["alpha-repo", "llm-toolkit"],
                "full_name": ["org/alpha", "org/llm"],
                "description": [None, "LLM inference engine"],
            }
        )
        result = filter_trending_by_search(df, "inference")
        assert len(result) == 1
        assert result.iloc[0]["repo_name"] == "llm-toolkit"

    def test_nan_row_excluded_from_results_when_all_searchable_columns_are_nan(self):
        """A row where all three searchable columns are NaN is not returned."""
        df = pd.DataFrame(
            {
                "repo_name": [np.nan, "real-repo"],
                "full_name": [np.nan, "org/real-repo"],
                "description": [np.nan, "A real description"],
            }
        )
        result = filter_trending_by_search(df, "real")
        assert len(result) == 1
        assert result.iloc[0]["repo_name"] == "real-repo"

    # ------------------------------------------------------------------
    # Immutability: input DataFrame must not be mutated
    # ------------------------------------------------------------------

    def test_input_dataframe_is_not_mutated(self):
        """filter_trending_by_search must return a new DataFrame and leave input unchanged."""
        df = _make_trending_df()
        original = df.copy(deep=True)
        _ = filter_trending_by_search(df, "llm")
        pd.testing.assert_frame_equal(df, original)

    # ------------------------------------------------------------------
    # Regex metacharacter safety — must never crash on special chars
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "query", ["(", "[llm]", "c++", "torch.*", "gpt-4|gemini", "\\k"]
    )
    def test_regex_metacharacters_do_not_raise(self, query):
        """User input containing regex metacharacters must not raise re.error."""
        df = _make_trending_df()
        result = filter_trending_by_search(df, query)
        assert isinstance(result, pd.DataFrame)
