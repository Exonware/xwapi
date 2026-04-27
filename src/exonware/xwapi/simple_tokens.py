#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/simple_tokens.py

Lightweight token store.

Distinct from :class:`APITokenManager` (which wires `IAuthProvider +
IStorageProvider + IPaymentProvider` for a full production tokenization
flow) — this module is the **minimum viable** API-token facility most
internal tools need:

* mint a bearer token scoped to one or more tenant ids,
* validate / rate-limit by last-used timestamp,
* revoke,
* list with redacted secrets.

Storage is pluggable via an ``ITokenPersistence`` protocol so the host
(hive-api, internal CLI, CI tool) decides where the tokens live — on
disk, in hive-db, or in a mock dict for tests. A
:class:`JSONFileTokenStore` default ships out of the box.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from exonware.xwsystem.io.serialization import JsonSerializer

_JSON = JsonSerializer()


@dataclass(slots=True)
class ApiToken:
    """Token record — the secret is never stored in plaintext."""

    id: str
    owner: str
    label: str
    prefix: str           # first 8 chars of the raw secret — shown in UI lists
    secret_hash: str      # sha256(secret) — what validate() compares against
    tenants: list[str]    # empty list = global access
    scopes: list[str]     # e.g. "read" / "write" / "admin"
    created_ts: float
    last_used_ts: float | None = None
    revoked_ts: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        return self.revoked_ts is None

    def covers_tenant(self, tenant: str | None) -> bool:
        if not self.tenants:
            return True  # global token
        if tenant is None:
            return False
        return tenant in self.tenants

    def covers_scope(self, scope: str | None) -> bool:
        if not self.scopes:
            return True
        if scope is None:
            return True
        return scope in self.scopes

    def redacted(self) -> dict[str, Any]:
        d = asdict(self)
        d["secret_hash"] = ""  # never ship to clients
        d["active"] = self.is_active()
        return d


@runtime_checkable
class ITokenPersistence(Protocol):
    """Minimal persistence contract — four methods, easy to mock."""

    def load_all(self) -> list[ApiToken]: ...
    def save(self, token: ApiToken) -> None: ...
    def delete(self, token_id: str) -> None: ...


class JSONFileTokenStore:
    """File-backed persistence — one JSON document per token."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[ApiToken]:
        out: list[ApiToken] = []
        for p in sorted(self._root.glob("*.json")):
            try:
                raw = _JSON.decode(p.read_text(encoding="utf-8"))
                raw.pop("active", None)  # derived field
                out.append(ApiToken(**raw))
            except Exception:
                continue
        return out

    def save(self, token: ApiToken) -> None:
        p = self._root / f"{token.id}.json"
        tmp = p.with_suffix(".json.tmp")
        encoded = _JSON.encode(asdict(token), options={"indent": 2})
        tmp.write_text(encoded.decode("utf-8") if isinstance(encoded, bytes) else encoded, encoding="utf-8")
        tmp.replace(p)

    def delete(self, token_id: str) -> None:
        p = self._root / f"{token_id}.json"
        if p.exists():
            p.unlink()


class SimpleTokenStore:
    """Process-level facade over an :class:`ITokenPersistence` adapter.

    Keeps an in-memory cache so :meth:`validate` is O(1) on the hot
    path. The cache is rebuilt lazily from the persistence layer on
    first access.
    """

    PREFIX = "hk_"
    TOKEN_LENGTH = 32  # bytes of entropy before hex-encode → 64-char hex

    def __init__(self, persistence: ITokenPersistence) -> None:
        self._persistence = persistence
        self._by_hash: dict[str, ApiToken] | None = None

    # ---- public API ----------------------------------------------------

    def create(
        self,
        *,
        owner: str,
        label: str = "",
        tenants: list[str] | None = None,
        scopes: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ApiToken, str]:
        """Mint a token. Returns ``(ApiToken record, raw_secret)``.

        The raw secret is returned ONCE here and never again. Callers
        are responsible for showing it to the end user immediately.
        """
        raw = f"{self.PREFIX}{secrets.token_hex(self.TOKEN_LENGTH)}"
        token_id = f"tok-{secrets.token_hex(6)}"
        record = ApiToken(
            id=token_id,
            owner=owner,
            label=label or token_id,
            prefix=raw[: len(self.PREFIX) + 8],
            secret_hash=_sha256(raw),
            tenants=list(tenants or []),
            scopes=list(scopes or []),
            created_ts=time.time(),
            metadata=dict(metadata or {}),
        )
        self._persistence.save(record)
        self._cache()[record.secret_hash] = record
        return record, raw

    def revoke(self, token_id: str) -> bool:
        """Mark a token as revoked. Returns True if it existed + was active."""
        for rec in self._cache().values():
            if rec.id == token_id and rec.is_active():
                rec.revoked_ts = time.time()
                self._persistence.save(rec)
                return True
        return False

    def delete(self, token_id: str) -> bool:
        """Hard-delete a token (remove from store + cache)."""
        hit = next((r for r in self._cache().values() if r.id == token_id), None)
        if hit is None:
            return False
        self._persistence.delete(token_id)
        self._cache().pop(hit.secret_hash, None)
        return True

    def list(self, *, include_revoked: bool = False) -> list[ApiToken]:
        items = list(self._cache().values())
        if not include_revoked:
            items = [t for t in items if t.is_active()]
        items.sort(key=lambda t: t.created_ts, reverse=True)
        return items

    def get(self, token_id: str) -> ApiToken | None:
        return next((r for r in self._cache().values() if r.id == token_id), None)

    def validate(
        self,
        raw_secret: str,
        *,
        tenant: str | None = None,
        scope: str | None = None,
    ) -> ApiToken | None:
        """Return the ApiToken record if `raw_secret` is active + covers
        the requested scope/tenant. Updates ``last_used_ts`` on success."""
        hit = self._cache().get(_sha256(raw_secret))
        if hit is None or not hit.is_active():
            return None
        if not hit.covers_tenant(tenant) or not hit.covers_scope(scope):
            return None
        hit.last_used_ts = time.time()
        # Best-effort persistence — a failure here should not fail the request.
        try:
            self._persistence.save(hit)
        except Exception:
            pass
        return hit

    # ---- internals -----------------------------------------------------

    def _cache(self) -> dict[str, ApiToken]:
        if self._by_hash is None:
            self._by_hash = {t.secret_hash: t for t in self._persistence.load_all()}
        return self._by_hash


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


__all__ = [
    "ApiToken",
    "ITokenPersistence",
    "JSONFileTokenStore",
    "SimpleTokenStore",
]
