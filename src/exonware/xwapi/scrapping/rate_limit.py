#exonware/xwapi/src/exonware/xwapi/scrapping/rate_limit.py
"""
Token-bucket rate limiter for scraper HTTP calls.

Simple, thread-safe, monotonic-clock-based. Use one instance per outbound
host so two scrapers can run side-by-side without bleeding into each other.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
import threading
import time


class TokenBucketRateLimiter:
    """Classic token-bucket: capacity tokens, refilled at `rate_per_sec` tokens/sec."""

    def __init__(self, rate_per_sec: float, capacity: int | None = None):
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be > 0")
        self._rate = float(rate_per_sec)
        # Default capacity allows ~1 second of burst.
        self._capacity = float(capacity if capacity is not None else max(1, int(rate_per_sec)))
        self._tokens = self._capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, n: float = 1.0) -> None:
        """Block until `n` tokens are available, then consume them."""
        if n <= 0:
            return
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now
                self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
                if self._tokens >= n:
                    self._tokens -= n
                    return
                # Need this many more tokens; sleep that long outside the lock.
                deficit = n - self._tokens
                wait = deficit / self._rate
            time.sleep(wait)
