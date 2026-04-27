#exonware/xwapi/src/exonware/xwapi/server/base.py
"""
Abstract base classes for xwapi server library.
This module re-exports AApiServer from exonware.xwapi.base for backward compatibility.
All new code should import from exonware.xwapi.base directly.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""
# Re-export AApiServer from xwapi.base for backward compatibility

from exonware.xwapi.base import AApiServer
__all__ = ['AApiServer']
# Original implementation moved to exonware.xwapi.base for consistency
# This module kept for backward compatibility with existing imports
