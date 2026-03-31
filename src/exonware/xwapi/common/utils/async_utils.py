#exonware/xwapi/src/exonware/xwapi/utils/async_utils.py
"""
Safe coroutine execution utilities.
Provides utilities for safely executing coroutines without blocking
running event loops from sync code paths.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
"""

import asyncio
import threading
from typing import Any, Coroutine, Optional
from concurrent.futures import ThreadPoolExecutor
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


def is_event_loop_running() -> bool:
    """
    Check if an event loop is currently running.
    Returns:
        True if event loop is running, False otherwise
    """
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


def run_safe_coroutine(coro: Coroutine, timeout: Optional[float] = None) -> Any:
    """
    Safely execute a coroutine without blocking running event loops.
    This function handles the case where an event loop is already running
    (e.g., in uvicorn) by using run_coroutine_threadsafe() instead of
    asyncio.run() which would fail.
    Args:
        coro: Coroutine to execute
        timeout: Optional timeout in seconds
    Returns:
        Coroutine result
    Raises:
        RuntimeError: If coroutine execution fails
        TimeoutError: If timeout is exceeded
    """
    if is_event_loop_running():
        # Event loop is already running - use run_coroutine_threadsafe
        logger.debug("Event loop is running, using run_coroutine_threadsafe")
        loop = asyncio.get_running_loop()
        # Create a future to wait for the result
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            if timeout:
                return future.result(timeout=timeout)
            else:
                return future.result()
        except Exception as e:
            logger.error(f"Error executing coroutine in running loop: {e}")
            raise
    else:
        # No event loop running - use asyncio.run()
        logger.debug("No event loop running, using asyncio.run()")
        try:
            if timeout:
                return asyncio.run(asyncio.wait_for(coro, timeout=timeout))
            else:
                return asyncio.run(coro)
        except Exception as e:
            logger.error(f"Error executing coroutine: {e}")
            raise


def run_async_in_thread(coro: Coroutine, timeout: Optional[float] = None) -> Any:
    """
    Execute a coroutine in a separate thread with its own event loop.
    This is useful when you need to run async code from sync code
    but don't want to interfere with the main event loop.
    Args:
        coro: Coroutine to execute
        timeout: Optional timeout in seconds
    Returns:
        Coroutine result
    """
    def run_in_thread():
        """Run coroutine in thread-local event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if timeout:
                return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
            else:
                return loop.run_until_complete(coro)
        finally:
            loop.close()
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_thread)
        return future.result()
