"""
Unit tests for the thin public wrapper module `xwlazy.lazy`.

These tests ensure:
- `config_package_lazy_install_enabled` delegates correctly to `auto_enable_lazy`
- `xwimport` is an alias to the core `lazy_import` API
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.xwlazy_unit


def _import_lazy_module(monkeypatch):
    """
    Import `xwlazy.lazy` with `auto_enable_lazy` and `lazy_import` patched.

    Returns:
        module, auto_enable_lazy_mock, lazy_import_mock, resolve_flags_mock
    """

    import importlib
    import sys

    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Patch the core APIs before importing the wrapper module
    auto_enable_lazy_mock = MagicMock(name="auto_enable_lazy")
    lazy_import_mock = MagicMock(name="lazy_import")
    resolve_flags_mock = MagicMock(
        name="resolve_package_lazy_flags",
        return_value={
            "enable_lazy_install": None,
            "enable_lazy_loading": None,
            "root_dir": None,
        },
    )
    monkeypatch.setattr(
        "exonware.xwlazy.auto_enable_lazy",
        auto_enable_lazy_mock,
        raising=False,
    )
    monkeypatch.setattr(
        "exonware.xwlazy.lazy_import",
        lazy_import_mock,
        raising=False,
    )
    monkeypatch.setattr(
        "exonware.xwlazy.resolve_package_lazy_flags",
        resolve_flags_mock,
        raising=False,
    )

    lazy_mod = importlib.import_module("xwlazy.lazy")
    importlib.reload(lazy_mod)
    return lazy_mod, auto_enable_lazy_mock, lazy_import_mock, resolve_flags_mock


class TestConfigPackageLazyInstallEnabled:
    """Tests for `config_package_lazy_install_enabled` wrapper."""

    def test_enabled_true_delegates_to_auto_enable_lazy(self, monkeypatch):
        """When enabled=True, wrapper calls auto_enable_lazy with mode and kwargs."""
        lazy_mod, auto_enable_lazy_mock, _, resolve_flags_mock = _import_lazy_module(monkeypatch)

        lazy_mod.config_package_lazy_install_enabled(
            "mypkg",
            enabled=True,
            mode="smart",
            install_hook=True,  # currently ignored by wrapper
            extra_flag="value",
        )

        auto_enable_lazy_mock.assert_called_once()
        resolve_flags_mock.assert_called_once()
        args, kwargs = auto_enable_lazy_mock.call_args
        assert args[0] == "mypkg"
        # Wrapper forwards mode and arbitrary kwargs, but not install_hook
        assert kwargs.get("mode") == "smart"
        assert kwargs.get("extra_flag") == "value"
        assert "install_hook" not in kwargs

    def test_enabled_false_does_not_call_auto_enable_lazy(self, monkeypatch):
        """When enabled=False, wrapper performs no side effects."""
        lazy_mod, auto_enable_lazy_mock, _, resolve_flags_mock = _import_lazy_module(monkeypatch)

        lazy_mod.config_package_lazy_install_enabled(
            "mypkg",
            enabled=False,
            mode="smart",
            install_hook=True,
        )

        auto_enable_lazy_mock.assert_not_called()
        resolve_flags_mock.assert_called_once()

    def test_config_disable_overrides_enabled_true(self, monkeypatch):
        """Config switch enable_lazy_install=false should disable wrapper activation."""
        lazy_mod, auto_enable_lazy_mock, _, resolve_flags_mock = _import_lazy_module(monkeypatch)
        resolve_flags_mock.return_value = {
            "enable_lazy_install": False,
            "enable_lazy_loading": True,
            "root_dir": "/tmp/project",
        }

        lazy_mod.config_package_lazy_install_enabled("mypkg", enabled=True, mode="smart")

        auto_enable_lazy_mock.assert_not_called()
        resolve_flags_mock.assert_called_once()

    def test_resolved_root_forwarded_when_missing(self, monkeypatch):
        """Wrapper should forward resolved root so config lookup remains deterministic."""
        lazy_mod, auto_enable_lazy_mock, _, resolve_flags_mock = _import_lazy_module(monkeypatch)
        resolve_flags_mock.return_value = {
            "enable_lazy_install": True,
            "enable_lazy_loading": False,
            "root_dir": "/tmp/project",
        }

        lazy_mod.config_package_lazy_install_enabled("mypkg", enabled=True, mode="smart")

        auto_enable_lazy_mock.assert_called_once()
        _, kwargs = auto_enable_lazy_mock.call_args
        assert kwargs.get("root") == "/tmp/project"

    def test_explicit_root_not_overwritten(self, monkeypatch):
        """Explicit root argument takes precedence over resolved root."""
        lazy_mod, auto_enable_lazy_mock, _, resolve_flags_mock = _import_lazy_module(monkeypatch)
        resolve_flags_mock.return_value = {
            "enable_lazy_install": True,
            "enable_lazy_loading": True,
            "root_dir": "/tmp/project",
        }

        lazy_mod.config_package_lazy_install_enabled(
            "mypkg",
            enabled=True,
            mode="smart",
            root="/custom/root",
        )

        auto_enable_lazy_mock.assert_called_once()
        _, kwargs = auto_enable_lazy_mock.call_args
        assert kwargs.get("root") == "/custom/root"


class TestXwimportAlias:
    """Tests for `xwimport` alias exported from `xwlazy.lazy`."""

    def test_xwimport_is_lazy_import_alias(self, monkeypatch):
        """xwimport delegates directly to `exonware.xwlazy.lazy_import`."""
        lazy_mod, _, lazy_import_mock, _ = _import_lazy_module(monkeypatch)

        sentinel = object()
        lazy_import_mock.return_value = sentinel

        result = lazy_mod.xwimport("json")

        lazy_import_mock.assert_called_once_with("json")
        assert result is sentinel

