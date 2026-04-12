#!/usr/bin/env python3

from exonware.xwapi.common.text_reply import cap_sequence


def test_cap_sequence_basic() -> None:
    shown, total, overflow = cap_sequence(["a", "b", "c"], cap=2)
    assert shown == ["a", "b"]
    assert total == 3
    assert overflow == 1


def test_cap_sequence_exact_cap() -> None:
    shown, total, overflow = cap_sequence(["x"], cap=3)
    assert shown == ["x"]
    assert total == 1
    assert overflow == 0


def test_cap_sequence_zero_cap() -> None:
    shown, total, overflow = cap_sequence(["a", "b"], cap=0)
    assert shown == []
    assert total == 2
    assert overflow == 2
