"""FastAPI routes for a persisted JSON theme document.

Thin wrapper that stores a single JSON configuration on disk under a
caller-supplied path. Used by products (HIVE API, …) that want the
xwui "custom" theme config to follow the installation rather than the
browser. The payload is intentionally untyped — UIs evolve, and this
endpoint is a blind pass-through.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from exonware.xwsystem.io.serialization import JsonSerializer

_JSON = JsonSerializer()


class _ThemeIn(BaseModel):
    config: dict[str, Any]


class _AuditLike(Protocol):
    def append(self, **kwargs: Any) -> Any: ...


GetPath = Callable[[Request], Path]
GetActorEmail = Callable[[Any], str]
GetAudit = Callable[[Request], _AuditLike | None]


def mount_theme_routes(
    router: APIRouter,
    *,
    user_dep: Callable[..., Any],
    get_path: GetPath,
    get_actor_email: GetActorEmail = lambda user: getattr(user, "email", "unknown"),
    get_audit: GetAudit | None = None,
    audit_kind: str = "resource.theme-custom",
    audit_resource: str = "theme.custom",
) -> None:
    """Attach ``GET / PUT / DELETE /custom`` routes to ``router``.

    - ``user_dep``: auth dependency (returns current user).
    - ``get_path``: ``Request -> Path`` pointing at the JSON document.
      The caller ensures the parent directory is created.
    - ``get_actor_email``: audit actor extractor (defaults to ``user.email``).
    - ``get_audit``: optional ``Request -> AuditLog | None`` resolver.
    - ``audit_kind`` / ``audit_resource``: identifiers used when
      auditing is enabled.
    """
    def _audit(request: Request, **kwargs: Any) -> None:
        if get_audit is None:
            return
        al = get_audit(request)
        if al is None:
            return
        al.append(**kwargs)

    @router.get("/custom")
    async def get_custom(request: Request, _: Any = Depends(user_dep)) -> dict[str, Any]:
        p = get_path(request)
        if not p.exists():
            return {"config": {}, "exists": False}
        try:
            raw = _JSON.decode(p.read_text(encoding="utf-8"))
        except Exception as err:  # noqa: BLE001
            raise HTTPException(500, f"invalid theme document: {err}") from err
        return {"config": raw.get("config", {}), "exists": True}

    @router.put("/custom")
    async def put_custom(
        body: _ThemeIn, request: Request, user: Any = Depends(user_dep),
    ) -> dict[str, Any]:
        p = get_path(request)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        encoded = _JSON.encode(
            {"config": body.config, "updated_by": get_actor_email(user)},
            options={"indent": 2},
        )
        tmp.write_text(
            encoded.decode("utf-8") if isinstance(encoded, bytes) else encoded,
            encoding="utf-8",
        )
        tmp.replace(p)
        _audit(
            request,
            actor=get_actor_email(user), kind=audit_kind,
            resource=audit_resource, action="update", ok=True,
            meta={"keys": sorted(body.config.keys())[:20]},
        )
        return {"ok": True, "keys": sorted(body.config.keys())}

    @router.delete("/custom")
    async def reset_custom(request: Request, user: Any = Depends(user_dep)) -> dict[str, Any]:
        p = get_path(request)
        existed = p.exists()
        if existed:
            p.unlink()
        _audit(
            request,
            actor=get_actor_email(user), kind=audit_kind,
            resource=audit_resource, action="reset", ok=existed, meta={},
        )
        return {"ok": True, "removed": existed}
