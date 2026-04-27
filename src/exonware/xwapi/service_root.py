# exonware/xwapi/src/exonware/xwapi/service_root.py
"""
Deploy-host ``GET /`` metadata using :class:`~exonware.xwaction.facade.XWAction` + ``register_action_endpoint``.

Keeps thin ``*-api`` runners aligned on discovery links (health/surface/docs) without ad-hoc FastAPI routes.
"""

from __future__ import annotations

from typing import Any

from exonware.xwapi.action import register_action_endpoint
from exonware.xwapi.service_surface import normalize_route_prefix


def register_deploy_host_root_action(
    app: Any,
    *,
    service_key: str,
    route_prefix: str,
    docs_path: str = "/docs",
    openapi_path: str = "/openapi.json",
    metrics_path: str | None = None,
    extra: dict[str, Any] | None = None,
) -> bool:
    """
    Register ``GET /`` returning JSON navigation hints for operators (xwaction-only).

    Idempotent per ``app.state.xwapi_deploy_root_registered``.
    """
    if app is None:
        raise TypeError("app is required")
    base = normalize_route_prefix(route_prefix)
    flag = getattr(app.state, "xwapi_deploy_root_registered", False)
    if flag:
        return True

    from exonware.xwaction import XWAction
    from exonware.xwaction.defs import ActionProfile
    from exonware.xwschema.types_base import schema_for

    op_id = "".join(ch if ch.isalnum() else "_" for ch in service_key).strip("_") or "service"
    out_schema = schema_for("json_object")
    out_types = {"return": out_schema} if out_schema is not None else {}

    health_path = f"{base}/health" if base != "/" else "/health"
    surface_path = f"{base}/surface" if base != "/" else "/surface"

    @XWAction(
        operationId=f"{op_id}_deploy_root",
        summary="Deploy host metadata",
        description="Stable JSON describing service key, probe paths, and documentation links.",
        method="GET",
        engine="fastapi",
        profile=ActionProfile.ENDPOINT,
        tags=["System"],
        out_types=out_types or None,
        responses={200: {"description": "Deploy navigation payload for operators and smoke tests."}},
    )
    def deploy_root() -> dict[str, Any]:
        body: dict[str, Any] = {
            "service": service_key,
            "health": health_path,
            "surface": surface_path,
            "docs": docs_path,
            "openapi": openapi_path,
            "xwapi_transport": "xwapi+xwaction",
        }
        if metrics_path:
            body["metrics"] = metrics_path
        if extra:
            body.update(extra)
        return body

    ok = register_action_endpoint(app, deploy_root, path="/", method="GET")
    if ok:
        app.state.xwapi_deploy_root_registered = True
    return ok
