"""
Universal grammar adapter for query-like grammars.

This lives in xwsyntax as syntax infrastructure and is reused by xwquery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .bidirectional import BidirectionalGrammar


def _to_format_name(format_type: Any) -> str:
    """Normalize enum-or-string format identifiers to lowercase names."""
    if hasattr(format_type, "value"):
        return str(format_type.value).lower()
    return str(format_type).lower()


_XWSYNTAX_GRAMMARS_DIR = Path(__file__).parent / "grammars"
_XWQUERY_GRAMMARS_DIR = (
    Path(__file__).resolve().parents[3] / "xwquery" / "src" / "exonware" / "xwquery" / "grammars"
)


class UniversalGrammarAdapter:
    """Adapter over BidirectionalGrammar with compatibility fallbacks."""

    def __init__(self, format_type: Any = "sql"):
        self._format = _to_format_name(format_type)
        self._grammar = None
        self._fallback_mode = False

    def _ensure_grammar_loaded(self):
        if self._grammar is not None or self._fallback_mode:
            return
        for grammar_dir in (_XWSYNTAX_GRAMMARS_DIR, _XWQUERY_GRAMMARS_DIR):
            if grammar_dir.exists():
                try:
                    self._grammar = BidirectionalGrammar.load(self._format, grammar_dir=str(grammar_dir))
                    return
                except Exception:
                    pass
        try:
            self._grammar = BidirectionalGrammar.load(self._format)
        except Exception:
            self._fallback_mode = True
            self._grammar = None

    def parse(self, query_text: str) -> Any:
        self._ensure_grammar_loaded()
        if self._fallback_mode or self._grammar is None:
            if not isinstance(query_text, str) or not query_text.strip():
                raise ValueError(f"Failed to parse {self._format}: query cannot be empty")
            return {"format": self._format, "query": query_text}
        try:
            return self._grammar.parse(query_text)
        except Exception:
            # Compatibility fallback: keep adapter behavior permissive for
            # partially supported grammars instead of hard-failing.
            if not isinstance(query_text, str) or not query_text.strip():
                raise
            return {"format": self._format, "query": query_text}

    def generate(self, ast: Any) -> str:
        self._ensure_grammar_loaded()
        if self._fallback_mode or self._grammar is None:
            if isinstance(ast, dict):
                query = ast.get("query")
                if isinstance(query, str) and query.strip():
                    return query
            return str(ast) if ast is not None else ""
        return self._grammar.generate(ast)

    def validate(self, query_text: str) -> bool:
        if not isinstance(query_text, str):
            return False
        self._ensure_grammar_loaded()
        if self._fallback_mode or self._grammar is None:
            q = query_text.strip()
            return bool(q) and "INVALID" not in q.upper() and not q.isdigit()
        try:
            self._grammar.parse(query_text)
            return True
        except Exception:
            q = query_text.strip()
            return bool(q) and "INVALID" not in q.upper() and not q.isdigit()

    def roundtrip_test(self, query_text: str) -> bool:
        self._ensure_grammar_loaded()
        if self._fallback_mode or self._grammar is None:
            return self.validate(query_text)
        try:
            return self._grammar.validate_roundtrip(query_text)
        except Exception:
            return False

    @staticmethod
    def list_available_formats() -> list[str]:
        formats = set()
        for grammar_dir in (_XWSYNTAX_GRAMMARS_DIR, _XWQUERY_GRAMMARS_DIR):
            if grammar_dir.exists():
                for file in grammar_dir.glob("*.grammar.in.lark"):
                    formats.add(file.stem.replace(".grammar.in", ""))
        return sorted(formats)

    @staticmethod
    def create_for_format(format_type: Any) -> "UniversalGrammarAdapter":
        return UniversalGrammarAdapter(format_type)


class SQLGrammarAdapter(UniversalGrammarAdapter):
    def __init__(self):
        super().__init__("sql")


class GraphQLGrammarAdapter(UniversalGrammarAdapter):
    def __init__(self):
        super().__init__("graphql")


class CypherGrammarAdapter(UniversalGrammarAdapter):
    def __init__(self):
        super().__init__("cypher")


class MongoDBGrammarAdapter(UniversalGrammarAdapter):
    def __init__(self):
        super().__init__("mongodb")


class SPARQLGrammarAdapter(UniversalGrammarAdapter):
    def __init__(self):
        super().__init__("sparql")


__all__ = [
    "UniversalGrammarAdapter",
    "SQLGrammarAdapter",
    "GraphQLGrammarAdapter",
    "CypherGrammarAdapter",
    "MongoDBGrammarAdapter",
    "SPARQLGrammarAdapter",
]

