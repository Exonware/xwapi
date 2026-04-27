#exonware/xwapi/src/exonware/xwapi/scrapping/dedup.py
"""
Stable dedup keys for normalized records.

The framework can't prescribe the dedup strategy (different domains have
different identity rules), but it ships a sensible default helper that
hashes a tuple of stable fields. Persistence implementations that want
finer control can compute their own keys.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
import hashlib
from typing import Any, Iterable, Mapping


def compute_dedup_key(record: Mapping[str, Any], fields: Iterable[str]) -> str:
    """
    SHA-1 hex of the concatenated, normalized values for the named fields.

    Missing or None fields contribute the literal token `<missing>`. Strings are
    casefolded so trivial casing differences don't fragment dedup. Numbers are
    rounded to 6 decimals to absorb float jitter from different sources.
    """
    parts: list[str] = []
    for field in fields:
        value = record.get(field)
        if value is None:
            parts.append("<missing>")
            continue
        if isinstance(value, str):
            parts.append(value.strip().casefold())
        elif isinstance(value, float):
            parts.append(f"{value:.6f}")
        else:
            parts.append(str(value))
    payload = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()
