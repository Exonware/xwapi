"""
Integration tests for xwsystem-facing lazy behavior.

These scenarios validate the user's requirement:
- xwlazy enabled -> lazy install + lazy loading policy for xwsystem
- xwlazy disabled -> no lazy install interception
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.xwlazy_integration

project_root = Path(__file__).resolve().parents[3]
src_root = project_root / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from exonware.xwlazy import auto_enable_lazy, uninstall_global_import_hook


def _reset_singleton_state() -> None:
    uninstall_global_import_hook()
    globals_dict = auto_enable_lazy.__globals__
    if "_instance" in globals_dict:
        globals_dict["_instance"] = None


def _write_pyproject(path: Path, *, enable_install: bool, enable_loading: bool) -> None:
    path.write_text(
        "\n".join(
            [
                "[project]",
                "name = 'demo'",
                "version = '0.0.0'",
                "",
                "[tool.xwlazy]",
                f"enable_lazy_install = {'true' if enable_install else 'false'}",
                f"enable_lazy_loading = {'true' if enable_loading else 'false'}",
                "",
            ]
        ),
        encoding="utf-8",
    )


class TestXWSystemExternalLazyBehavior:
    def teardown_method(self):
        _reset_singleton_state()

    def test_xwsystem_policy_becomes_lazy_when_both_flags_enabled(self, tmp_path: Path):
        _write_pyproject(
            tmp_path / "pyproject.toml",
            enable_install=True,
            enable_loading=True,
        )
        guardian = auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))
        policy = guardian.package_policies.get("exonware.xwsystem")

        assert policy is not None
        assert policy["enabled"] is True
        assert policy["mode"] == "lazy"
        assert policy["strategy"] == "smart"

    def test_external_missing_dependency_uses_lazy_loader_when_enabled(self, tmp_path: Path):
        _write_pyproject(
            tmp_path / "pyproject.toml",
            enable_install=True,
            enable_loading=True,
        )
        guardian = auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))

        # Use a guaranteed-missing import name to exercise lazy external path.
        spec = guardian.find_spec("external_pkg_that_does_not_exist_for_xwsystem", None)

        assert spec is not None
        assert spec.loader is not None
        assert spec.loader.__class__.__name__ == "LazyLoader"

    def test_external_missing_dependency_not_intercepted_when_install_disabled(self, tmp_path: Path):
        _write_pyproject(
            tmp_path / "pyproject.toml",
            enable_install=False,
            enable_loading=True,
        )
        guardian = auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))

        spec = guardian.find_spec("external_pkg_that_does_not_exist_for_xwsystem", None)

        assert spec is None
