#exonware/xwapi/tests/1.unit/test_common_cap_sequence.py
"""
Unit tests for xwapi common text_reply — cap_sequence helper.
"""

from __future__ import annotations

import pytest


@pytest.mark.xwapi_unit
class TestCapSequence:

    def test_cap_within_limit(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence(["a", "b", "c"], cap=5)
        assert shown == ["a", "b", "c"]
        assert total == 3
        assert overflow == 0

    def test_cap_exact_limit(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence(["a", "b"], cap=2)
        assert shown == ["a", "b"]
        assert total == 2
        assert overflow == 0

    def test_cap_overflow(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence(["a", "b", "c", "d"], cap=2)
        assert shown == ["a", "b"]
        assert total == 4
        assert overflow == 2

    def test_cap_zero(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence(["a", "b"], cap=0)
        assert shown == []
        assert total == 2
        assert overflow == 2

    def test_cap_negative(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence(["a"], cap=-1)
        assert shown == []
        assert overflow == 1

    def test_empty_input(self):
        from exonware.xwapi.common.text_reply import cap_sequence
        shown, total, overflow = cap_sequence([], cap=10)
        assert shown == []
        assert total == 0
        assert overflow == 0
