#!/usr/bin/env python3
"""
Core protocol conformance tests for xwapi provider contracts.
"""

import pytest

from exonware.xwapi.contracts import IAuthProvider, IStorageProvider
from exonware.xwapi.providers import LocalAuthProvider, InMemoryStorageProvider, XWAuthLibraryProvider
from exonware.xwsystem.security.contracts import AuthContext as SharedAuthContext


class _AuthContextLike:
    subject_id = "user-1"
    tenant_id = "tenant-1"
    scopes = ["read"]
    roles = ["member"]
    session_id = None
    aal = None
    claims = {"sub": "user-1", "tid": "tenant-1"}
    token_id = "tok-1"
    token_type = "bearer"


class _MockXWAuth:
    async def resolve_auth_context(self, token: str):
        if token == "ok":
            return _AuthContextLike()
        return None


class _MockXWAuthIntrospectionOnly:
    def __init__(self) -> None:
        self.introspect_called = False
        self.private_token_manager_used = False
        self._token_manager = self

    async def resolve_auth_context(self, token: str):
        _ = token
        return None

    async def introspect_token(self, token: str):
        self.introspect_called = True
        if token == "introspect-ok":
            return {
                "active": True,
                "sub": "user-introspect",
                "scope": "read write",
                "tid": "tenant-introspect",
                "roles": ["member"],
                "token_type": "bearer",
            }
        return {"active": False}

    # If provider attempted to call private token manager, we can detect it.
    async def __call__(self, *args, **kwargs):
        self.private_token_manager_used = True
        _ = args
        _ = kwargs
        return {"active": False}


@pytest.mark.xwapi_core
def test_default_providers_conform_to_protocols() -> None:
    assert isinstance(LocalAuthProvider(), IAuthProvider)
    assert isinstance(InMemoryStorageProvider(), IStorageProvider)


@pytest.mark.xwapi_core
@pytest.mark.asyncio
async def test_xwauth_library_provider_conforms_and_normalizes_context() -> None:
    provider = XWAuthLibraryProvider(_MockXWAuth())
    assert isinstance(provider, IAuthProvider)
    context = await provider.resolve_auth_context("ok")
    assert context is not None
    assert context.subject_id == "user-1"
    assert context.tenant_id == "tenant-1"


@pytest.mark.xwapi_core
@pytest.mark.asyncio
async def test_xwauth_library_provider_uses_public_introspection_surface() -> None:
    auth = _MockXWAuthIntrospectionOnly()
    provider = XWAuthLibraryProvider(auth)
    context = await provider.resolve_auth_context("introspect-ok")
    assert auth.introspect_called is True
    assert context is not None
    assert context.subject_id == "user-introspect"
    assert context.tenant_id == "tenant-introspect"
    assert sorted(context.scopes) == ["read", "write"]


@pytest.mark.xwapi_core
def test_xwapi_auth_context_reuses_xwsystem_contract() -> None:
    from exonware.xwapi.contracts import AuthContext

    assert AuthContext is SharedAuthContext
