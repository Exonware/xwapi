"""
Generic AST utility functions for ParseNode trees.
"""

from typing import Any, Optional, Iterator, Callable

from .syntax_tree import ParseNode

MAX_AST_DEPTH = 1000


def find_node_by_type(ast: ParseNode, node_type: str) -> Optional[ParseNode]:
    if not ast:
        return None
    if ast.type == node_type:
        return ast
    if hasattr(ast, "children") and ast.children:
        for child in ast.children:
            result = find_node_by_type(child, node_type)
            if result:
                return result
    return None


def find_all_nodes_by_type(
    ast: ParseNode, node_type: str, max_depth: int = MAX_AST_DEPTH
) -> list[ParseNode]:
    results = []

    def _search(node: ParseNode, depth: int):
        if depth > max_depth or not node:
            return
        if node.type == node_type:
            results.append(node)
        if hasattr(node, "children") and node.children:
            for child in node.children:
                _search(child, depth + 1)

    _search(ast, 0)
    return results


def extract_node_value(ast: ParseNode) -> Any:
    if not ast:
        return None
    if hasattr(ast, "value") and ast.value is not None:
        return ast.value
    if ast.type == "terminal":
        return ast.value if hasattr(ast, "value") else None
    if hasattr(ast, "children") and ast.children:
        if len(ast.children) == 1:
            return extract_node_value(ast.children[0])
        values = []
        for child in ast.children:
            val = extract_node_value(child)
            if val is not None:
                values.append(val)
        return values if values else None
    return None


def traverse_depth_first(
    ast: ParseNode, max_depth: int = MAX_AST_DEPTH
) -> Iterator[ParseNode]:
    def _traverse(node: ParseNode, depth: int):
        if depth > max_depth or not node:
            return
        yield node
        if hasattr(node, "children") and node.children:
            for child in node.children:
                yield from _traverse(child, depth + 1)

    yield from _traverse(ast, 0)


def traverse_breadth_first(ast: ParseNode) -> Iterator[ParseNode]:
    if not ast:
        return
    queue = [ast]
    while queue:
        node = queue.pop(0)
        yield node
        if hasattr(node, "children") and node.children:
            queue.extend(node.children)


def find_parent(ast: ParseNode, target_node: ParseNode) -> Optional[ParseNode]:
    if not ast or not target_node:
        return None
    if hasattr(ast, "children") and ast.children:
        for child in ast.children:
            if child is target_node:
                return ast
            parent = find_parent(child, target_node)
            if parent:
                return parent
    return None


def get_node_text(ast: ParseNode) -> str:
    if not ast:
        return ""
    if ast.type == "terminal" or not hasattr(ast, "children"):
        return str(ast.value) if ast.value is not None else ""
    parts = []
    for child in ast.children:
        text = get_node_text(child)
        if text:
            parts.append(text)
    return " ".join(parts)


def ast_to_dict(ast: ParseNode, max_depth: int = 10) -> dict[str, Any]:
    if not ast or max_depth <= 0:
        return {}
    result = {
        "type": ast.type,
        "value": ast.value if hasattr(ast, "value") else None,
        "metadata": ast.metadata if hasattr(ast, "metadata") else {},
    }
    if hasattr(ast, "children") and ast.children:
        result["children"] = [ast_to_dict(child, max_depth - 1) for child in ast.children]
    return result


def count_nodes(ast: ParseNode) -> int:
    if not ast:
        return 0
    count = 1
    if hasattr(ast, "children") and ast.children:
        for child in ast.children:
            count += count_nodes(child)
    return count


def get_ast_depth(ast: ParseNode) -> int:
    if not ast:
        return 0
    if not hasattr(ast, "children") or not ast.children:
        return 0
    max_child_depth = 0
    for child in ast.children:
        max_child_depth = max(max_child_depth, get_ast_depth(child))
    return 1 + max_child_depth


def collect_terminals(ast: ParseNode) -> list[ParseNode]:
    terminals = []
    for node in traverse_depth_first(ast):
        if node.type == "terminal" or not hasattr(node, "children") or not node.children:
            terminals.append(node)
    return terminals


def extract_text_from_subtree(ast: ParseNode, separator: str = " ") -> str:
    terminals = collect_terminals(ast)
    texts = [str(t.value) for t in terminals if t.value is not None]
    return separator.join(texts)


def find_nodes_by_predicate(
    ast: ParseNode,
    predicate: Callable[[ParseNode], bool],
    max_depth: int = MAX_AST_DEPTH,
) -> list[ParseNode]:
    results = []

    def _search(node: ParseNode, depth: int):
        if depth > max_depth or not node:
            return
        if predicate(node):
            results.append(node)
        if hasattr(node, "children") and node.children:
            for child in node.children:
                _search(child, depth + 1)

    _search(ast, 0)
    return results


def extract_keyword_node(ast: ParseNode, keyword: str) -> Optional[ParseNode]:
    keyword_upper = keyword.upper()
    for node in traverse_depth_first(ast):
        if node.value and str(node.value).upper() == keyword_upper:
            parent = find_parent(ast, node)
            if parent and hasattr(parent, "children"):
                try:
                    node_idx = parent.children.index(node)
                    if node_idx + 1 < len(parent.children):
                        return parent.children[node_idx + 1]
                except (ValueError, IndexError):
                    pass
    return None


def has_child_of_type(ast: ParseNode, node_type: str) -> bool:
    if not ast or not hasattr(ast, "children"):
        return False
    return any(child.type == node_type for child in ast.children)


def get_child_by_type(ast: ParseNode, node_type: str) -> Optional[ParseNode]:
    if not ast or not hasattr(ast, "children"):
        return None
    for child in ast.children:
        if child.type == node_type:
            return child
    return None


def get_children_by_type(ast: ParseNode, node_type: str) -> list[ParseNode]:
    if not ast or not hasattr(ast, "children"):
        return []
    return [child for child in ast.children if child.type == node_type]


def is_terminal(node: ParseNode) -> bool:
    return node.type == "terminal" or not hasattr(node, "children") or not node.children


def get_node_at_path(ast: ParseNode, path: list[str]) -> Optional[ParseNode]:
    current = ast
    for node_type in path:
        if not current:
            return None
        current = get_child_by_type(current, node_type)
    return current


def extract_identifier_chain(ast: ParseNode) -> list[str]:
    identifiers = []
    for node in traverse_depth_first(ast):
        if node.type.lower() in ("identifier", "ncname", "name"):
            value = extract_node_value(node)
            if value and isinstance(value, str):
                identifiers.append(value)
    return identifiers


def print_ast_tree(ast: ParseNode, indent: int = 0, max_depth: int = 10):
    if not ast or indent > max_depth:
        return
    prefix = "  " * indent
    value_str = f": {ast.value}" if ast.value is not None else ""
    print(f"{prefix}{ast.type}{value_str}")
    if hasattr(ast, "children") and ast.children:
        for child in ast.children:
            print_ast_tree(child, indent + 1, max_depth)


__all__ = [
    "MAX_AST_DEPTH",
    "find_node_by_type",
    "find_all_nodes_by_type",
    "extract_node_value",
    "traverse_depth_first",
    "traverse_breadth_first",
    "find_parent",
    "get_node_text",
    "ast_to_dict",
    "count_nodes",
    "get_ast_depth",
    "collect_terminals",
    "extract_text_from_subtree",
    "find_nodes_by_predicate",
    "extract_keyword_node",
    "has_child_of_type",
    "get_child_by_type",
    "get_children_by_type",
    "is_terminal",
    "get_node_at_path",
    "extract_identifier_chain",
    "print_ast_tree",
]

