#exonware/xwapi/src/exonware/xwapi/scrapping/http.py
"""
Minimal HTTP fetcher built on `urllib.request` so the framework has zero
third-party dependencies. Source adapters that need richer behavior
(JS-rendered pages, cookies, proxies) can plug in their own client and
ignore this helper.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from typing import Any, Mapping

from .contracts import IRateLimiter

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; eXonware-xwapi-scrapping/0.1; "
    "+https://exonware.com)"
)


class HttpFetcher:
    """Tiny GET-focused HTTP client with optional rate limiting and JSON decode."""

    def __init__(
        self,
        rate_limiter: IRateLimiter | None = None,
        timeout: float = 20.0,
        user_agent: str = DEFAULT_USER_AGENT,
        extra_headers: Mapping[str, str] | None = None,
    ):
        self._rate = rate_limiter
        self._timeout = timeout
        self._headers = {"User-Agent": user_agent, "Accept": "*/*"}
        if extra_headers:
            self._headers.update(extra_headers)

    def get(self, url: str, headers: Mapping[str, str] | None = None) -> bytes:
        """Issue a GET, return raw bytes. Raises urllib.error.URLError on failure."""
        if self._rate is not None:
            self._rate.acquire()
        merged = dict(self._headers)
        if headers:
            merged.update(headers)
        req = urllib.request.Request(url, headers=merged, method="GET")
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            return resp.read()

    def get_json(self, url: str, headers: Mapping[str, str] | None = None) -> Any:
        """GET + decode as UTF-8 JSON."""
        body = self.get(url, headers=headers)
        return json.loads(body.decode("utf-8"))

    def get_text(self, url: str, headers: Mapping[str, str] | None = None) -> str:
        """GET + decode as UTF-8 text."""
        body = self.get(url, headers=headers)
        return body.decode("utf-8", errors="replace")
