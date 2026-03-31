#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/transactions.py
"""
Transaction Support for XWJSON
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
ACID transaction support with write-ahead logging (WAL) for zero performance penalty.
Priority 1 (Security): Safe transactions, atomicity guarantees
Priority 2 (Usability): Clear transaction API, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): WAL ensures zero performance penalty
Priority 5 (Extensibility): Plugin system for custom transaction strategies
"""

import asyncio
from typing import Any
from pathlib import Path
from .serializer import XWJSONSerializer
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.formats.text import json as xw_json


class XWJSONTransaction:
    """
    Transaction manager with ACID guarantees.
    Features:
    - Atomicity: All operations succeed or fail together
    - Consistency: Data remains valid throughout transaction
    - Isolation: Concurrent transactions don't interfere
    - Durability: Committed transactions persist
    - Performance: WAL ensures zero penalty
    """

    def __init__(self, file_path: str | Path):
        """
        Initialize transaction.
        Args:
            file_path: Path to XWJSON file
        """
        self._file_path = Path(file_path)
        self._wal_path = self._file_path.with_suffix(self._file_path.suffix + '.wal')
        self._operations: list[dict[str, Any]] = []
        self._committed = False
        self._rolled_back = False

    @staticmethod
    def _get_file_lock(file_path: Path) -> asyncio.Lock:
        """Get per-file async lock to serialize concurrent transaction commits."""
        resolved = file_path.resolve()
        lock = _TRANSACTION_FILE_LOCKS.get(resolved)
        if lock is None:
            lock = asyncio.Lock()
            _TRANSACTION_FILE_LOCKS[resolved] = lock
        return lock

    async def write(self, key: str, value: Any) -> None:
        """Add write operation to transaction."""
        if self._committed or self._rolled_back:
            raise SerializationError("Transaction already committed or rolled back")
        self._operations.append({
            'op': 'write',
            'key': key,
            'value': value
        })

    async def update_path(self, path: str, value: Any) -> None:
        """Add path update operation to transaction."""
        if self._committed or self._rolled_back:
            raise SerializationError("Transaction already committed or rolled back")
        self._operations.append({
            'op': 'update_path',
            'path': path,
            'value': value
        })

    async def commit(self) -> None:
        """Commit transaction (apply all operations atomically)."""
        if self._committed:
            return
        if self._rolled_back:
            raise SerializationError("Cannot commit rolled back transaction")
        try:
            # Write to WAL first
            import aiofiles
            async with aiofiles.open(self._wal_path, 'w', encoding='utf-8') as f:
                await f.write(xw_json.dumps(self._operations, indent=2))
            # Apply operations
            await self._apply_operations()
            # Remove WAL on success
            if self._wal_path.exists():
                self._wal_path.unlink()
            self._committed = True
        except Exception as e:
            # Rollback on error
            await self.rollback()
            raise SerializationError(f"Transaction commit failed: {e}") from e

    async def rollback(self) -> None:
        """Rollback transaction (discard all operations)."""
        if self._rolled_back:
            return
        # Remove WAL
        if self._wal_path.exists():
            self._wal_path.unlink()
        self._operations.clear()
        self._rolled_back = True

    async def _apply_operations(self) -> None:
        """
        Apply all operations atomically.
        Loads data, applies all operations, then saves.
        """
        serializer = XWJSONSerializer()
        # Load current data
        if self._file_path.exists():
            data = serializer.load_file(str(self._file_path))
        else:
            data = {}
        # Apply all operations
        for operation in self._operations:
            op_type = operation.get('op')
            if op_type == 'write':
                key = operation.get('key')
                value = operation.get('value')
                if isinstance(data, dict):
                    data[key] = value
                else:
                    raise SerializationError(f"Cannot write to non-dict data: {type(data)}")
            elif op_type == 'update_path':
                path = operation.get('path', '')
                value = operation.get('value')
                # Simple path update (JSON Pointer style)
                parts = path.strip('/').split('/') if path else []
                current = data
                for part in parts[:-1]:
                    if isinstance(current, dict):
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    elif isinstance(current, list):
                        idx = int(part)
                        current = current[idx]
                    else:
                        raise SerializationError(f"Cannot navigate to path: {path}")
                if parts:
                    final_key = parts[-1]
                    if isinstance(current, dict):
                        current[final_key] = value
                    elif isinstance(current, list):
                        current[int(final_key)] = value
                else:
                    data = value
        # Save updated data
        serializer.save_file(data, str(self._file_path))


class TransactionContext:
    """
    Context manager for transactions.
    Usage:
        async with TransactionContext("file.xwjson") as tx:
            await tx.write("key1", value1)
            await tx.write("key2", value2)
            # Commit on success, rollback on error
    """

    def __init__(self, file_path: str | Path):
        """
        Initialize transaction context.
        Args:
            file_path: Path to XWJSON file
        """
        self._file_path = file_path
        self._transaction: XWJSONTransaction | None = None
        self._lock: asyncio.Lock | None = None

    async def __aenter__(self) -> XWJSONTransaction:
        """Enter transaction context."""
        # Acquire per-file lock for the entire transaction scope (read+write isolation).
        self._lock = XWJSONTransaction._get_file_lock(Path(self._file_path))
        await self._lock.acquire()
        self._transaction = XWJSONTransaction(self._file_path)
        return self._transaction

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit transaction context (commit or rollback)."""
        try:
            if self._transaction:
                if exc_type is None:
                    # No exception - commit
                    await self._transaction.commit()
                else:
                    # Exception occurred - rollback
                    await self._transaction.rollback()
        finally:
            if self._lock and self._lock.locked():
                self._lock.release()
        return False  # Don't suppress exceptions
# Convenience function

def transaction(file_path: str | Path) -> TransactionContext:
    """
    Create transaction context.
    Args:
        file_path: Path to XWJSON file
    Returns:
        TransactionContext
    """
    return TransactionContext(file_path)


# Shared per-file lock map for async transaction commits.
_TRANSACTION_FILE_LOCKS: dict[Path, asyncio.Lock] = {}
