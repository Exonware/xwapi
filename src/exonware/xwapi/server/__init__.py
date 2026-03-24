#exonware/xwapi/src/exonware/xwapi/server/__init__.py
"""
Server package for xwapi library.
Contains all server-related functionality:
- XWApiServer: Main server implementation
- engines/: Server engine implementations (FastAPI, Flask, etc.)
- admin/: Admin endpoints
- middleware/: Server middleware (auth, rate limiting, etc.)
- governance/: Instance governance (registry, lockfile)
"""

from exonware.xwapi.server.xwserver import XWApiServer
__all__ = [
    "XWApiServer",
]
