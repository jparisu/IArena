"""
Pytest configuration file for iarena tests.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"value": 42, "data": [1, 2, 3, 4, 5]}


@pytest.fixture
def sample_value():
    """Provide a sample value for tests."""
    return 10
