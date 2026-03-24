#exonware/xwapi/src/exonware/xwapi/client/__init__.py
"""
Client package for xwapi library.
Contains all client/agent-related functionality:
- XWApiAgent: Main agent implementation
- engines/: Client engine implementations
"""

from exonware.xwapi.client.xwclient import XWApiAgent
__all__ = [
    "XWApiAgent",
]
