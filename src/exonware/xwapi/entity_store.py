#!/usr/bin/env python3
"""
Persistence backends for entity resources when *publishing* CRUD-style HTTP routes (facade).
"""

from __future__ import annotations

from typing import Any, Optional


class InMemoryEntityStore:
    """In-memory CRUD store used as default backend."""

    def __init__(self, records: dict[str, dict[str, dict[str, Any]]] | None = None):
        self._records: dict[str, dict[str, dict[str, Any]]] = records if records is not None else {}

    async def list_items(self, collection: str) -> list[dict[str, Any]]:
        records = self._records.setdefault(collection, {})
        return [dict(item) for item in records.values()]

    async def get_item(self, collection: str, entity_id: str) -> dict[str, Any] | None:
        records = self._records.setdefault(collection, {})
        item = records.get(entity_id)
        if item is None:
            return None
        return dict(item)

    async def put_item(self, collection: str, entity_id: str, item: dict[str, Any]) -> None:
        records = self._records.setdefault(collection, {})
        records[entity_id] = dict(item)

    async def delete_item(self, collection: str, entity_id: str) -> bool:
        records = self._records.setdefault(collection, {})
        if entity_id not in records:
            return False
        records.pop(entity_id)
        return True


class XWStorageEntityStore:
    """xwstorage-backed CRUD store."""

    def __init__(self, storage: Any, key_prefix: str = "xwapi/entity_crud"):
        self._storage = storage
        self._key_prefix = key_prefix.rstrip("/")

    def _index_path(self, collection: str) -> str:
        return f"{self._key_prefix}/{collection}/__index__"

    def _item_path(self, collection: str, entity_id: str) -> str:
        return f"{self._key_prefix}/{collection}/{entity_id}"

    async def _read_index(self, collection: str) -> list[str]:
        index_path = self._index_path(collection)
        try:
            data = await self._storage.read(index_path)
            if isinstance(data, dict):
                ids = data.get("ids", [])
                if isinstance(ids, list):
                    return [str(item) for item in ids]
            if isinstance(data, list):
                return [str(item) for item in data]
        except Exception:
            return []
        return []

    async def _write_index(self, collection: str, ids: list[str]) -> None:
        # Preserve insertion order while removing duplicates.
        unique_ids = list(dict.fromkeys(ids))
        await self._storage.write(self._index_path(collection), {"ids": unique_ids})

    async def list_items(self, collection: str) -> list[dict[str, Any]]:
        ids = await self._read_index(collection)
        items: list[dict[str, Any]] = []
        for entity_id in ids:
            item = await self.get_item(collection, entity_id)
            if item is not None:
                items.append(item)
        return items

    async def get_item(self, collection: str, entity_id: str) -> dict[str, Any] | None:
        item_path = self._item_path(collection, entity_id)
        try:
            item = await self._storage.read(item_path)
            if isinstance(item, dict):
                return dict(item)
            return {"id": entity_id, "value": item}
        except Exception:
            return None

    async def put_item(self, collection: str, entity_id: str, item: dict[str, Any]) -> None:
        await self._storage.write(self._item_path(collection, entity_id), dict(item))
        ids = await self._read_index(collection)
        if entity_id not in ids:
            ids.append(entity_id)
            await self._write_index(collection, ids)

    async def delete_item(self, collection: str, entity_id: str) -> bool:
        item_path = self._item_path(collection, entity_id)
        try:
            exists = await self._storage.exists(item_path)
        except Exception:
            exists = False
        if not exists:
            return False
        await self._storage.delete(item_path)
        ids = [item for item in await self._read_index(collection) if item != entity_id]
        await self._write_index(collection, ids)
        return True
