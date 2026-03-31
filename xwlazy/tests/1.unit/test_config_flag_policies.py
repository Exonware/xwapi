"""
Unit tests for config-driven lazy behavior.

These tests validate [tool.xwlazy] switches:
- enable_lazy_install
- enable_lazy_loading
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.xwlazy_unit

project_root = Path(__file__).resolve().parents[2]
src_root = project_root / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from exonware.xwlazy import auto_enable_lazy, hook, uninstall_global_import_hook, resolve_package_lazy_flags


def _reset_singleton_state() -> None:
    uninstall_global_import_hook()
    # Reset the module-level singleton used by hook()/auto_enable_lazy().
    globals_dict = hook.__globals__
    if "_instance" in globals_dict:
        globals_dict["_instance"] = None


class TestConfigFlagPolicies:
    def teardown_method(self):
        _reset_singleton_state()

    def test_resolve_package_lazy_flags_reads_tool_section(self, tmp_path: Path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "demo"
version = "0.0.0"

[tool.xwlazy]
enable_lazy_install = false
enable_lazy_loading = true
""".strip(),
            encoding="utf-8",
        )
        nested = tmp_path / "src" / "pkg"
        nested.mkdir(parents=True, exist_ok=True)

        flags = resolve_package_lazy_flags(nested)

        assert flags["enable_lazy_install"] is False
        assert flags["enable_lazy_loading"] is True
        assert flags["root_dir"] == str(tmp_path.resolve())

    def test_hook_default_enabled_follows_enable_lazy_install(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "demo"
version = "0.0.0"

[tool.xwlazy]
enable_lazy_install = false
""".strip(),
            encoding="utf-8",
        )

        manager = hook(root=str(tmp_path), default_enabled=True, enable_global_hook=False)

        assert manager.default_enabled is False
        assert manager._get_policy("example")["enabled"] is False

    def test_smart_mode_uses_blocking_when_lazy_loading_disabled(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "demo"
version = "0.0.0"

[tool.xwlazy]
enable_lazy_loading = false
""".strip(),
            encoding="utf-8",
        )

        manager = auto_enable_lazy("demo_pkg", mode="smart", root=str(tmp_path))

        policy = manager.package_policies["demo_pkg"]
        assert policy["strategy"] == "smart"
        assert policy["mode"] == "blocking"

    def test_smart_mode_remains_lazy_when_lazy_loading_enabled(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "demo"
version = "0.0.0"

[tool.xwlazy]
enable_lazy_loading = true
""".strip(),
            encoding="utf-8",
        )

        manager = auto_enable_lazy("demo_pkg", mode="smart", root=str(tmp_path))

        policy = manager.package_policies["demo_pkg"]
        assert policy["strategy"] == "smart"
        assert policy["mode"] == "lazy"

    def test_smart_mode_keeps_legacy_default_when_flag_missing(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "demo"
version = "0.0.0"
""".strip(),
            encoding="utf-8",
        )

        manager = auto_enable_lazy("demo_pkg", mode="smart", root=str(tmp_path))

        policy = manager.package_policies["demo_pkg"]
        assert policy["strategy"] == "smart"
        assert policy["mode"] == "lazy"

    def test_stdlib_modules_never_resolve_to_install_targets(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text(
            """
[project]
name = "demo"
version = "0.0.0"
""".strip(),
            encoding="utf-8",
        )

        manager = hook(root=str(tmp_path), default_enabled=True, enable_global_hook=False)

        # Platform-specific stdlib names may be missing at runtime on Windows,
        # but they still belong to stdlib and must never trigger pip installs.
        for module_name in ("pwd", "grp", "termios"):
            assert manager._is_stdlib_module(module_name) is True
            assert manager._resolve_target(module_name) is None
