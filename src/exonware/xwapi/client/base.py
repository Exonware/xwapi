#exonware/xwapi/src/exonware/xwapi/client/base.py
"""
Abstract base classes for xwapi client library.
This module re-exports AApiAgent from exonware.xwapi.base for backward compatibility.
All new code should import from exonware.xwapi.base directly.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""
# Re-export AApiAgent from xwapi.base for backward compatibility

from exonware.xwapi.base import AApiAgent
__all__ = ['AApiAgent']
# Original implementation moved to exonware.xwapi.base for consistency
# This module kept for backward compatibility with existing imports
