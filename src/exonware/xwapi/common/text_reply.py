#!/usr/bin/env python3
"""
Plain-text reply building blocks for any surface (bot replies, CLI, API summaries).

Kept free of chat/transport specifics so callers can wrap results in HTML/Markdown/etc.
"""

from __future__ import annotations

from collections.abc import Sequence


def cap_sequence(items: Sequence[str], *, cap: int) -> tuple[list[str], int, int]:
    """
    Return ``(shown, total, overflow)`` where ``overflow = max(0, total - cap)``.

    If ``cap <= 0``, ``shown`` is empty and ``overflow`` equals ``total``.
    """
    seq = list(items)
    total = len(seq)
    if cap <= 0:
        return [], total, total
    shown = seq[:cap]
    overflow = max(0, total - cap)
    return shown, total, overflow
