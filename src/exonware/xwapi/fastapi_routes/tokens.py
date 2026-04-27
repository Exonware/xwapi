"""FastAPI routes for :class:`xwapi.SimpleTokenStore`.

Mounts ``GET / POST / POST .../revoke / DELETE / POST /validate`` on a
caller-supplied :class:`APIRouter` so any product that wants bearer
token management gets the full surface in one call. The caller wires
up a ``get_store(request)`` factory (so the product controls where the
store lives on disk + how it's cached on ``app.state``), plus its auth
dependency and an optional audit-append callback.
"""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Iterable, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..simple_tokens import SimpleTokenStore


class _CreateIn(BaseModel):
    label: str = ""
    tenants: list[str] = []
    scopes: list[str] = []
    owner: str | None = None


class _ValidateIn(BaseModel):
    secret: str
    tenant: str | None = None
    scope: str | None = None


# Callback signatures -- products implement these against their own state.
GetStore = Callable[[Request], SimpleTokenStore]
GetActorEmail = Callable[[Any], str]
ListKnownTenants = Callable[[Request], Awaitable[Iterable[str]]]
class _AuditLike(Protocol):
    def append(self, **kwargs: Any) -> Any: ...


GetAudit = Callable[[Request], _AuditLike | None]


def mount_token_routes(
    router: APIRouter,
    *,
    user_dep: Callable[..., Any],
    get_store: GetStore,
    get_actor_email: GetActorEmail = lambda user: getattr(user, "email", "unknown"),
    list_known_tenants: ListKnownTenants | None = None,
    get_audit: GetAudit | None = None,
) -> None:
    """Attach API-token CRUD + validation routes to ``router``.

    - ``user_dep``: auth dependency (returns the current user object).
    - ``get_store``: ``Request -> SimpleTokenStore`` — the product owns
      the store's lifecycle (usually cached on ``app.state``).
    - ``get_actor_email``: how to derive the audit "actor" from the user
      object; defaults to ``user.email``.
    - ``list_known_tenants``: optional async check used to reject tokens
      scoped to unknown tenants. When ``None``, no validation runs.
    - ``get_audit``: optional ``Request -> AuditLog | None`` resolver —
      when present and non-None, every mutating route appends an entry
      with the same keyword arguments as :meth:`AuditLog.append`.
    """
    def _audit(request: Request, **kwargs: Any) -> None:
        if get_audit is None:
            return
        al = get_audit(request)
        if al is None:
            return
        al.append(**kwargs)

    @router.get("")
    async def list_tokens(
        request: Request,
        include_revoked: bool = False,
        _: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        store = get_store(request)
        return {"tokens": [t.redacted() for t in store.list(include_revoked=include_revoked)]}

    @router.post("")
    async def create_token(
        body: _CreateIn, request: Request, user: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        store = get_store(request)

        if body.tenants and list_known_tenants is not None:
            known = set(await list_known_tenants(request))
            missing = [t for t in body.tenants if t not in known]
            if missing:
                raise HTTPException(404, f"unknown tenant(s): {sorted(missing)}")

        record, raw = store.create(
            owner=body.owner or get_actor_email(user),
            label=body.label,
            tenants=body.tenants,
            scopes=body.scopes,
        )
        _audit(
            request,
            actor=get_actor_email(user), kind="resource.api-tokens",
            resource=record.id, action="create", ok=True,
            meta={"tenants": body.tenants, "scopes": body.scopes},
        )
        return {"token": record.redacted(), "secret": raw}

    @router.post("/{token_id}/revoke")
    async def revoke_token(
        token_id: str, request: Request, user: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        store = get_store(request)
        ok = store.revoke(token_id)
        if not ok:
            raise HTTPException(404, f"token {token_id} not active")
        _audit(
            request,
            actor=get_actor_email(user), kind="resource.api-tokens",
            resource=token_id, action="revoke", ok=True, meta={},
        )
        return {"ok": True, "token_id": token_id, "revoked_ts": time.time()}

    @router.delete("/{token_id}")
    async def delete_token(
        token_id: str, request: Request, user: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        store = get_store(request)
        ok = store.delete(token_id)
        if not ok:
            raise HTTPException(404, f"token {token_id} not found")
        _audit(
            request,
            actor=get_actor_email(user), kind="resource.api-tokens",
            resource=token_id, action="delete", ok=True, meta={},
        )
        return {"ok": True, "token_id": token_id}

    @router.post("/validate")
    async def validate_token(
        body: _ValidateIn, request: Request, _: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        store = get_store(request)
        record = store.validate(body.secret, tenant=body.tenant, scope=body.scope)
        if record is None:
            return {"valid": False}
        return {"valid": True, "token": record.redacted()}
