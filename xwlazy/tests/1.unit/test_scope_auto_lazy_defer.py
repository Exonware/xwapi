"""
Unit tests for automatic scope-based deferred loading via xwlazy global hook.
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

from exonware.xwlazy import auto_enable_lazy, uninstall_global_import_hook


def _reset_state():
    uninstall_global_import_hook()
    globals_dict = auto_enable_lazy.__globals__
    if "_instance" in globals_dict:
        globals_dict["_instance"] = None


class TestScopeAutoLazyDefer:
    def teardown_method(self):
        for mod in ("xw_auto_lazy_dep_enabled", "xw_auto_lazy_dep_disabled"):
            sys.modules.pop(mod, None)
        _reset_state()

    def test_defer_external_import_when_scope_enabled(self, tmp_path: Path):
        _reset_state()
        dep_file = tmp_path / "xw_auto_lazy_dep_enabled.py"
        dep_file.write_text("loaded_value = 42\n", encoding="utf-8")
        sys.path.insert(0, str(tmp_path))
        try:
            sys.modules.pop("xw_auto_lazy_dep_enabled", None)
            guardian = auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))
            intercept = auto_enable_lazy.__globals__["_intercepting_import"]

            mod = intercept(
                "xw_auto_lazy_dep_enabled",
                {"__name__": "exonware.xwsystem.module_a", "__package__": "exonware.xwsystem"},
                None,
                (),
                0,
            )

            assert mod.__class__.__name__ == "DeferredImportProxy"
            assert "loaded_value" not in mod.__dict__
            assert mod.loaded_value == 42
            assert sys.modules["xw_auto_lazy_dep_enabled"].__class__.__name__ != "DeferredImportProxy"
        finally:
            sys.path.remove(str(tmp_path))

    def test_no_defer_when_scope_disabled(self, tmp_path: Path):
        _reset_state()
        dep_file = tmp_path / "xw_auto_lazy_dep_disabled.py"
        dep_file.write_text("loaded_value = 7\n", encoding="utf-8")
        sys.path.insert(0, str(tmp_path))
        try:
            guardian = auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))
            guardian.configure("exonware.xwsystem", enabled=False, mode="lazy", install_strategy="smart")
            intercept = auto_enable_lazy.__globals__["_intercepting_import"]

            mod = intercept(
                "xw_auto_lazy_dep_disabled",
                {"__name__": "exonware.xwsystem.module_b", "__package__": "exonware.xwsystem"},
                None,
                (),
                0,
            )

            assert mod.__class__.__name__ != "DeferredImportProxy"
            assert getattr(mod, "loaded_value", None) == 7
            assert guardian._should_defer_external_import("xw_auto_lazy_dep_disabled", "exonware.xwsystem.module_b") is False
        finally:
            sys.path.remove(str(tmp_path))

    def test_defer_dotted_import_with_fromlist(self, tmp_path: Path):
        _reset_state()
        pkg_dir = tmp_path / "xw_auto_lazy_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
        (pkg_dir / "submodule.py").write_text("lazy_value = 123\n", encoding="utf-8")
        sys.path.insert(0, str(tmp_path))
        try:
            sys.modules.pop("xw_auto_lazy_pkg", None)
            sys.modules.pop("xw_auto_lazy_pkg.submodule", None)
            auto_enable_lazy("exonware.xwsystem", mode="smart", root=str(tmp_path))
            intercept = auto_enable_lazy.__globals__["_intercepting_import"]

            mod = intercept(
                "xw_auto_lazy_pkg.submodule",
                {"__name__": "exonware.xwsystem.module_c", "__package__": "exonware.xwsystem"},
                None,
                ("lazy_value",),
                0,
            )

            assert mod.__class__.__name__ == "DeferredImportProxy"
            assert mod.__name__ == "xw_auto_lazy_pkg.submodule"
            assert mod.lazy_value == 123
            assert sys.modules["xw_auto_lazy_pkg.submodule"].__class__.__name__ != "DeferredImportProxy"
        finally:
            sys.path.remove(str(tmp_path))
