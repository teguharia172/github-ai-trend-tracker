"""Tests for dashboard utility functions."""

from dashboard.streamlit_app import format_number


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
