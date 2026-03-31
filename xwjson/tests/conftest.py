#exonware/xwjson/tests/conftest.py
"""
Shared pytest fixtures for xwjson tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys
# Ensure src is in path for imports
tests_dir = Path(__file__).resolve().parent
project_root = tests_dir.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
# Add dependency source paths (monorepo structure)
workspace_root = project_root.parent
dependency_paths = [
    workspace_root / "xwsystem" / "src",
    workspace_root / "xwnode" / "src",
    workspace_root / "xwschema" / "src",
]
for dep_path in dependency_paths:
    if dep_path.exists() and str(dep_path) not in sys.path:
        sys.path.insert(0, str(dep_path))
@pytest.fixture


def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)
@pytest.fixture


def sample_data():
    """Sample data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ],
        "metadata": {
            "version": "1.0",
            "created": "2025-01-01"
        }
    }
@pytest.fixture


def xwjson_serializer():
    """XWJSONSerializer instance for testing."""
    from exonware.xwjson import XWJSONSerializer
    return XWJSONSerializer()
