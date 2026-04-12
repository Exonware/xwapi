#exonware/xwapi/src/exonware/xwapi/governance/registry.py
"""
Instance registry for server governance.
Manages server instances with singleton enforcement and thread-safe access.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
"""

from typing import Any
import threading
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class InstanceRegistry:
    """
    Thread-safe registry for server instances.
    Enforces singleton pattern by tracking instances by server_id
    and enforcing max_instances limit.
    """

    def __init__(self, max_instances: int = 1):
        """
        Initialize instance registry.
        Args:
            max_instances: Maximum number of instances per server_id (default: 1)
        """
        self._instances: dict[str, list[Any]] = {}
        self._lock = threading.Lock()
        self._max_instances = max_instances

    def register(self, server_id: str, instance: Any) -> bool:
        """
        Register a server instance.
        Args:
            server_id: Unique identifier for the server (name/role)
            instance: Server instance to register
        Returns:
            True if registration successful, False if max_instances exceeded
        """
        with self._lock:
            if server_id not in self._instances:
                self._instances[server_id] = []
            instances = self._instances[server_id]
            # Check if instance already registered
            if instance in instances:
                logger.debug(f"Instance already registered for server_id: {server_id}")
                return True
            # Check max instances limit
            if len(instances) >= self._max_instances:
                logger.warning(
                    f"Max instances ({self._max_instances}) exceeded for server_id: {server_id}. "
                    f"Current instances: {len(instances)}"
                )
                return False
            instances.append(instance)
            logger.debug(f"Registered instance for server_id: {server_id} (total: {len(instances)})")
            return True

    def unregister(self, server_id: str, instance: Any) -> bool:
        """
        Unregister a server instance.
        Args:
            server_id: Unique identifier for the server
            instance: Server instance to unregister
        Returns:
            True if unregistration successful, False if not found
        """
        with self._lock:
            if server_id not in self._instances:
                return False
            instances = self._instances[server_id]
            if instance not in instances:
                return False
            instances.remove(instance)
            if not instances:
                del self._instances[server_id]
            logger.debug(f"Unregistered instance for server_id: {server_id}")
            return True

    def get_instances(self, server_id: str) -> list[Any]:
        """
        Get all instances for a server_id.
        Args:
            server_id: Unique identifier for the server
        Returns:
            List of registered instances
        """
        with self._lock:
            return self._instances.get(server_id, []).copy()

    def list_server_ids(self) -> list[str]:
        """
        List all registered server IDs.
        Returns:
            List of server IDs
        """
        with self._lock:
            return list(self._instances.keys())

    def count_instances(self, server_id: str) -> int:
        """
        Count instances for a server_id.
        Args:
            server_id: Unique identifier for the server
        Returns:
            Number of registered instances
        """
        with self._lock:
            return len(self._instances.get(server_id, []))

    def clear(self, server_id: str | None = None) -> None:
        """
        Clear instances for a server_id or all server_ids.
        Args:
            server_id: Optional server_id to clear. If None, clears all.
        """
        with self._lock:
            if server_id is None:
                self._instances.clear()
                logger.debug("Cleared all instances from registry")
            else:
                if server_id in self._instances:
                    del self._instances[server_id]
                    logger.debug(f"Cleared instances for server_id: {server_id}")
# Global registry instance
_global_registry: InstanceRegistry | None = None
_registry_lock = threading.Lock()


def get_registry(max_instances: int = 1) -> InstanceRegistry:
    """
    Get or create global instance registry.
    Args:
        max_instances: Maximum number of instances per server_id (only used on first call)
    Returns:
        Global InstanceRegistry instance
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = InstanceRegistry(max_instances=max_instances)
        return _global_registry
