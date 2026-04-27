# exonware/xwapi/src/exonware/xwapi/service_surface.py
"""
Shared **transport metadata** routes (health + JSON surface) for deployable ``*-api`` hosts.

Domain endpoints stay in their owning libraries (``xwauth``, ``xwstorage.connect.api``, …); this module
only centralizes the xwapi/xwaction/xwschema wiring so every HTTP deploy package exposes the same
operational baseline (parity with reference AS stacks that publish ``/health``-style probes plus
machine-readable capability maps).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any


def _norm_prefix(route_prefix: str) -> str:
    p = (route_prefix or "").strip()
    if not p.startswith("/"):
        raise ValueError("route_prefix must start with '/'")
    return p.rstrip("/") or "/"


def normalize_route_prefix(route_prefix: str) -> str:
    """Shared prefix normalization for deploy hosts (health/surface/deploy-root wiring)."""
    return _norm_prefix(route_prefix)


def _op_token(service_key: str) -> str:
    t = "".join(ch if ch.isalnum() else "_" for ch in service_key).strip("_")
    return t or "service"


def register_xw_service_surface_routes(
    app: Any,
    *,
    service_key: str,
    route_prefix: str,
    package_version: str,
    describe: Callable[[], dict[str, Any]],
    extra_tags: Sequence[str] | None = None,
) -> None:
    """
    Register ``GET {prefix}/health`` and ``GET {prefix}/surface`` as :class:`~exonware.xwaction.facade.XWAction`
    endpoints on an xwapi FastAPI runtime ``app`` (``XWApiServer(...).app``).

    Idempotent per ``(service_key, route_prefix)`` pair using ``app.state``.
    """
    if app is None:
        raise TypeError("app is required")
    base = _norm_prefix(route_prefix)
    reg: set[str] = getattr(app.state, "xwapi_service_surface_keys", None) or set()
    dedupe_key = f"{service_key}@{base}"
    if dedupe_key in reg:
        return

    from exonware.xwaction import XWAction
    from exonware.xwaction.defs import ActionParameter, ActionProfile
    from exonware.xwapi.action import register_action_endpoint
    from exonware.xwschema.types_base import schema_for

    tags = ["System", *(extra_tags or ())]
    suffix = _op_token(service_key)
    bool_schema = schema_for("boolean_json") or schema_for("boolean")
    if bool_schema is None:
        raise RuntimeError("xwschema types_base missing boolean_json schema")
    bool_json = dict(bool_schema.to_native())

    @XWAction(
        operationId=f"xw_service_{suffix}_health",
        summary="Service health",
        description="Liveness-style JSON probe for load balancers and deploy hooks.",
        method="GET",
        engine="fastapi",
        profile=ActionProfile.ENDPOINT,
        tags=list(tags),
        parameters=[
            ActionParameter(
                "detailed",
                param_type=bool,
                required=False,
                default=False,
                description="When true, include optional diagnostic hints safe for public probes.",
                schema=bool_json,
            ),
        ],
        responses={
            200: {"description": "Service is reachable and reporting version metadata."},
            503: {"description": "Reserved for future degraded / readiness semantics."},
        },
        examples={
            "default": {
                "summary": "Healthy",
                "value": {"status": "ok", "service": service_key, "version": package_version},
            }
        },
    )
    def xw_service_health(detailed: bool = False) -> dict[str, Any]:
        body: dict[str, Any] = {
            "status": "ok",
            "service": service_key,
            "version": package_version,
        }
        if detailed:
            body["detail"] = {"transport": "xwapi+xwaction", "surface": f"{base}/surface"}
        return body

    @XWAction(
        operationId=f"xw_service_{suffix}_surface",
        summary="Service surface metadata",
        description="Stable JSON for discovery pages, admin consoles, and contract tests.",
        method="GET",
        engine="fastapi",
        profile=ActionProfile.ENDPOINT,
        tags=list(tags),
        parameters=[
            ActionParameter(
                "format",
                param_type=str,
                required=False,
                default="json",
                enum=["json"],
                description="Reserved for future encodings; only json is supported today.",
            ),
        ],
        responses={200: {"description": "JSON surface describing package, library, and optional versions."}},
        examples={
            "default": {
                "summary": "Surface",
                "value": {
                    "service": service_key,
                    "version": package_version,
                    "xwapi_surface": "xwapi.service_surface.v1",
                },
            }
        },
    )
    def xw_service_surface(format: str = "json") -> dict[str, Any]:
        _ = format
        payload = describe()
        payload.setdefault("service", service_key)
        payload.setdefault("version", package_version)
        payload.setdefault("xwapi_surface", "xwapi.service_surface.v1")
        return payload

    health_path = f"{base}/health" if base != "/" else "/health"
    surface_path = f"{base}/surface" if base != "/" else "/surface"
    if not register_action_endpoint(app, xw_service_health, path=health_path, method="GET"):
        raise RuntimeError(f"failed to register health route: GET {health_path}")
    if not register_action_endpoint(app, xw_service_surface, path=surface_path, method="GET"):
        raise RuntimeError(f"failed to register surface route: GET {surface_path}")

    reg = set(reg)
    reg.add(dedupe_key)
    app.state.xwapi_service_surface_keys = reg
