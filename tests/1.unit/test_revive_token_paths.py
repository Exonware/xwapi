# exonware/xwapi/tests/1.unit/test_revive_token_paths.py
"""Regression: /revive token discovery (dir_data, case, hyphen vs underscore)."""

from __future__ import annotations

import inspect
import json

import pytest

from exonware.xwapi import XWApiAgent


class _ProbeAgent(XWApiAgent):
    def __init__(self) -> None:
        super().__init__(name="probe", auto_discover=False)


@pytest.mark.xwapi_unit
def test_token_json_paths_matches_hyphen_dir_for_underscore_auth(tmp_path) -> None:
    """Config auth ru_karizma vs token dir RU-KARIZMA (LiveMe saves agency display name)."""
    root = tmp_path
    (root / "xwauth" / "liveme" / "RU-KARIZMA").mkdir(parents=True)
    (root / "xwauth" / "liveme" / "RU-KARIZMA" / "token.json").write_text(
        json.dumps({"ok": True}), encoding="utf-8"
    )
    agent = _ProbeAgent()
    agent.dir_data = str(root)
    paths = agent._token_json_paths("liveme", "ru_karizma")
    assert any(p.is_file() for p in paths), paths


@pytest.mark.xwapi_unit
def test_revive_auths_uses_dir_data_when_base_path_empty(tmp_path) -> None:
    """Empty base_path should scan dir_data/xwauth, not only cwd .data/xwauth."""
    root = tmp_path
    cfg = root / "xwauth" / "liveme" / "ru_karizma" / "config.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(json.dumps({"client_id": "t"}), encoding="utf-8")
    (root / "xwauth" / "liveme" / "RU-KARIZMA").mkdir(parents=True)
    (root / "xwauth" / "liveme" / "RU-KARIZMA" / "token.json").write_text(
        json.dumps({"x": 1}), encoding="utf-8"
    )

    agent = _ProbeAgent()
    agent.dir_data = str(root)
    result = inspect.unwrap(agent.revive_auths)(agent, base_path="")
    assert result.get("success")
    assert result.get("reloaded_count", 0) >= 1
    report = result.get("user_report") or ""
    assert "saved token file" in report.lower()
    assert "RU-KARIZMA" in report or "token.json" in report
