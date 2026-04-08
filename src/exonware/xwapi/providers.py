#!/usr/bin/env python3
"""
Provider adapters for secured *exposable actions* and API runtime (auth, storage, payment).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Optional

from exonware.xwapi.contracts import AuthContext, IAuthProvider, IStorageProvider, IPaymentProvider


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryStorageProvider(IStorageProvider):
    """Default in-memory storage provider."""

    def __init__(self):
        self._lock = RLock()
        self._records: dict[str, Any] = {}

    async def read(self, key: str) -> Any:
        with self._lock:
            if key not in self._records:
                raise KeyError(key)
            value = self._records[key]
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, list):
                return list(value)
            return value

    async def write(self, key: str, value: Any) -> None:
        with self._lock:
            self._records[key] = value

    async def delete(self, key: str) -> None:
        with self._lock:
            self._records.pop(key, None)

    async def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._records


class XWStorageProvider(IStorageProvider):
    """Adapter from xwstorage-like instance to IStorageProvider."""

    def __init__(self, storage: Any):
        self._storage = storage

    async def read(self, key: str) -> Any:
        return await self._storage.read(key)

    async def write(self, key: str, value: Any) -> None:
        await self._storage.write(key, value)

    async def delete(self, key: str) -> None:
        await self._storage.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._storage.exists(key)


class LocalAuthProvider(IAuthProvider):
    """Library-level auth provider for API token issue/verify/revoke."""

    def __init__(self):
        self._lock = RLock()
        self._token_hashes: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def issue_api_token(
        self,
        *,
        subject_id: str,
        name: str,
        scopes: list[str],
        expires_in_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        token_id = secrets.token_hex(10)
        secret = secrets.token_urlsafe(32)
        plaintext_token = f"xw_{token_id}_{secret}"
        expires_at = None
        if expires_in_seconds and expires_in_seconds > 0:
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).isoformat()
        record = {
            "token_id": token_id,
            "subject_id": subject_id,
            "name": name,
            "scopes": list(scopes or []),
            "metadata": dict(metadata or {}),
            "created_at": _utc_now_iso(),
            "expires_at": expires_at,
            "revoked": False,
            "token_hash": self._hash_token(plaintext_token),
        }
        with self._lock:
            self._token_hashes[token_id] = record
        return {"token": plaintext_token, "token_id": token_id, "record": {k: v for k, v in record.items() if k != "token_hash"}}

    async def verify_api_token(self, token: str) -> dict[str, Any] | None:
        if not token:
            return None
        parts = token.split("_", 2)
        if len(parts) != 3 or parts[0] != "xw":
            return None
        token_id = parts[1]
        with self._lock:
            record = self._token_hashes.get(token_id)
            if not record:
                return None
            if record.get("revoked"):
                return None
            expires_at = record.get("expires_at")
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
                return None
            if self._hash_token(token) != record.get("token_hash"):
                return None
            return {k: v for k, v in record.items() if k != "token_hash"}

    async def revoke_api_token(self, token_id: str) -> bool:
        with self._lock:
            record = self._token_hashes.get(token_id)
            if not record:
                return False
            record["revoked"] = True
            return True

    async def resolve_auth_context(self, token: str) -> AuthContext | None:
        claims = await self.verify_api_token(token)
        if not isinstance(claims, dict):
            return None
        claims_copy = dict(claims)
        return AuthContext(
            subject_id=str(claims_copy.get("subject_id") or ""),
            tenant_id=claims_copy.get("tenant_id") or claims_copy.get("tid"),
            scopes=list(claims_copy.get("scopes") or []),
            roles=list(claims_copy.get("roles") or []),
            session_id=claims_copy.get("session_id"),
            aal=claims_copy.get("aal"),
            claims=claims_copy,
            token_id=claims_copy.get("token_id"),
            token_type=str(claims_copy.get("token_type") or "api_token"),
        )


class XWAuthLibraryProvider(LocalAuthProvider):
    """
    xwauth library adapter.
    Falls back to local behavior when xwauth instance has no direct token API.
    """

    def __init__(self, auth: Any):
        super().__init__()
        self._auth = auth

    async def issue_api_token(
        self,
        *,
        subject_id: str,
        name: str,
        scopes: list[str],
        expires_in_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Keep local issuance for product API keys unless xwauth explicitly exposes issue_api_token.
        issuer = getattr(self._auth, "issue_api_token", None)
        if callable(issuer):
            issued = await issuer(
                subject_id=subject_id,
                name=name,
                scopes=scopes,
                expires_in_seconds=expires_in_seconds,
                metadata=metadata,
            )
            if isinstance(issued, dict):
                return issued
        return await super().issue_api_token(
            subject_id=subject_id,
            name=name,
            scopes=scopes,
            expires_in_seconds=expires_in_seconds,
            metadata=metadata,
        )

    async def verify_api_token(self, token: str) -> dict[str, Any] | None:
        resolver = getattr(self._auth, "resolve_auth_context", None)
        if callable(resolver):
            context = await resolver(token)
            if context:
                return self._context_to_claims(context)
        introspect = getattr(self._auth, "introspect_token", None)
        if callable(introspect):
            try:
                result = await introspect(token)
                if isinstance(result, dict) and bool(result.get("active", False)):
                    return self._normalize_introspection_claims(result)
            except Exception:
                pass
        # Backward compatible fallback to local tokens.
        return await super().verify_api_token(token)

    async def resolve_auth_context(self, token: str) -> AuthContext | None:
        resolver = getattr(self._auth, "resolve_auth_context", None)
        if callable(resolver):
            context = await resolver(token)
            if context:
                if isinstance(context, AuthContext):
                    return context
                return self._claims_to_context(self._context_to_claims(context))
        claims = await self.verify_api_token(token)
        if not isinstance(claims, dict):
            return None
        return self._claims_to_context(claims)

    @staticmethod
    def _context_to_claims(context: Any) -> dict[str, Any]:
        if isinstance(context, dict):
            return dict(context)
        claims = dict(getattr(context, "claims", {}) or {})
        claims.setdefault("subject_id", getattr(context, "subject_id", claims.get("subject_id")))
        claims.setdefault("tenant_id", getattr(context, "tenant_id", claims.get("tenant_id")))
        claims.setdefault("scopes", list(getattr(context, "scopes", claims.get("scopes", [])) or []))
        claims.setdefault("roles", list(getattr(context, "roles", claims.get("roles", [])) or []))
        claims.setdefault("session_id", getattr(context, "session_id", claims.get("session_id")))
        claims.setdefault("aal", getattr(context, "aal", claims.get("aal")))
        claims.setdefault("token_id", getattr(context, "token_id", claims.get("token_id")))
        claims.setdefault("token_type", getattr(context, "token_type", claims.get("token_type")))
        return claims

    @staticmethod
    def _normalize_introspection_claims(result: dict[str, Any]) -> dict[str, Any]:
        claims: dict[str, Any] = dict(result)
        subject_id = (
            result.get("subject_id")
            or result.get("sub")
            or result.get("user_id")
            or result.get("client_id")
            or ""
        )
        claims["subject_id"] = str(subject_id)
        scopes = result.get("scope")
        if isinstance(scopes, str):
            claims["scopes"] = [scope for scope in scopes.split(" ") if scope]
        else:
            claims["scopes"] = list(result.get("scopes") or [])
        claims.setdefault("roles", list(result.get("roles") or []))
        claims.setdefault("tenant_id", result.get("tenant_id") or result.get("tid"))
        claims.setdefault("token_type", result.get("token_type") or "bearer")
        return claims

    @staticmethod
    def _claims_to_context(claims: dict[str, Any]) -> AuthContext:
        claims_copy = dict(claims)
        return AuthContext(
            subject_id=str(claims_copy.get("subject_id") or ""),
            tenant_id=claims_copy.get("tenant_id") or claims_copy.get("tid"),
            scopes=list(claims_copy.get("scopes") or []),
            roles=list(claims_copy.get("roles") or []),
            session_id=claims_copy.get("session_id"),
            aal=claims_copy.get("aal"),
            claims=claims_copy,
            token_id=claims_copy.get("token_id"),
            token_type=claims_copy.get("token_type"),
        )


class InMemoryPaymentProvider(IPaymentProvider):
    """Simple ledger-style payment provider with subject balances."""

    def __init__(self):
        self._lock = RLock()
        self._balances: dict[str, float] = {}
        self._events: list[dict[str, Any]] = []
        self._consume_idempotency: dict[tuple[str, str], dict[str, Any]] = {}

    async def create_recharge(
        self,
        *,
        subject_id: str,
        amount: float,
        currency: str = "USD",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if amount <= 0:
            raise ValueError("amount must be > 0")
        with self._lock:
            md = dict(metadata or {})
            current = self._balances.get(subject_id, 0.0)
            updated = current + float(amount)
            self._balances[subject_id] = updated
            event = {
                "event_id": secrets.token_hex(8),
                "subject_id": subject_id,
                "amount": float(amount),
                "currency": currency,
                "status": "succeeded",
                "created_at": _utc_now_iso(),
                "metadata": md,
                "balance_after": updated,
            }
            if md.get("type") == "usage_compensation" and md.get("idempotency_key"):
                self._consume_idempotency.pop((subject_id, str(md["idempotency_key"])), None)
            self._events.append(event)
            return event

    async def get_balance(self, subject_id: str) -> float:
        with self._lock:
            return float(self._balances.get(subject_id, 0.0))

    async def consume_credits(
        self,
        *,
        subject_id: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        if amount <= 0:
            raise ValueError("amount must be > 0")
        md = dict(metadata or {})
        with self._lock:
            if idempotency_key:
                cached_key = (subject_id, idempotency_key)
                cached = self._consume_idempotency.get(cached_key)
                if cached is not None:
                    if float(cached["amount"]) != float(amount):
                        raise ValueError("idempotency key reuse with different amount")
                    replay = dict(cached["event"])
                    replay["balance_after"] = float(self._balances.get(subject_id, 0.0))
                    replay_meta = dict(replay.get("metadata") or {})
                    replay_meta["idempotent_replay"] = True
                    replay["metadata"] = replay_meta
                    return replay
            current = self._balances.get(subject_id, 0.0)
            if amount > current:
                raise ValueError("insufficient balance")
            updated = current - float(amount)
            self._balances[subject_id] = updated
            event = {
                "event_id": secrets.token_hex(8),
                "subject_id": subject_id,
                "amount": -float(amount),
                "currency": "USD",
                "status": "succeeded",
                "created_at": _utc_now_iso(),
                "metadata": md,
                "balance_after": updated,
            }
            self._events.append(event)
            if idempotency_key:
                self._consume_idempotency[(subject_id, idempotency_key)] = {
                    "amount": float(amount),
                    "event": dict(event),
                }
            return event
