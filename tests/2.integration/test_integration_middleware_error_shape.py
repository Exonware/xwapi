from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from exonware.xwapi.server.middleware.admin_auth import AdminTokenMiddleware
from exonware.xwapi.server.middleware.api_token import APITokenMiddleware
from exonware.xwapi.server.middleware.auth import auth_middleware
from exonware.xwapi.server.middleware.tenant import tenant_middleware
from exonware.xwapi.server.engines.fastapi import http_exception_handler
from exonware.xwsystem.security.contracts import AuthContext

_STABLE_TOP_LEVEL_KEYS = frozenset({"code", "message", "trace_id", "details", "hint"})


def _assert_error_envelope(
    body: dict,
    *,
    code: str,
    message: str,
    detail_keys: frozenset[str],
) -> None:
    assert frozenset(body.keys()) == _STABLE_TOP_LEVEL_KEYS
    assert body["code"] == code
    assert body["message"] == message
    assert isinstance(body["trace_id"], str) and body["trace_id"]
    assert isinstance(body["hint"], str) and body["hint"]
    assert isinstance(body["details"], dict)
    assert frozenset(body["details"].keys()) == detail_keys


def _assert_http_exception_envelope(
    body: dict,
    *,
    code: str,
    message: str,
    status_code: int,
) -> None:
    assert {"code", "message", "trace_id", "details"}.issubset(set(body.keys()))
    assert body["code"] == code
    assert body["message"] == message
    assert isinstance(body["trace_id"], str) and body["trace_id"]
    assert isinstance(body["details"], dict)
    assert body["details"]["status_code"] == status_code


class _ResolverProvider:
    async def resolve_auth_context(self, token: str):
        if token != "good-token":
            return None
        return AuthContext(
            subject_id="user-42",
            tenant_id="tenant-abc",
            scopes=["read:data"],
            roles=["member"],
            claims={"sub": "user-42", "tenant_id": "tenant-abc", "roles": ["member"]},
        )


@pytest.mark.xwapi_integration
def test_tenant_conflict_returns_uniform_xwapi_error_shape() -> None:
    app = FastAPI()
    provider = _ResolverProvider()
    app.state.xwapi_server = SimpleNamespace(_tenant_reject_conflicting_override=True)

    @app.middleware("http")
    async def _tenant(request: Request, call_next):
        return await tenant_middleware(request, call_next)

    @app.middleware("http")
    async def _auth(request: Request, call_next):
        return await auth_middleware(request, call_next, require_auth=True, auth_provider=provider)

    @app.get("/whoami")
    async def whoami(request: Request):
        return JSONResponse({"tenant_id": getattr(request.state, "tenant_id", None)})

    client = TestClient(app)
    response = client.get(
        "/whoami?tenant_id=query-tenant",
        headers={"Authorization": "Bearer good-token", "X-Tenant-Id": "header-tenant"},
    )
    assert response.status_code == 403
    body = response.json()
    _assert_error_envelope(
        body,
        code="AuthorizationError",
        message="Tenant override does not match authenticated tenant",
        detail_keys=frozenset({"principal_tenant", "header_tenant", "query_tenant"}),
    )


@pytest.mark.xwapi_integration
def test_admin_auth_returns_uniform_error_shape_and_bearer_header() -> None:
    app = FastAPI()
    app.state.xwapi_server = SimpleNamespace(
        _admin_token="admin-secret",
        _admin_auth_prefixes={"/server"},
        _admin_protect_reads=True,
    )
    app.add_middleware(AdminTokenMiddleware)

    @app.get("/server/status")
    async def server_status():
        return JSONResponse({"status": "ok"})

    client = TestClient(app)
    response = client.get("/server/status")
    assert response.status_code == 401
    body = response.json()
    _assert_error_envelope(
        body,
        code="AuthenticationError",
        message="Admin authentication required",
        detail_keys=frozenset({"path", "method"}),
    )
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.xwapi_integration
def test_api_token_middleware_returns_uniform_error_shape_and_bearer_header() -> None:
    app = FastAPI()
    app.state.xwapi_server = SimpleNamespace(
        _api_token_middleware_enabled=True,
        _api_token_require_bearer=True,
        _api_token_exempt_paths=set(),
        _admin_auth_prefixes=set(),
        _admin_token=None,
        _api_token_enforce_scopes=False,
    )
    app.add_middleware(APITokenMiddleware)

    @app.get("/protected")
    async def protected():
        return JSONResponse({"ok": True})

    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 401
    body = response.json()
    _assert_error_envelope(
        body,
        code="AuthenticationError",
        message="API bearer token required",
        detail_keys=frozenset({"path", "method"}),
    )
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.xwapi_integration
def test_fastapi_http_exception_preserves_www_authenticate_header() -> None:
    app = FastAPI()
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    @app.get("/auth-error")
    async def auth_error():
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    client = TestClient(app)
    response = client.get("/auth-error")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == 'Bearer error="invalid_token"'
    body = response.json()
    _assert_http_exception_envelope(
        body,
        code="AuthenticationError",
        message="Token expired",
        status_code=401,
    )


@pytest.mark.xwapi_integration
def test_starlette_http_exception_preserves_custom_headers() -> None:
    app = FastAPI()
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    @app.get("/rate-limit-error")
    async def rate_limit_error():
        raise StarletteHTTPException(
            status_code=429,
            detail="Slow down",
            headers={"Retry-After": "120", "X-RateLimit-Remaining": "0"},
        )

    client = TestClient(app)
    response = client.get("/rate-limit-error")
    assert response.status_code == 429
    assert response.headers.get("Retry-After") == "120"
    assert response.headers.get("X-RateLimit-Remaining") == "0"
    body = response.json()
    _assert_http_exception_envelope(
        body,
        code="RateLimitError",
        message="Slow down",
        status_code=429,
    )
