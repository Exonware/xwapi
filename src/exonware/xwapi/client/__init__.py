#exonware/xwapi/src/exonware/xwapi/client/__init__.py
"""
Client and agent package: **consume** exposable actions (HTTP APIs, discovery, auth).

Mirrors the server stack; use with ``XWApiServer`` / ``XWAPI`` on the publish side.
"""

from exonware.xwapi.client.xwclient import XWApiAgent
__all__ = [
    "XWApiAgent",
]
