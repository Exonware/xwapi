#exonware/xwapi/src/exonware/xwapi/governance/__init__.py
"""
Instance governance module for xwapi.
Provides singleton enforcement, instance registry, lockfile management,
and PID-based process control for server instances.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from .registry import InstanceRegistry, get_registry
from .lockfile import LockfileManager, create_lockfile_manager
__all__ = [
    'InstanceRegistry',
    'get_registry',
    'LockfileManager',
    'create_lockfile_manager',
]
