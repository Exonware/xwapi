# exonware/xwapi/src/exonware/xwapi/server/compose.py
"""
Composable FastAPI server merge helpers for XWApiServer-based hosts.

This keeps deployment DX simple: run one process, merge multiple service servers, and
optionally namespace each service under a prefix without rewriting route definitions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from fastapi import APIRouter
from fastapi.routing import APIRoute, APIWebSocketRoute

from exonware.xwapi.service_surface import normalize_route_prefix

ConflictPolicy = Literal["error", "skip"]

_RESERVED_INFRA_PATHS: frozenset[str] = frozenset(
    {
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
    }
)


@dataclass(frozen=True, slots=True)
class XWApiComposeSpec:
    """
    One child server/app to merge into a host app.

    - ``server_or_app``: ``XWApiServer`` instance or FastAPI app-like object.
    - ``prefix``: optional child namespace prefix (must start with ``/`` when provided).
    - ``include_root_routes``: include child ``/`` routes (disabled by default to avoid root conflicts).
    """

    server_or_app: Any
    prefix: str | None = None
    include_root_routes: bool = False
    name: str | None = None


@dataclass(frozen=True, slots=True)
class XWApiComposeOptions:
    """Global composition options shared by all child merge specs."""

    global_prefix: str | None = None
    conflict_policy: ConflictPolicy = "error"
    strip_framework_infra_routes: bool = True


def compose_xwapi_servers(
    host_server_or_app: Any,
    specs: Sequence[XWApiComposeSpec],
    *,
    options: XWApiComposeOptions | None = None,
) -> Any:
    """
    Merge child FastAPI route surfaces into a host app.

    The host can be an ``XWApiServer`` or a FastAPI app-like object exposing ``include_router``.
    Child routes are copied route-by-route (not mounted) so they behave like one merged API host.
    """
    if not specs:
        return _resolve_app(host_server_or_app)
    cfg = options or XWApiComposeOptions()
    host_app = _resolve_app(host_server_or_app)
    _assert_fastapi_router_capability(host_app, role="host")
    _ensure_host_prefixed_surface(host_app, global_prefix=cfg.global_prefix)
    existing = _collect_route_signatures(host_app)

    for spec in specs:
        child_app = _resolve_app(spec.server_or_app)
        _assert_fastapi_router_capability(child_app, role=f"child {spec.name or '<unnamed>'}")
        combined_prefix = _combine_prefixes(cfg.global_prefix, spec.prefix)
        child_router = _build_filtered_router(
            child_app,
            include_root_routes=spec.include_root_routes,
            strip_framework_infra_routes=cfg.strip_framework_infra_routes,
        )
        _apply_conflict_policy(
            host_app=host_app,
            child_router=child_router,
            child_name=spec.name or _infer_name(spec.server_or_app),
            combined_prefix=combined_prefix,
            existing_signatures=existing,
            conflict_policy=cfg.conflict_policy,
        )
        if child_router.routes:
            host_app.include_router(child_router, prefix=combined_prefix)
            existing = _collect_route_signatures(host_app)
    return host_app


def _ensure_host_prefixed_surface(host_app: Any, *, global_prefix: str | None) -> None:
    """Mirror host routes under global_prefix so composed surfaces share one namespace."""
    prefix = _normalize_optional_prefix(global_prefix)
    if not prefix:
        return
    host_router = _build_filtered_router(
        host_app,
        include_root_routes=True,
        strip_framework_infra_routes=True,
    )
    if not host_router.routes:
        return
    existing = _collect_route_signatures(host_app)
    _drop_conflicting_routes(
        child_router=host_router,
        combined_prefix=prefix,
        existing_signatures=existing,
    )
    if host_router.routes:
        host_app.include_router(host_router, prefix=prefix)


def _build_filtered_router(
    app: Any,
    *,
    include_root_routes: bool,
    strip_framework_infra_routes: bool,
) -> APIRouter:
    router = APIRouter()
    for route in getattr(app.router, "routes", []):
        path = getattr(route, "path", "")
        if not isinstance(path, str) or not path.startswith("/"):
            continue
        if path == "/" and not include_root_routes:
            continue
        if strip_framework_infra_routes and path in _RESERVED_INFRA_PATHS:
            continue
        if isinstance(route, APIRoute):
            router.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                response_model=route.response_model,
                status_code=route.status_code,
                tags=route.tags,
                dependencies=route.dependencies,
                summary=route.summary,
                description=route.description,
                response_description=route.response_description,
                responses=route.responses,
                deprecated=route.deprecated,
                methods=route.methods,
                operation_id=route.operation_id,
                response_model_include=route.response_model_include,
                response_model_exclude=route.response_model_exclude,
                response_model_by_alias=route.response_model_by_alias,
                response_model_exclude_unset=route.response_model_exclude_unset,
                response_model_exclude_defaults=route.response_model_exclude_defaults,
                response_model_exclude_none=route.response_model_exclude_none,
                include_in_schema=route.include_in_schema,
                name=route.name,
                callbacks=route.callbacks,
                openapi_extra=route.openapi_extra,
                generate_unique_id_function=route.generate_unique_id_function,
            )
        elif isinstance(route, APIWebSocketRoute):
            router.add_api_websocket_route(
                path=route.path,
                endpoint=route.endpoint,
                name=route.name,
                dependencies=route.dependencies,
            )
    return router


def _apply_conflict_policy(
    *,
    host_app: Any,
    child_router: APIRouter,
    child_name: str,
    combined_prefix: str,
    existing_signatures: set[str],
    conflict_policy: ConflictPolicy,
) -> None:
    if conflict_policy not in ("error", "skip"):
        raise ValueError("conflict_policy must be one of: 'error', 'skip'")
    if conflict_policy == "skip":
        _drop_conflicting_routes(
            child_router=child_router,
            combined_prefix=combined_prefix,
            existing_signatures=existing_signatures,
        )
        return

    conflicts: list[str] = []
    for signature in _collect_router_signatures(child_router, prefix=combined_prefix):
        if signature in existing_signatures:
            conflicts.append(signature)
    if conflicts:
        preview = ", ".join(conflicts[:3])
        suffix = "" if len(conflicts) <= 3 else f" (+{len(conflicts) - 3} more)"
        raise ValueError(
            f"route conflict while merging '{child_name}': {preview}{suffix}. "
            "Use prefixes or conflict_policy='skip'."
        )


def _drop_conflicting_routes(
    *,
    child_router: APIRouter,
    combined_prefix: str,
    existing_signatures: set[str],
) -> None:
    kept: list[Any] = []
    for route in child_router.routes:
        if _route_is_conflicting(route, combined_prefix=combined_prefix, existing_signatures=existing_signatures):
            continue
        kept.append(route)
    child_router.routes = kept


def _route_is_conflicting(route: Any, *, combined_prefix: str, existing_signatures: set[str]) -> bool:
    for signature in _route_signature_items(route, prefix=combined_prefix):
        if signature in existing_signatures:
            return True
    return False


def _collect_route_signatures(app: Any) -> set[str]:
    signatures: set[str] = set()
    for route in getattr(app.router, "routes", []):
        signatures.update(_route_signature_items(route, prefix=""))
    return signatures


def _collect_router_signatures(router: APIRouter, *, prefix: str) -> set[str]:
    signatures: set[str] = set()
    for route in router.routes:
        signatures.update(_route_signature_items(route, prefix=prefix))
    return signatures


def _route_signature_items(route: Any, *, prefix: str) -> set[str]:
    if isinstance(route, APIRoute):
        path = _join_paths(prefix, route.path)
        methods = set(route.methods or set())
        methods.discard("HEAD")
        methods.discard("OPTIONS")
        if not methods:
            methods = {"GET"}
        return {f"{m}:{path}" for m in methods}
    if isinstance(route, APIWebSocketRoute):
        path = _join_paths(prefix, route.path)
        return {f"WS:{path}"}
    return set()


def _resolve_app(server_or_app: Any) -> Any:
    app = getattr(server_or_app, "app", None)
    return app if app is not None else server_or_app


def _assert_fastapi_router_capability(app: Any, *, role: str) -> None:
    if app is None or not hasattr(app, "router") or not hasattr(app, "include_router"):
        raise TypeError(f"{role} must be a FastAPI app or XWApiServer with a FastAPI app.")


def _combine_prefixes(global_prefix: str | None, local_prefix: str | None) -> str:
    g = _normalize_optional_prefix(global_prefix)
    l = _normalize_optional_prefix(local_prefix)
    # Avoid accidental double-prefixing when both prefixes are the same.
    # This keeps conflict detection behavior deterministic (e.g. /x + /x => /x).
    if g and l and g == l:
        return g
    return _join_paths(g, l)


def _normalize_optional_prefix(prefix: str | None) -> str:
    if prefix is None:
        return ""
    raw = prefix.strip()
    if not raw:
        return ""
    normalized = normalize_route_prefix(raw)
    return "" if normalized == "/" else normalized


def _join_paths(left: str, right: str) -> str:
    l = (left or "").rstrip("/")
    r = (right or "").strip()
    if not r:
        return l
    if not r.startswith("/"):
        raise ValueError("prefix must start with '/'")
    if not l:
        return r
    return f"{l}{r}"


def _infer_name(server_or_app: Any) -> str:
    return type(server_or_app).__name__
