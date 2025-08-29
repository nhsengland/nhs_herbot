"""
Tests for package version functionality.
"""

import pytest

import nhs_herbot


class TestVersion:
    """Tests for package version."""

    def test_version_exists(self):
        """Test that __version__ attribute exists."""
        assert hasattr(nhs_herbot, "__version__")

    def test_version_is_string(self):
        """Test that __version__ is a string."""
        assert isinstance(nhs_herbot.__version__, str)

    def test_version_format(self):
        """Test that __version__ follows expected format."""
        version = nhs_herbot.__version__
        # Should be in format YYYY.MM.DD
        assert len(version.split(".")) == 3
        year, month, day = version.split(".")
        assert len(year) == 4
        assert len(month) == 2
        assert len(day) == 2

    def test_version_value(self):
        """Test that __version__ has the expected current value."""
        assert nhs_herbot.__version__ == "2025.08.12"


if __name__ == "__main__":
    pytest.main([__file__])
