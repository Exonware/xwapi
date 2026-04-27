#exonware/xwapi/tests/1.unit/middleware_tests/test_ratelimit.py
"""
Unit tests for xwapi rate limiting middleware.
"""

from __future__ import annotations

import pytest
from datetime import timedelta
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.xwapi_unit
class TestRateLimiter:

    def test_default_allows_requests(self):
        from exonware.xwapi.server.middleware.ratelimit import RateLimiter
        limiter = RateLimiter(calls=5, period=timedelta(minutes=1))
        allowed, remaining, _ = limiter.is_allowed("test_key")
        assert allowed is True
        assert remaining == 4

    def test_exceeds_limit(self):
        from exonware.xwapi.server.middleware.ratelimit import RateLimiter
        limiter = RateLimiter(calls=2, period=timedelta(minutes=1))
        limiter.is_allowed("key_exceed")
        limiter.is_allowed("key_exceed")
        allowed, remaining, _ = limiter.is_allowed("key_exceed")
        assert allowed is False
        assert remaining == 0

    def test_get_key_per_ip(self):
        from exonware.xwapi.server.middleware.ratelimit import RateLimiter
        limiter = RateLimiter(per_ip=True, per_client=False, per_tenant=False)
        request = MagicMock()
        request.client.host = "1.2.3.4"
        key = limiter.get_key(request)
        assert "ip:1.2.3.4" in key

    def test_get_key_no_client(self):
        from exonware.xwapi.server.middleware.ratelimit import RateLimiter
        limiter = RateLimiter(per_ip=True)
        request = MagicMock()
        request.client = None
        key = limiter.get_key(request)
        assert "ip:unknown" in key

    def test_separate_keys_isolated(self):
        from exonware.xwapi.server.middleware.ratelimit import RateLimiter
        limiter = RateLimiter(calls=1, period=timedelta(minutes=1))
        limiter.is_allowed("key_a")
        allowed, _, _ = limiter.is_allowed("key_b")
        assert allowed is True
