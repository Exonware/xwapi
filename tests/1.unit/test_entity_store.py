from __future__ import annotations

import pytest

from exonware.xwapi.entity_store import InMemoryEntityStore, XWStorageEntityStore


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_inmemory_entity_store_crud() -> None:
    """In-memory store should support CRUD semantics."""
    store = InMemoryEntityStore()
    await store.put_item("users", "u1", {"id": "u1", "name": "Alice"})
    item = await store.get_item("users", "u1")
    assert item is not None
    assert item["name"] == "Alice"

    items = await store.list_items("users")
    assert len(items) == 1
    assert items[0]["id"] == "u1"

    deleted = await store.delete_item("users", "u1")
    assert deleted is True
    missing = await store.get_item("users", "u1")
    assert missing is None


class _FakeStorage:
    def __init__(self):
        self._db: dict[str, object] = {}

    async def read(self, path: str):
        if path not in self._db:
            raise FileNotFoundError(path)
        return self._db[path]

    async def write(self, path: str, data):
        self._db[path] = data

    async def delete(self, path: str):
        self._db.pop(path, None)

    async def exists(self, path: str) -> bool:
        return path in self._db


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_xwstorage_entity_store_crud() -> None:
    """xwstorage adapter should preserve items and index entries."""
    storage = _FakeStorage()
    store = XWStorageEntityStore(storage, key_prefix="xwapi/test")

    await store.put_item("users", "u1", {"id": "u1", "name": "Alice"})
    await store.put_item("users", "u2", {"id": "u2", "name": "Bob"})

    items = await store.list_items("users")
    ids = sorted(item["id"] for item in items)
    assert ids == ["u1", "u2"]

    deleted = await store.delete_item("users", "u1")
    assert deleted is True
    missing = await store.get_item("users", "u1")
    assert missing is None
