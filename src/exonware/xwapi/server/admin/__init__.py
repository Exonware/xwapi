#exonware/xwapi/src/exonware/xwapi/admin/__init__.py
"""
Admin endpoints module for xwapi.
Provides built-in server management endpoints (start, stop, restart, status, health, log)
that work with any AApiServer implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
"""

from .router import create_admin_router, register_admin_endpoints
__all__ = ['create_admin_router', 'register_admin_endpoints']
