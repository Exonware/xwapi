"""
Query format auto-detection utilities.
"""

import re
from collections import defaultdict
from typing import Optional


class QueryFormatDetector:
    """Multi-stage query format detector."""

    def __init__(self, confidence_threshold: float = 0.8):
        self._threshold = confidence_threshold
        self._keyword_weights = self._build_keyword_weights()
        self._pattern_matchers = self._build_pattern_matchers()

    def _build_keyword_weights(self) -> dict[str, dict[str, int]]:
        return {
            "SQL": {"SELECT": 10, "FROM": 10, "WHERE": 8, "INSERT": 10, "UPDATE": 10, "DELETE": 10},
            "GraphQL": {"query": 10, "mutation": 10, "subscription": 10, "fragment": 9},
            "Cypher": {"MATCH": 10, "RETURN": 10, "MERGE": 9, "UNWIND": 9, "OPTIONAL": 8, "CREATE": 9},
            "SPARQL": {"PREFIX": 10, "CONSTRUCT": 10, "DESCRIBE": 10, "ASK": 10, "FILTER": 8},
            "Gremlin": {"V": 9, "E": 9, "hasLabel": 9, "repeat": 8, "emit": 8},
            "JMESPath": {"sort_by": 9, "starts_with": 8, "ends_with": 8, "flatten": 8},
            "MongoDB": {"$match": 10, "$group": 10, "$lookup": 10, "find": 9, "aggregate": 9},
        }

    def _build_pattern_matchers(self) -> dict[str, list[tuple[re.Pattern, float]]]:
        return {
            "SQL": [
                (re.compile(r"\bSELECT\s+.+\s+FROM\s+", re.IGNORECASE), 0.95),
                (re.compile(r"\bINSERT\s+INTO\s+", re.IGNORECASE), 0.95),
                (re.compile(r"\bUPDATE\s+.+\s+SET\s+", re.IGNORECASE), 0.95),
                (re.compile(r"\bDELETE\s+FROM\s+", re.IGNORECASE), 0.95),
            ],
            "GraphQL": [
                (re.compile(r"^\s*query\s+\w+\s*\{", re.IGNORECASE), 0.95),
                (re.compile(r"^\s*mutation\s+\w+\s*\{", re.IGNORECASE), 0.95),
                (re.compile(r"^\s*subscription\s+\w+\s*\{", re.IGNORECASE), 0.95),
            ],
            "Cypher": [
                (re.compile(r"\bMATCH\s+\([^)]*\)", re.IGNORECASE), 0.95),
                (re.compile(r"\([^)]*\)-\[[^\]]*\]->\([^)]*\)", re.IGNORECASE), 0.95),
                (re.compile(r"^\s*CREATE\s+\([^)]*\)", re.IGNORECASE), 0.95),
            ],
            "SPARQL": [
                (re.compile(r"^\s*PREFIX\s+\w+:\s*<", re.IGNORECASE), 0.95),
                (re.compile(r"\bASK\s+\{", re.IGNORECASE), 0.95),
            ],
            "Gremlin": [
                (re.compile(r"g\.V\(\)", re.IGNORECASE), 0.95),
                (re.compile(r"g\.E\(\)", re.IGNORECASE), 0.95),
            ],
            "JMESPath": [
                (re.compile(r"\[\?\s*.+\s*\]", re.IGNORECASE), 0.90),
                (re.compile(r"sort_by\(", re.IGNORECASE), 0.90),
            ],
            "JSONPath": [(re.compile(r"^\$\.", re.IGNORECASE), 0.95)],
            "XPath": [(re.compile(r"^//", re.IGNORECASE), 0.90), (re.compile(r"^/", re.IGNORECASE), 0.85)],
            "MongoDB": [
                (re.compile(r"\$match\s*:", re.IGNORECASE), 0.95),
                (re.compile(r"\.find\(", re.IGNORECASE), 0.90),
            ],
        }

    def detect_format(self, query: str) -> tuple[str, float]:
        if not query or not isinstance(query, str):
            return "SQL", 0.5
        query = query.strip()
        quick_result = self._quick_keyword_check(query)
        if quick_result and quick_result[1] >= 0.85:
            return quick_result
        pattern_scores = self._pattern_matching_detection(query)
        keyword_scores = self._keyword_frequency_detection(query)
        combined_scores = self._combine_scores(pattern_scores, keyword_scores)
        if not combined_scores:
            return "SQL", 0.5
        best_format = max(combined_scores, key=combined_scores.get)
        return best_format, combined_scores[best_format]

    def _quick_keyword_check(self, query: str) -> Optional[tuple[str, float]]:
        query_upper = query.upper()
        if "SELECT" in query_upper and "FROM" in query_upper:
            return "SQL", 0.95
        if query_upper.startswith(("INSERT ", "UPDATE ", "DELETE FROM")):
            return "SQL", 0.95
        if "MATCH" in query_upper and "RETURN" in query_upper:
            return "Cypher", 0.95
        if query_upper.startswith("CREATE (") and ":" in query and "{" in query:
            # Distinguish Cypher node creation from SQL CREATE statements.
            return "Cypher", 0.95
        if query.strip().startswith(("query ", "mutation ", "subscription ")):
            return "GraphQL", 0.95
        if query_upper.startswith("PREFIX ") or "CONSTRUCT {" in query_upper:
            return "SPARQL", 0.95
        if query.strip().startswith("g.V(") or query.strip().startswith("g.E("):
            return "Gremlin", 0.95
        if query.strip().startswith("db.") and (".find(" in query or ".aggregate(" in query):
            return "MongoDB", 0.95
        if query.startswith("$."):
            return "JSONPath", 0.90
        if query.startswith("//"):
            return "XPath", 0.90
        if query.startswith("/") and not query.startswith("/http"):
            return "XPath", 0.85
        return None

    def _pattern_matching_detection(self, query: str) -> dict[str, float]:
        scores = {}
        for format_name, patterns in self._pattern_matchers.items():
            max_confidence = 0.0
            for pattern, confidence_weight in patterns:
                if pattern.search(query):
                    max_confidence = max(max_confidence, confidence_weight)
            if max_confidence > 0:
                scores[format_name] = max_confidence
        return scores

    def _keyword_frequency_detection(self, query: str) -> dict[str, float]:
        scores = defaultdict(float)
        tokens = set(re.findall(r"\$?[a-zA-Z_]\w*\b", query))
        for format_name, keywords in self._keyword_weights.items():
            keyword_lookup = {key.upper(): weight for key, weight in keywords.items()}
            for token in tokens:
                token_upper = token.upper()
                if token_upper in keyword_lookup:
                    scores[format_name] += keyword_lookup[token_upper]
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                for format_name in scores:
                    scores[format_name] = scores[format_name] / max_score
        return dict(scores)

    def _combine_scores(
        self, pattern_scores: dict[str, float], keyword_scores: dict[str, float]
    ) -> dict[str, float]:
        combined = defaultdict(float)
        all_formats = set(pattern_scores.keys()) | set(keyword_scores.keys())
        for format_name in all_formats:
            pattern_score = pattern_scores.get(format_name, 0.0)
            keyword_score = keyword_scores.get(format_name, 0.0)
            has_pattern = format_name in pattern_scores
            has_keyword = format_name in keyword_scores
            if has_pattern and has_keyword:
                combined[format_name] = (pattern_score * 0.6) + (keyword_score * 0.4)
            elif has_pattern:
                combined[format_name] = pattern_score
            else:
                combined[format_name] = keyword_score
        return dict(combined)

    def detect_format_with_candidates(self, query: str) -> dict[str, float]:
        pattern_scores = self._pattern_matching_detection(query)
        keyword_scores = self._keyword_frequency_detection(query)
        combined = self._combine_scores(pattern_scores, keyword_scores)
        return dict(sorted(combined.items(), key=lambda x: x[1], reverse=True))

    def is_confident(self, query: str) -> bool:
        _, confidence = self.detect_format(query)
        return confidence >= self._threshold


_global_detector: Optional[QueryFormatDetector] = None


def detect_query_format(query: str) -> tuple[str, float]:
    global _global_detector
    if _global_detector is None:
        _global_detector = QueryFormatDetector()
    return _global_detector.detect_format(query)


__all__ = ["QueryFormatDetector", "detect_query_format"]

