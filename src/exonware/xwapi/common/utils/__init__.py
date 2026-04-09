#exonware/xwapi/src/exonware/xwapi/utils/__init__.py
"""
Utility modules for xwapi.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
"""

from .async_utils import run_safe_coroutine, is_event_loop_running
__all__ = ['run_safe_coroutine', 'is_event_loop_running']
