from __future__ import annotations

import pytest
from types import SimpleNamespace
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from exonware.xwapi.server.middleware.auth import auth_middleware
from exonware.xwapi.server.middleware.tenant import tenant_middleware
from exonware.xwsystem.security.contracts import AuthContext


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


class _VerifyFallbackProvider:
    async def resolve_auth_context(self, token: str):
        _ = token
        return None

    async def verify_api_token(self, token: str):
        if token != "verify-token":
            return None
        return AuthContext(
            subject_id="verify-user",
            tenant_id="verify-tenant",
            scopes=["read:data"],
            roles=["reader"],
            claims={"sub": "verify-user", "tenant_id": "verify-tenant", "roles": ["reader"]},
        )


class _LegacyValidateProvider:
    async def validate_token(self, token: str):
        if token != "legacy-token":
            return None
        return {"sub": "legacy-user", "tenant_id": "legacy-tenant", "roles": ["legacy-role"]}


@pytest.mark.xwapi_integration
def test_auth_middleware_resolver_and_tenant_propagation() -> None:
    app = FastAPI()
    provider = _ResolverProvider()

    @app.middleware("http")
    async def _auth(request: Request, call_next):
        return await auth_middleware(request, call_next, require_auth=True, auth_provider=provider)

    @app.get("/whoami")
    async def whoami(request: Request):
        return JSONResponse(
            {
                "authenticated": getattr(request.state, "authenticated", False),
                "tenant_id": getattr(request.state, "tenant_id", None),
                "policy_context": getattr(request.state, "policy_context", None),
            }
        )

    client = TestClient(app, raise_server_exceptions=False)
    ok = client.get("/whoami", headers={"Authorization": "Bearer good-token"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["authenticated"] is True
    assert body["tenant_id"] == "tenant-abc"
    assert body["policy_context"]["tenant_id"] == "tenant-abc"
    assert body["policy_context"]["user_id"] == "user-42"

    bad = client.get("/whoami", headers={"Authorization": "Bearer bad-token"})
    assert bad.status_code == 200
    bad_body = bad.json()
    assert bad_body["authenticated"] is False
    assert bad_body["tenant_id"] is None


@pytest.mark.xwapi_integration
def test_auth_middleware_falls_back_to_verify_api_token() -> None:
    app = FastAPI()
    provider = _VerifyFallbackProvider()

    @app.middleware("http")
    async def _auth(request: Request, call_next):
        return await auth_middleware(request, call_next, require_auth=True, auth_provider=provider)

    @app.get("/whoami")
    async def whoami(request: Request):
        return JSONResponse(
            {
                "authenticated": getattr(request.state, "authenticated", False),
                "tenant_id": getattr(request.state, "tenant_id", None),
                "policy_context": getattr(request.state, "policy_context", None),
            }
        )

    client = TestClient(app, raise_server_exceptions=False)
    ok = client.get("/whoami", headers={"Authorization": "Bearer verify-token"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["authenticated"] is True
    assert body["tenant_id"] == "verify-tenant"
    assert body["policy_context"]["user_id"] == "verify-user"
    assert body["policy_context"]["roles"] == ["reader"]


@pytest.mark.xwapi_integration
def test_auth_middleware_falls_back_to_legacy_validate_token() -> None:
    app = FastAPI()
    provider = _LegacyValidateProvider()

    @app.middleware("http")
    async def _auth(request: Request, call_next):
        return await auth_middleware(request, call_next, require_auth=True, auth_provider=provider)

    @app.get("/whoami")
    async def whoami(request: Request):
        return JSONResponse(
            {
                "authenticated": getattr(request.state, "authenticated", False),
                "tenant_id": getattr(request.state, "tenant_id", None),
                "policy_context": getattr(request.state, "policy_context", None),
            }
        )

    client = TestClient(app, raise_server_exceptions=False)
    ok = client.get("/whoami", headers={"Authorization": "Bearer legacy-token"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["authenticated"] is True
    assert body["tenant_id"] == "legacy-tenant"
    assert body["policy_context"]["user_id"] == "legacy-user"
    assert body["policy_context"]["roles"] == ["legacy-role"]


@pytest.mark.xwapi_integration
def test_tenant_middleware_claims_then_header_then_query_precedence() -> None:
    app = FastAPI()

    @app.middleware("http")
    async def _tenant(request: Request, call_next):
        return await tenant_middleware(request, call_next)

    @app.middleware("http")
    async def _seed_claims(request: Request, call_next):
        request.state.claims = {"tenant_id": "claims-tenant", "tid": "claims-tid"}
        return await call_next(request)

    @app.get("/tenant")
    async def whoami(request: Request):
        return JSONResponse({"tenant_id": getattr(request.state, "tenant_id", None)})

    client = TestClient(app)
    response = client.get("/tenant?tenant_id=query-tenant", headers={"X-Tenant-Id": "header-tenant"})
    assert response.status_code == 200
    assert response.json()["tenant_id"] == "claims-tenant"


@pytest.mark.xwapi_integration
def test_auth_then_tenant_middleware_preserves_authenticated_tenant_over_header_and_query() -> None:
    app = FastAPI()
    provider = _ResolverProvider()

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
    ok = client.get(
        "/whoami?tenant_id=query-tenant",
        headers={"Authorization": "Bearer good-token", "X-Tenant-Id": "header-tenant"},
    )
    assert ok.status_code == 200
    assert ok.json()["tenant_id"] == "tenant-abc"


@pytest.mark.xwapi_integration
def test_tenant_middleware_rejects_conflicting_override_when_configured() -> None:
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
    bad = client.get(
        "/whoami?tenant_id=query-tenant",
        headers={"Authorization": "Bearer good-token", "X-Tenant-Id": "header-tenant"},
    )
    assert bad.status_code == 403
    bad_body = bad.json()
    assert bad_body["code"] == "AuthorizationError"
    assert bad_body["message"] == "Tenant override does not match authenticated tenant"

    ok = client.get(
        "/whoami?tenant_id=tenant-abc",
        headers={"Authorization": "Bearer good-token", "X-Tenant-Id": "tenant-abc"},
    )
    assert ok.status_code == 200
    assert ok.json()["tenant_id"] == "tenant-abc"


@pytest.mark.xwapi_integration
def test_tenant_middleware_requires_authenticated_source_when_configured() -> None:
    app = FastAPI()
    app.state.xwapi_server = SimpleNamespace(_tenant_require_authenticated_source=True)

    @app.middleware("http")
    async def _tenant(request: Request, call_next):
        return await tenant_middleware(request, call_next)

    @app.get("/tenant")
    async def whoami(request: Request):
        return JSONResponse({"tenant_id": getattr(request.state, "tenant_id", None)})

    client = TestClient(app)
    response = client.get("/tenant?tenant_id=query-tenant", headers={"X-Tenant-Id": "header-tenant"})
    assert response.status_code == 200
    assert response.json()["tenant_id"] is None
