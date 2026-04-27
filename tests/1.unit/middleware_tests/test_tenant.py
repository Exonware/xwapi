#exonware/xwapi/tests/1.unit/middleware_tests/test_tenant.py
"""
Unit tests for xwapi tenant middleware helpers.
"""

from __future__ import annotations

import pytest
from starlette.exceptions import HTTPException


@pytest.mark.xwapi_unit
class TestRequireTenant:

    def test_raises_when_none(self):
        from exonware.xwapi.server.middleware.tenant import require_tenant
        with pytest.raises(HTTPException) as exc_info:
            require_tenant(None)
        assert exc_info.value.status_code == 400

    def test_raises_when_empty(self):
        from exonware.xwapi.server.middleware.tenant import require_tenant
        with pytest.raises(HTTPException):
            require_tenant("")

    def test_passes_when_present(self):
        from exonware.xwapi.server.middleware.tenant import require_tenant
        require_tenant("tenant-123")  # Should not raise


@pytest.mark.xwapi_unit
class TestTenantHelpers:

    def test_conflicts_both_none(self):
        from exonware.xwapi.server.middleware.tenant import _conflicts
        assert _conflicts(None, None) is False

    def test_conflicts_candidate_none(self):
        from exonware.xwapi.server.middleware.tenant import _conflicts
        assert _conflicts(None, "t1") is False

    def test_conflicts_match(self):
        from exonware.xwapi.server.middleware.tenant import _conflicts
        assert _conflicts("t1", "t1") is False

    def test_conflicts_mismatch(self):
        from exonware.xwapi.server.middleware.tenant import _conflicts
        assert _conflicts("t1", "t2") is True

    def test_flag_enabled_with_bool(self):
        from exonware.xwapi.server.middleware.tenant import _flag_enabled

        class FakeServer:
            flag = True

        assert _flag_enabled(FakeServer(), "flag", False) is True

    def test_flag_enabled_missing_returns_default(self):
        from exonware.xwapi.server.middleware.tenant import _flag_enabled

        class FakeServer:
            pass

        assert _flag_enabled(FakeServer(), "flag", True) is True
