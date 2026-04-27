#exonware/xwapi/tests/1.unit/test_contracts_enums.py
"""
Unit tests for xwapi contracts — enums and protocol conformance.
"""

from __future__ import annotations

import pytest


@pytest.mark.xwapi_unit
class TestHTTPMethodEnum:

    def test_values(self):
        from exonware.xwapi.contracts import HTTPMethod
        assert HTTPMethod.GET == "GET"
        assert HTTPMethod.POST == "POST"
        assert HTTPMethod.PUT == "PUT"
        assert HTTPMethod.PATCH == "PATCH"
        assert HTTPMethod.DELETE == "DELETE"
        assert HTTPMethod.OPTIONS == "OPTIONS"
        assert HTTPMethod.HEAD == "HEAD"

    def test_is_str(self):
        from exonware.xwapi.contracts import HTTPMethod
        assert isinstance(HTTPMethod.GET, str)


@pytest.mark.xwapi_unit
class TestSecurityTypeEnum:

    def test_values(self):
        from exonware.xwapi.contracts import SecurityType
        assert SecurityType.OAUTH2 == "oauth2"
        assert SecurityType.API_KEY == "apiKey"
        assert SecurityType.BEARER == "bearer"
        assert SecurityType.BASIC == "basic"


@pytest.mark.xwapi_unit
class TestProtocolConformance:

    def test_in_memory_storage_is_istorageprovider(self):
        from exonware.xwapi.contracts import IStorageProvider
        from exonware.xwapi.providers import InMemoryStorageProvider
        assert isinstance(InMemoryStorageProvider(), IStorageProvider)

    def test_local_auth_is_iauthprovider(self):
        from exonware.xwapi.contracts import IAuthProvider
        from exonware.xwapi.providers import LocalAuthProvider
        assert isinstance(LocalAuthProvider(), IAuthProvider)

    def test_in_memory_payment_is_ipaymentprovider(self):
        from exonware.xwapi.contracts import IPaymentProvider
        from exonware.xwapi.providers import InMemoryPaymentProvider
        assert isinstance(InMemoryPaymentProvider(), IPaymentProvider)
