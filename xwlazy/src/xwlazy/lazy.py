"""
xwlazy.lazy - public API for package-level lazy install configuration.
Used by xwnode, xwsystem, etc. for: from xwlazy.lazy import config_package_lazy_install_enabled.
Company: eXonware.com
"""
from exonware.xwlazy import auto_enable_lazy, lazy_import, resolve_package_lazy_flags

# Alias used by xwnode and others
xwimport = lazy_import

__all__ = ["config_package_lazy_install_enabled", "xwimport"]


def config_package_lazy_install_enabled(
    package_name: str,
    enabled: bool = True,
    mode: str = "smart",
    install_hook: bool = True,
    **kwargs,
) -> None:
    """Configure a package for lazy installation. Wrapper over auto_enable_lazy."""
    call_kwargs = dict(kwargs)
    flag_config = resolve_package_lazy_flags(call_kwargs.get("root", "."))
    # Keep explicit enabled=False semantics, but allow config to globally disable install.
    config_allows_install = flag_config["enable_lazy_install"] is not False
    effective_enabled = bool(enabled) and config_allows_install
    if not effective_enabled:
        return
    # Pass resolved project root to keep config discovery stable even when cwd changes.
    if "root" not in call_kwargs and flag_config.get("root_dir"):
        call_kwargs["root"] = flag_config["root_dir"]
    auto_enable_lazy(package_name, mode=mode, **call_kwargs)
