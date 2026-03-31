#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_dependency_graph.py
"""
Unit tests for dependency graph and batch operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.dependency_graph import XWJSONDependencyGraph
@pytest.mark.xwjson_unit


def test_dependency_graph_init():
    """Test dependency graph initialization."""
    graph = XWJSONDependencyGraph()
    assert graph is not None
@pytest.mark.xwjson_unit


def test_add_operation():
    """Test adding operations to graph."""
    graph = XWJSONDependencyGraph()
    graph.add_operation("op1", {"op": "update_path", "path": "/users/0/name", "value": "Alice"})
    assert "op1" in graph._operations
@pytest.mark.xwjson_unit


def test_add_dependency():
    """Test adding dependencies."""
    graph = XWJSONDependencyGraph()
    graph.add_operation("op1", {"op": "update_path", "path": "/users/0/id", "value": 2})
    graph.add_operation("op2", {"op": "move", "from": "/users/0", "to": "/users/2"})
    graph.add_dependency("op2", "op1")  # op2 depends on op1
    assert "op1" in graph._dependencies["op2"]
@pytest.mark.xwjson_unit


def test_detect_conflicts():
    """Test conflict detection."""
    graph = XWJSONDependencyGraph()
    operations = [
        {"op": "update_path", "path": "/users/0/name", "value": "Alice"},
        {"op": "update_path", "path": "/users/0/name", "value": "Bob"},  # Conflict: same path
        {"op": "update_path", "path": "/users/1/age", "value": 30},  # No conflict
    ]
    conflicts = graph.detect_conflicts(operations)
    assert len(conflicts) > 0
    # op_0 and op_1 should conflict
    assert "op_1" in conflicts.get("op_0", [])
@pytest.mark.xwjson_unit


def test_topological_sort():
    """Test topological sort."""
    graph = XWJSONDependencyGraph()
    operations = [
        {"op": "update_path", "path": "/users/0/id", "value": 2},  # op_0
        {"op": "update_path", "path": "/users/0/name", "value": "Alice"},  # op_1
        {"op": "move", "from": "/users/0", "to": "/users/2"},  # op_2 (depends on op_0)
    ]
    levels = graph.topological_sort(operations)
    assert len(levels) > 0
    # op_0 and op_1 should be in first level (parallel)
    # op_2 should be in second level (depends on op_0)
    first_level = levels[0]
    assert "op_0" in first_level or "op_1" in first_level
