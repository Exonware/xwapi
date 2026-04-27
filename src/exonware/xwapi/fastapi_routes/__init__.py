"""FastAPI router factories for xwapi primitives.

These modules offer ``mount_*`` helpers that attach FastAPI routes
backed by xwapi internals (simple bearer-token store, persisted JSON
theme document, …) onto a caller-supplied :class:`APIRouter`. Products
(HIVE API, …) assemble their API surface by calling the mount helpers
and wiring them to their own auth dependency + state object. Nothing
here imports product-specific code — the helpers stay reusable.
"""

from __future__ import annotations

from .tokens import mount_token_routes
from .theme import mount_theme_routes

__all__ = ["mount_token_routes", "mount_theme_routes"]
