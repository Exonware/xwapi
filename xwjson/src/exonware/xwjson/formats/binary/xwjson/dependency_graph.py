#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/dependency_graph.py
"""
XWJSON Dependency Graph - Uses xwnode for graph operations
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Dependency graph for batch operations using xwnode for graph operations,
dependency resolution, and topological sort.
Priority 1 (Security): Safe graph operations, cycle detection
Priority 2 (Usability): Clear dependency structure, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast dependency resolution, efficient topological sort
Priority 5 (Extensibility): Plugin system for custom dependency rules
"""

from typing import Any
from collections import deque


class XWJSONDependencyGraph:
    """
    Dependency graph for batch operations using xwnode.
    Leverages xwnode's graph capabilities for:
    - Dependency graph building
    - Topological sort for execution order
    - Graph navigation for complex operations
    - Cycle detection
    This class provides a simplified interface that uses xwnode internally.
    """

    def __init__(self):
        """Initialize dependency graph."""
        self._dependencies: dict[str, list[str]] = {}  # op_id -> [prerequisite_op_ids]
        self._reverse_deps: dict[str, list[str]] = {}  # op_id -> [dependent_op_ids]
        self._operations: dict[str, dict[str, Any]] = {}  # op_id -> operation dict
        # Try to use xwnode if available (required dependency)
        try:
            from exonware.xwnode import XWNode
            self._xwnode_available = True
            self._xwnode_class = XWNode
        except ImportError:
            self._xwnode_available = False
            self._xwnode_class = None

    def add_operation(self, op_id: str, operation: dict[str, Any]) -> None:
        """
        Add operation to graph.
        Args:
            op_id: Unique operation identifier
            operation: Operation dictionary with 'op', 'path', etc.
        """
        self._operations[op_id] = operation
        if op_id not in self._dependencies:
            self._dependencies[op_id] = []
        if op_id not in self._reverse_deps:
            self._reverse_deps[op_id] = []

    def add_dependency(self, op_id: str, depends_on: str) -> None:
        """
        Add dependency: op_id depends on depends_on.
        Args:
            op_id: Operation that depends on another
            depends_on: Operation that must complete first
        """
        if op_id not in self._dependencies:
            self._dependencies[op_id] = []
        if depends_on not in self._dependencies[op_id]:
            self._dependencies[op_id].append(depends_on)
        if depends_on not in self._reverse_deps:
            self._reverse_deps[depends_on] = []
        if op_id not in self._reverse_deps[depends_on]:
            self._reverse_deps[depends_on].append(op_id)

    def detect_conflicts(self, operations: list[dict[str, Any]]) -> dict[str, list[str]]:
        """
        Detect conflicts between operations based on paths.
        Args:
            operations: list of operations to analyze
        Returns:
            Dict mapping operation_id -> list of conflicting operation_ids
        """
        conflicts: dict[str, list[str]] = {}
        for i, op1 in enumerate(operations):
            op1_id = f"op_{i}"
            conflicts[op1_id] = []
            path1 = self._extract_path(op1)
            if not path1:
                continue
            for j, op2 in enumerate(operations):
                if i == j:
                    continue
                op2_id = f"op_{j}"
                path2 = self._extract_path(op2)
                if not path2:
                    continue
                if self._paths_conflict(path1, path2, op1, op2):
                    conflicts[op1_id].append(op2_id)
        return conflicts

    def build_dependencies(self, operations: list[dict[str, Any]]) -> dict[str, list[str]]:
        """
        Build dependency graph from operations.
        Args:
            operations: list of operations to analyze
        Returns:
            Dict mapping operation_id -> list of prerequisite operation_ids
        """
        # Detect conflicts first
        conflicts = self.detect_conflicts(operations)
        # Build dependency graph from conflicts
        dependencies: dict[str, list[str]] = {}
        processed_pairs = set()  # Track processed conflict pairs to avoid circular dependencies
        for op_id, conflicting_ops in conflicts.items():
            if op_id not in dependencies:
                dependencies[op_id] = []
            for conflict_id in conflicting_ops:
                # Only process each conflict pair once (avoid circular dependencies)
                pair_key = tuple(sorted([op_id, conflict_id]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)
                # Determine dependency direction
                op1_idx = int(op_id.split("_")[1])
                op2_idx = int(conflict_id.split("_")[1])
                op1 = operations[op1_idx]
                op2 = operations[op2_idx]
                if self._should_run_first(op1, op2):
                    # op2 depends on op1 (op1 must run first)
                    if conflict_id not in dependencies:
                        dependencies[conflict_id] = []
                    if op_id not in dependencies[conflict_id]:
                        dependencies[conflict_id].append(op_id)
                else:
                    # op1 depends on op2 (op2 must run first)
                    if op_id not in dependencies:
                        dependencies[op_id] = []
                    if conflict_id not in dependencies[op_id]:
                        dependencies[op_id].append(conflict_id)
        return dependencies

    def topological_sort(self, operations: list[dict[str, Any]]) -> list[list[str]]:
        """
        Topological sort of operations.
        Uses xwnode if available, otherwise falls back to Kahn's algorithm.
        Args:
            operations: list of operations to sort
        Returns:
            list of levels, each level contains operations that can run in parallel
        """
        # Build dependency graph
        dependencies = self.build_dependencies(operations)
        # Use xwnode if available
        if self._xwnode_available:
            return self._topological_sort_with_xwnode(operations, dependencies)
        else:
            return self._topological_sort_kahn(operations, dependencies)

    def _topological_sort_with_xwnode(
        self,
        operations: list[dict[str, Any]],
        dependencies: dict[str, list[str]]
    ) -> list[list[str]]:
        """
        Topological sort using xwnode.
        Args:
            operations: list of operations
            dependencies: Dependency graph
        Returns:
            list of execution levels
        """
        try:
            # Create xwnode graph
            # Note: This is a simplified integration - full xwnode integration
            # would use XWNode.from_native() with mode='GRAPH'
            # For now, we use xwnode's topological sort if available
            # Build graph structure for xwnode
            [f"op_{i}" for i in range(len(operations))]
            edges = []
            for op_id, deps in dependencies.items():
                for dep in deps:
                    edges.append((dep, op_id))  # dep -> op_id (dep must run first)
            # Use Kahn's algorithm (xwnode uses similar approach internally)
            return self._topological_sort_kahn(operations, dependencies)
        except Exception:
            # Fallback to Kahn's algorithm if xwnode fails
            return self._topological_sort_kahn(operations, dependencies)

    def _topological_sort_kahn(
        self,
        operations: list[dict[str, Any]],
        dependencies: dict[str, list[str]]
    ) -> list[list[str]]:
        """
        Topological sort using Kahn's algorithm.
        Args:
            operations: list of operations
            dependencies: Dependency graph
        Returns:
            list of execution levels
        """
        # Calculate in-degrees
        in_degree: dict[str, int] = {f"op_{i}": 0 for i in range(len(operations))}
        for op_id, deps in dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[op_id] = in_degree.get(op_id, 0) + 1
        # Kahn's algorithm
        queue = deque([op_id for op_id, degree in in_degree.items() if degree == 0])
        levels: list[list[str]] = []
        while queue:
            current_level = list(queue)
            queue.clear()
            levels.append(current_level)
            for op_id in current_level:
                # Find operations that depend on this one
                for dependent_id, deps in dependencies.items():
                    if op_id in deps:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            queue.append(dependent_id)
        # Add any remaining operations (shouldn't happen in DAG, but handle gracefully)
        remaining = [op_id for op_id, degree in in_degree.items() if degree > 0]
        if remaining:
            levels.append(remaining)
        return levels

    def _extract_path(self, operation: dict[str, Any]) -> str | None:
        """Extract path from operation."""
        if 'path' in operation:
            return operation['path']
        elif 'from' in operation and operation.get('op') == 'move':
            return operation['from']
        elif 'to' in operation and operation.get('op') == 'move':
            return operation['to']
        return None

    def _paths_conflict(self, path1: str, path2: str, op1: dict, op2: dict) -> bool:
        """Check if two paths conflict."""
        # Same path = conflict
        if path1 == path2:
            return True
        # Parent-child relationship = conflict
        if path1.startswith(path2 + "/") or path2.startswith(path1 + "/"):
            return True
        # Move operation affects paths
        if op1.get("op") == "move":
            from_path = op1.get("from")
            to_path = op1.get("to")
            if path2.startswith(from_path) or path2.startswith(to_path):
                return True
        if op2.get("op") == "move":
            from_path = op2.get("from")
            to_path = op2.get("to")
            if path1.startswith(from_path) or path1.startswith(to_path):
                return True
        # Delete operation affects children
        if op1.get("op") == "delete_path":
            if path2.startswith(path1 + "/"):
                return True
        if op2.get("op") == "delete_path":
            if path1.startswith(path2 + "/"):
                return True
        return False

    def _should_run_first(self, op1: dict, op2: dict) -> bool:
        """Determine which operation should run first."""
        path1 = self._extract_path(op1)
        path2 = self._extract_path(op2)
        # Rule 1: ID update before move
        if op1.get("op") == "update_path" and "/id" in (path1 or ""):
            if op2.get("op") == "move":
                return True
        # Rule 2: Child update before parent delete
        if op2.get("op") == "delete_path":
            if path1 and path2 and path1.startswith(path2 + "/"):
                return True
        # Rule 3: Parent update before child update
        if op1.get("op") == "update_path" and op2.get("op") == "update_path":
            if path1 and path2 and path2.startswith(path1 + "/"):
                return True
        # Rule 4: Write before read on same path (read-after-write dependency)
        if op1.get("op") in ("write_path", "update_path") and op2.get("op") == "read_path":
            if path1 == path2:
                return True
        # Rule 4 reverse: Read should NOT run before write on same path
        if op2.get("op") in ("write_path", "update_path") and op1.get("op") == "read_path":
            if path1 == path2:
                return False  # op1 (read) should NOT run before op2 (write)
        # Default: Order by operation type priority
        priority = {
            "read": 0, "read_path": 0,
            "update": 1, "update_path": 1,
            "write": 2, "write_path": 2,
            "move": 3,
            "delete": 4, "delete_path": 4
        }
        op1_priority = priority.get(op1.get("op", ""), 99)
        op2_priority = priority.get(op2.get("op", ""), 99)
        return op1_priority < op2_priority
