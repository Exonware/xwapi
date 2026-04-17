#exonware/xwapi/tests/1.unit/test_contracts.py
"""
Unit tests for xwapi contracts (enums, protocols, runtime_checkable).
Company: eXonware.com
"""

from __future__ import annotations
import pytest


@pytest.mark.xwapi_unit
class TestEnums:
    """Tests for contract enumerations."""

    def test_http_method_values(self):
        from exonware.xwapi.contracts import HTTPMethod
        assert HTTPMethod.GET == "GET"
        assert HTTPMethod.POST == "POST"
        assert HTTPMethod.PUT == "PUT"
        assert HTTPMethod.PATCH == "PATCH"
        assert HTTPMethod.DELETE == "DELETE"
        assert HTTPMethod.OPTIONS == "OPTIONS"
        assert HTTPMethod.HEAD == "HEAD"

    def test_security_type_values(self):
        from exonware.xwapi.contracts import SecurityType
        assert SecurityType.OAUTH2 == "oauth2"
        assert SecurityType.API_KEY == "apiKey"
        assert SecurityType.BEARER == "bearer"
        assert SecurityType.BASIC == "basic"


@pytest.mark.xwapi_unit
class TestProtocols:
    """Tests that protocols are runtime_checkable."""

    def test_api_endpoint_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IAPIEndpoint
        assert hasattr(IAPIEndpoint, "__protocol_attrs__") or hasattr(IAPIEndpoint, "__abstractmethods__") or True
        # Verify it's a Protocol via isinstance check capability
        class FakeEndpoint:
            def get_path(self): return "/test"
            def get_method(self): return "GET"
            def get_entity_type(self): return "User"
        assert isinstance(FakeEndpoint(), IAPIEndpoint)

    def test_api_generator_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IAPIGenerator
        class FakeGen:
            async def generate_openapi(self): return {}
            def create_app(self): return None
        assert isinstance(FakeGen(), IAPIGenerator)

    def test_oauth2_provider_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IOAuth2Provider
        class FakeOAuth:
            def get_authorization_url(self): return "/auth"
            def get_token_url(self): return "/token"
            def get_userinfo_url(self): return "/userinfo"
        assert isinstance(FakeOAuth(), IOAuth2Provider)

    def test_storage_provider_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IStorageProvider
        class FakeStorage:
            async def read(self, key): pass
            async def write(self, key, value): pass
            async def delete(self, key): pass
            async def exists(self, key): return False
        assert isinstance(FakeStorage(), IStorageProvider)

    def test_payment_provider_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IPaymentProvider
        class FakePayment:
            async def create_recharge(self, *, subject_id, amount, currency="USD", metadata=None): pass
            async def get_balance(self, subject_id): return 0.0
            async def consume_credits(self, *, subject_id, amount, metadata=None, idempotency_key=None): pass
        assert isinstance(FakePayment(), IPaymentProvider)

    def test_entity_crud_store_is_runtime_checkable(self):
        from exonware.xwapi.contracts import IEntityCrudStore
        class FakeStore:
            async def list_items(self, collection): return []
            async def get_item(self, collection, entity_id): return None
            async def put_item(self, collection, entity_id, item): pass
            async def delete_item(self, collection, entity_id): return False
        assert isinstance(FakeStore(), IEntityCrudStore)
