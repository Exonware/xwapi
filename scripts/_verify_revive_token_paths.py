#!/usr/bin/env python3
"""One-off: verify revive token path resolution (dir_data + case-insensitive auth dir)."""
from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

# Repo src first so we exercise the working tree, not an older install.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from exonware.xwapi import XWApiAgent  # noqa: E402


class ProbeAgent(XWApiAgent):
    """Minimal agent; skip heavy auto_discover of engines."""

    def __init__(self) -> None:
        super().__init__(name="probe", auto_discover=False)


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="xwapi-revive-verify-"))
    try:
        # Token only under RU-KARIZMA; config key is ru_karizma (case mismatch).
        tok_dir = root / "xwauth" / "liveme" / "RU-KARIZMA"
        tok_dir.mkdir(parents=True)
        (tok_dir / "token.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
        cfg = root / "xwauth" / "liveme" / "ru_karizma" / "config.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(json.dumps({"client_id": "test"}), encoding="utf-8")

        agent = ProbeAgent()
        agent.dir_data = str(root)

        paths = agent._token_json_paths("liveme", "ru_karizma")
        found = [p for p in paths if p.is_file()]
        assert found, f"expected token file in paths, got {paths}"
        print("token paths OK:", found[0])

        lines = agent._revival_lines_probe_token("liveme", "ru_karizma")
        text = "\n".join(lines)
        assert "OK" in text and "token" in text.lower(), text
        print("probe_token liveme OK")

        lines_g = agent._revival_lines_probe_token("google", "kta")
        gtxt = "\n".join(lines_g).lower()
        assert "service-account" in gtxt or "config.json" in gtxt, lines_g
        print("probe_token google OK")

        agent2 = ProbeAgent()
        agent2.dir_data = str(root)
        # revive_auths is @XWAction with roles; unwrap for programmatic test.
        result = inspect.unwrap(agent2.revive_auths)(agent2, base_path="")
        assert result.get("success"), result
        assert result.get("reloaded_count", 0) >= 1, result
        assert "liveme" in (result.get("auths") or {}), result
        assert "ru_karizma" in result["auths"]["liveme"], result
        report = result.get("user_report") or ""
        assert "RU-KARIZMA" in report or "token" in report.lower(), report[:500]
        assert "no token file yet" not in report.lower() or "google" in report.lower(), report
        # Live.me block should mention saved token, not "no token file yet" for ru_karizma
        assert "saved token file" in report.lower(), report
        print("revive_auths OK (default base uses dir_data)")
        print("--- user_report excerpt ---")
        print("\n".join(report.splitlines()[:25]))
        return 0
    finally:
        import shutil

        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
