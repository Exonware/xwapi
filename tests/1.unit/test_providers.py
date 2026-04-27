#exonware/xwapi/tests/1.unit/test_providers.py
"""
Unit tests for xwapi providers — InMemoryStorageProvider, LocalAuthProvider, InMemoryPaymentProvider.
"""

from __future__ import annotations

import pytest
import asyncio


@pytest.mark.xwapi_unit
class TestInMemoryStorageProvider:
    """Test in-memory storage CRUD operations."""

    @pytest.fixture
    def storage(self):
        from exonware.xwapi.providers import InMemoryStorageProvider
        return InMemoryStorageProvider()

    @pytest.mark.asyncio
    async def test_write_and_read(self, storage):
        await storage.write("key1", {"name": "Alice"})
        result = await storage.read("key1")
        assert result == {"name": "Alice"}

    @pytest.mark.asyncio
    async def test_read_returns_copy(self, storage):
        original = {"name": "Alice"}
        await storage.write("key1", original)
        result = await storage.read("key1")
        result["name"] = "Bob"
        assert (await storage.read("key1"))["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_read_missing_key_raises(self, storage):
        with pytest.raises(KeyError):
            await storage.read("missing")

    @pytest.mark.asyncio
    async def test_exists(self, storage):
        assert await storage.exists("key1") is False
        await storage.write("key1", "value")
        assert await storage.exists("key1") is True

    @pytest.mark.asyncio
    async def test_delete(self, storage):
        await storage.write("key1", "value")
        await storage.delete("key1")
        assert await storage.exists("key1") is False

    @pytest.mark.asyncio
    async def test_delete_missing_no_error(self, storage):
        await storage.delete("nonexistent")  # Should not raise


@pytest.mark.xwapi_unit
class TestLocalAuthProvider:
    """Test local auth provider token lifecycle."""

    @pytest.fixture
    def auth(self):
        from exonware.xwapi.providers import LocalAuthProvider
        return LocalAuthProvider()

    @pytest.mark.asyncio
    async def test_issue_and_verify(self, auth):
        result = await auth.issue_api_token(
            subject_id="user1", name="test-token", scopes=["read"]
        )
        assert "token" in result
        assert result["token"].startswith("xw_")
        verified = await auth.verify_api_token(result["token"])
        assert verified is not None
        assert verified["subject_id"] == "user1"

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, auth):
        assert await auth.verify_api_token("invalid") is None
        assert await auth.verify_api_token("") is None
        assert await auth.verify_api_token("xw_bad") is None

    @pytest.mark.asyncio
    async def test_revoke(self, auth):
        result = await auth.issue_api_token(
            subject_id="user1", name="t", scopes=[]
        )
        token_id = result["token_id"]
        assert await auth.revoke_api_token(token_id) is True
        assert await auth.verify_api_token(result["token"]) is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent(self, auth):
        assert await auth.revoke_api_token("nonexistent") is False

    @pytest.mark.asyncio
    async def test_resolve_auth_context(self, auth):
        result = await auth.issue_api_token(
            subject_id="user1", name="ctx-test", scopes=["admin"]
        )
        ctx = await auth.resolve_auth_context(result["token"])
        assert ctx is not None
        assert ctx.subject_id == "user1"
        assert "admin" in ctx.scopes

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, auth):
        # expires_in_seconds=1 then manually expire the record
        result = await auth.issue_api_token(
            subject_id="user1", name="exp", scopes=[], expires_in_seconds=1
        )
        # Manually backdate the expiry to force expiration
        token_id = result["token_id"]
        from datetime import datetime, timezone, timedelta
        auth._token_hashes[token_id]["expires_at"] = (
            datetime.now(timezone.utc) - timedelta(seconds=10)
        ).isoformat()
        verified = await auth.verify_api_token(result["token"])
        assert verified is None

    @pytest.mark.asyncio
    async def test_wrong_hash_rejected(self, auth):
        result = await auth.issue_api_token(
            subject_id="user1", name="t", scopes=[]
        )
        # Tamper with the token secret
        parts = result["token"].split("_", 2)
        tampered = f"xw_{parts[1]}_wrongsecret"
        assert await auth.verify_api_token(tampered) is None


@pytest.mark.xwapi_unit
class TestInMemoryPaymentProvider:
    """Test payment provider balance and credit operations."""

    @pytest.fixture
    def payment(self):
        from exonware.xwapi.providers import InMemoryPaymentProvider
        return InMemoryPaymentProvider()

    @pytest.mark.asyncio
    async def test_initial_balance_zero(self, payment):
        balance = await payment.get_balance("user1")
        assert balance == 0.0

    @pytest.mark.asyncio
    async def test_recharge(self, payment):
        event = await payment.create_recharge(
            subject_id="user1", amount=100.0
        )
        assert event["status"] == "succeeded"
        assert event["balance_after"] == 100.0
        assert await payment.get_balance("user1") == 100.0

    @pytest.mark.asyncio
    async def test_recharge_negative_amount_raises(self, payment):
        with pytest.raises(ValueError, match="amount must be > 0"):
            await payment.create_recharge(subject_id="user1", amount=-10.0)

    @pytest.mark.asyncio
    async def test_consume_credits(self, payment):
        await payment.create_recharge(subject_id="user1", amount=50.0)
        event = await payment.consume_credits(
            subject_id="user1", amount=20.0
        )
        assert event["amount"] == -20.0
        assert event["balance_after"] == 30.0

    @pytest.mark.asyncio
    async def test_consume_insufficient_balance(self, payment):
        with pytest.raises(ValueError, match="insufficient balance"):
            await payment.consume_credits(subject_id="user1", amount=10.0)

    @pytest.mark.asyncio
    async def test_consume_idempotency(self, payment):
        await payment.create_recharge(subject_id="user1", amount=100.0)
        first = await payment.consume_credits(
            subject_id="user1", amount=10.0, idempotency_key="op1"
        )
        second = await payment.consume_credits(
            subject_id="user1", amount=10.0, idempotency_key="op1"
        )
        # Second call is a replay, balance should not change
        assert second["metadata"].get("idempotent_replay") is True
        assert await payment.get_balance("user1") == 90.0

    @pytest.mark.asyncio
    async def test_idempotency_different_amount_raises(self, payment):
        await payment.create_recharge(subject_id="user1", amount=100.0)
        await payment.consume_credits(
            subject_id="user1", amount=10.0, idempotency_key="op1"
        )
        with pytest.raises(ValueError, match="idempotency key reuse"):
            await payment.consume_credits(
                subject_id="user1", amount=20.0, idempotency_key="op1"
            )
