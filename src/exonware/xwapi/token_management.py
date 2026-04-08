#!/usr/bin/env python3
"""
API token lifecycle for clients calling published actions (issue, revoke, usage, recharge).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from exonware.xwapi.contracts import IAuthProvider, IStorageProvider, IPaymentProvider


class APITokenManager:
    """Coordinates auth/storage/payment providers for token lifecycle and usage."""

    def __init__(
        self,
        *,
        auth_provider: IAuthProvider,
        storage_provider: IStorageProvider,
        payment_provider: IPaymentProvider,
        storage_prefix: str = "xwapi/token_mgmt",
    ):
        self._auth_provider = auth_provider
        self._storage_provider = storage_provider
        self._payment_provider = payment_provider
        self._prefix = storage_prefix.rstrip("/")
        self._lock = RLock()
        self._subject_locks: dict[str, asyncio.Lock] = {}

    def _get_subject_lock(self, subject_id: str) -> asyncio.Lock:
        with self._lock:
            lock = self._subject_locks.get(subject_id)
            if lock is None:
                lock = asyncio.Lock()
                self._subject_locks[subject_id] = lock
            return lock

    def _token_key(self, token_id: str) -> str:
        return f"{self._prefix}/tokens/{token_id}"

    def _subject_index_key(self, subject_id: str) -> str:
        return f"{self._prefix}/subjects/{subject_id}/tokens"

    def _usage_key(self, token_id: str) -> str:
        return f"{self._prefix}/usage/{token_id}"

    async def create_token(
        self,
        *,
        subject_id: str,
        name: str,
        scopes: list[str],
        expires_in_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        issued = await self._auth_provider.issue_api_token(
            subject_id=subject_id,
            name=name,
            scopes=scopes,
            expires_in_seconds=expires_in_seconds,
            metadata=metadata,
        )
        token_id = issued["token_id"]
        record = {
            **issued["record"],
            "token_id": token_id,
            "subject_id": subject_id,
            "name": name,
            "scopes": list(scopes or []),
            "created_at": issued["record"].get("created_at"),
            "last_used_at": None,
            "usage_count": 0,
            "credits_spent": 0.0,
        }
        await self._storage_provider.write(self._token_key(token_id), record)
        async with self._get_subject_lock(subject_id):
            try:
                subject_tokens = await self._storage_provider.read(self._subject_index_key(subject_id))
                if not isinstance(subject_tokens, list):
                    subject_tokens = []
            except Exception:
                subject_tokens = []
            if token_id not in subject_tokens:
                subject_tokens.append(token_id)
            await self._storage_provider.write(self._subject_index_key(subject_id), subject_tokens)
        await self._storage_provider.write(self._usage_key(token_id), [])
        return {
            "token": issued["token"],
            "token_id": token_id,
            "record": record,
        }

    async def list_tokens(self, *, subject_id: str | None = None) -> list[dict[str, Any]]:
        if subject_id:
            try:
                token_ids = await self._storage_provider.read(self._subject_index_key(subject_id))
            except Exception:
                return []
            result: list[dict[str, Any]] = []
            for token_id in token_ids if isinstance(token_ids, list) else []:
                try:
                    record = await self._storage_provider.read(self._token_key(str(token_id)))
                    if isinstance(record, dict):
                        result.append(record)
                except Exception:
                    continue
            return result
        # No global scan contract in storage provider, so return empty by design.
        return []

    async def revoke_token(self, token_id: str) -> bool:
        revoked = await self._auth_provider.revoke_api_token(token_id)
        if not revoked:
            return False
        try:
            record = await self._storage_provider.read(self._token_key(token_id))
            if isinstance(record, dict):
                record["revoked"] = True
                await self._storage_provider.write(self._token_key(token_id), record)
        except Exception:
            pass
        return True

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        return await self._auth_provider.verify_api_token(token)

    async def record_usage(
        self,
        *,
        token_id: str,
        amount: float,
        operation: str,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        token = await self._storage_provider.read(self._token_key(token_id))
        if not isinstance(token, dict):
            raise ValueError("invalid token record")
        if token.get("revoked"):
            raise ValueError("token revoked")
        subject_id = str(token.get("subject_id") or "")
        if not subject_id:
            raise ValueError("invalid token subject")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("amount must be > 0")

        async with self._get_subject_lock(subject_id):
            if idempotency_key:
                try:
                    existing_history = await self._storage_provider.read(self._usage_key(token_id))
                    if isinstance(existing_history, list):
                        for event in existing_history:
                            if not isinstance(event, dict):
                                continue
                            if event.get("idempotency_key") == idempotency_key:
                                if float(event.get("amount", 0.0)) != float(amount):
                                    raise ValueError("idempotency key reuse with different amount")
                                return dict(event)
                except ValueError:
                    raise
                except Exception:
                    pass
            balance_before = await self._payment_provider.get_balance(subject_id)
            if amount > balance_before:
                raise ValueError("insufficient balance")
            payment_metadata = {"type": "usage_debit", "token_id": token_id, "operation": operation}
            if idempotency_key:
                payment_metadata["idempotency_key"] = idempotency_key
            debit_event = await self._payment_provider.consume_credits(
                subject_id=subject_id,
                amount=amount,
                metadata=payment_metadata,
                idempotency_key=idempotency_key,
            )
            usage_event = {
                "token_id": token_id,
                "subject_id": subject_id,
                "operation": operation,
                "amount": amount,
                "metadata": dict(metadata or {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "balance_before": balance_before,
                "balance_after": float(debit_event.get("balance_after", balance_before - amount)),
            }
            if idempotency_key:
                usage_event["idempotency_key"] = idempotency_key
            try:
                try:
                    history = await self._storage_provider.read(self._usage_key(token_id))
                    if not isinstance(history, list):
                        history = []
                except Exception:
                    history = []
                history.append(usage_event)
                await self._storage_provider.write(self._usage_key(token_id), history)

                token["usage_count"] = int(token.get("usage_count", 0)) + 1
                token["credits_spent"] = float(token.get("credits_spent", 0.0)) + amount
                token["last_used_at"] = usage_event["timestamp"]
                await self._storage_provider.write(self._token_key(token_id), token)
            except Exception:
                # Best-effort compensation if usage persistence fails after debit.
                compensation_metadata = {"type": "usage_compensation", "token_id": token_id, "operation": operation}
                if idempotency_key:
                    compensation_metadata["idempotency_key"] = idempotency_key
                await self._payment_provider.create_recharge(
                    subject_id=subject_id,
                    amount=amount,
                    currency="USD",
                    metadata=compensation_metadata,
                )
                raise
        return usage_event

    async def get_usage(self, token_id: str) -> list[dict[str, Any]]:
        try:
            history = await self._storage_provider.read(self._usage_key(token_id))
            if isinstance(history, list):
                return history
        except Exception:
            pass
        return []

    async def recharge(
        self,
        *,
        subject_id: str,
        amount: float,
        currency: str = "USD",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._payment_provider.create_recharge(
            subject_id=subject_id,
            amount=amount,
            currency=currency,
            metadata=metadata,
        )

    async def get_balance(self, subject_id: str) -> float:
        return await self._payment_provider.get_balance(subject_id)
