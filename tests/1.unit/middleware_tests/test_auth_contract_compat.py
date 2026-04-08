from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from exonware.xwapi.contracts import AuthContext
from exonware.xwapi.server.middleware.auth import auth_middleware


class _ContextProvider:
    async def resolve_auth_context(self, token: str) -> AuthContext | None:
        if token == "ok-token":
            return AuthContext(
                subject_id="user-1",
                tenant_id="tenant-1",
                scopes=["read"],
                claims={"tid": "tenant-1"},
                token_id="tok-1",
            )
        if token == "claims-only-token":
            return AuthContext(
                subject_id="user-2",
                tenant_id=None,
                scopes=["read"],
                claims={"tid": "tenant-claims"},
                token_id="tok-2",
            )
        return None


class _LegacyProvider:
    async def validate_token(self, token: str) -> dict[str, str] | None:
        if token == "legacy-token":
            return {"sub": "legacy-user", "tenant_id": "tenant-legacy"}
        return None


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_prefers_resolve_auth_context() -> None:
    request = SimpleNamespace(
        headers={"Authorization": "Bearer ok-token"},
        cookies={},
        state=SimpleNamespace(),
    )
    response = SimpleNamespace(headers={})
    next_call = AsyncMock(return_value=response)

    result = await auth_middleware(request, next_call, auth_provider=_ContextProvider())
    assert result is response
    assert request.state.authenticated is True
    assert request.state.tenant_id == "tenant-1"
    assert isinstance(request.state.user, AuthContext)
    assert request.state.policy_context["tenant_id"] == "tenant-1"
    assert request.state.policy_context["user_id"] == "user-1"


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_supports_legacy_validate_token() -> None:
    request = SimpleNamespace(
        headers={"Authorization": "Bearer legacy-token"},
        cookies={},
        state=SimpleNamespace(),
    )
    response = SimpleNamespace(headers={})
    next_call = AsyncMock(return_value=response)

    result = await auth_middleware(request, next_call, auth_provider=_LegacyProvider())
    assert result is response
    assert request.state.authenticated is True
    assert request.state.tenant_id == "tenant-legacy"


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_falls_back_to_claim_tid() -> None:
    request = SimpleNamespace(
        headers={"Authorization": "Bearer claims-only-token"},
        cookies={},
        state=SimpleNamespace(),
    )
    response = SimpleNamespace(headers={})
    next_call = AsyncMock(return_value=response)

    result = await auth_middleware(request, next_call, auth_provider=_ContextProvider())
    assert result is response
    assert request.state.authenticated is True
    assert request.state.tenant_id == "tenant-claims"
