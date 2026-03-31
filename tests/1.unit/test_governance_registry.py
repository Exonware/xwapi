from __future__ import annotations

import pytest

from exonware.xwapi.server.governance.registry import InstanceRegistry


@pytest.mark.xwapi_unit
def test_registry_respects_max_instances() -> None:
    """Registry should reject registrations beyond max_instances."""
    registry = InstanceRegistry(max_instances=1)
    a = object()
    b = object()

    assert registry.register("api", a) is True
    assert registry.register("api", b) is False
    assert registry.count_instances("api") == 1


@pytest.mark.xwapi_unit
def test_registry_duplicate_registration_is_idempotent() -> None:
    """Registering same object twice should not consume extra capacity."""
    registry = InstanceRegistry(max_instances=1)
    a = object()

    assert registry.register("api", a) is True
    assert registry.register("api", a) is True
    assert registry.count_instances("api") == 1


@pytest.mark.xwapi_unit
def test_registry_unregister_and_clear_paths() -> None:
    """Unregister and clear should fully remove tracked ids."""
    registry = InstanceRegistry(max_instances=2)
    a = object()
    b = object()

    assert registry.register("api", a) is True
    assert registry.register("api", b) is True
    assert registry.unregister("api", a) is True
    assert registry.count_instances("api") == 1

    registry.clear("api")
    assert registry.count_instances("api") == 0
    assert "api" not in registry.list_server_ids()
