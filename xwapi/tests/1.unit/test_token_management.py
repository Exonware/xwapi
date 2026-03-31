from __future__ import annotations

import asyncio

import pytest

from exonware.xwapi.providers import (
    LocalAuthProvider,
    InMemoryStorageProvider,
    InMemoryPaymentProvider,
)
from exonware.xwapi.token_management import APITokenManager


class _FailOnceUsageWriteStorage(InMemoryStorageProvider):
    def __init__(self) -> None:
        super().__init__()
        self._failed = False
        self._armed = False

    def arm_failure(self) -> None:
        self._armed = True

    async def write(self, key: str, value):
        if self._armed and ("/usage/" in key) and not self._failed:
            self._failed = True
            raise RuntimeError("simulated usage persistence failure")
        await super().write(key, value)


class _ReadFailureStorage(InMemoryStorageProvider):
    def __init__(self, fail_key_fragment: str) -> None:
        super().__init__()
        self._fragment = fail_key_fragment

    async def read(self, key: str):
        if self._fragment in key:
            raise RuntimeError("simulated read failure")
        return await super().read(key)


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_token_create_verify_revoke_flow() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-1",
        name="dev token",
        scopes=["read", "write"],
        expires_in_seconds=3600,
    )
    assert created["token_id"]
    assert created["token"].startswith("xw_")

    verified = await manager.verify_token(created["token"])
    assert verified is not None
    assert verified["subject_id"] == "user-1"

    assert await manager.revoke_token(created["token_id"]) is True
    assert await manager.verify_token(created["token"]) is None


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_token_usage_requires_balance_then_consumes_credits() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-billing",
        name="billing token",
        scopes=["infer"],
    )
    token_id = created["token_id"]

    with pytest.raises(ValueError):
        await manager.record_usage(token_id=token_id, amount=5.0, operation="completion")

    await manager.recharge(subject_id="user-billing", amount=10.0)
    usage = await manager.record_usage(token_id=token_id, amount=3.5, operation="completion")
    assert usage["amount"] == 3.5

    balance = await manager.get_balance("user-billing")
    assert balance == pytest.approx(6.5)

    history = await manager.get_usage(token_id)
    assert len(history) == 1
    assert history[0]["operation"] == "completion"


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_concurrent_usage_is_serialized_per_subject() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-race",
        name="race token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-race", amount=10.0)

    async def consume(amount: float) -> bool:
        try:
            await manager.record_usage(token_id=token_id, amount=amount, operation="completion")
            return True
        except ValueError:
            return False

    ok1, ok2 = await asyncio.gather(consume(6.0), consume(6.0))
    assert [ok1, ok2].count(True) == 1
    balance = await manager.get_balance("user-race")
    assert balance == pytest.approx(4.0)


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_record_usage_rejects_revoked_token() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-revoked",
        name="revoked token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-revoked", amount=2.0)
    assert await manager.revoke_token(token_id) is True

    with pytest.raises(ValueError, match="token revoked"):
        await manager.record_usage(token_id=token_id, amount=1.0, operation="completion")


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_record_usage_idempotency_key_no_double_debit() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-idem",
        name="idempotent token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-idem", amount=10.0)

    key = "req-abc"
    usage1 = await manager.record_usage(
        token_id=token_id,
        amount=2.0,
        operation="completion",
        idempotency_key=key,
    )
    usage2 = await manager.record_usage(
        token_id=token_id,
        amount=2.0,
        operation="completion",
        idempotency_key=key,
    )
    assert usage1["idempotency_key"] == key
    assert usage2["idempotency_key"] == key
    assert await manager.get_balance("user-idem") == pytest.approx(8.0)
    history = await manager.get_usage(token_id)
    assert len(history) == 1


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_record_usage_idempotency_amount_mismatch_raises() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-idem2",
        name="idempotent token 2",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-idem2", amount=10.0)
    await manager.record_usage(
        token_id=token_id,
        amount=1.0,
        operation="a",
        idempotency_key="same-key",
    )
    with pytest.raises(ValueError, match="idempotency key reuse"):
        await manager.record_usage(
            token_id=token_id,
            amount=2.0,
            operation="b",
            idempotency_key="same-key",
        )


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_record_usage_storage_failure_compensates_and_allows_retry() -> None:
    storage = _FailOnceUsageWriteStorage()
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=storage,
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-compensate",
        name="compensate token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-compensate", amount=10.0)
    storage.arm_failure()

    with pytest.raises(RuntimeError, match="simulated usage persistence failure"):
        await manager.record_usage(
            token_id=token_id,
            amount=2.0,
            operation="completion",
            idempotency_key="compensate-key",
        )
    assert await manager.get_balance("user-compensate") == pytest.approx(10.0)

    retried = await manager.record_usage(
        token_id=token_id,
        amount=2.0,
        operation="completion",
        idempotency_key="compensate-key",
    )
    assert retried["amount"] == 2.0
    assert await manager.get_balance("user-compensate") == pytest.approx(8.0)
    history = await manager.get_usage(token_id)
    assert len(history) == 1


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_record_usage_concurrent_same_idempotency_key_single_history() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-idem-concurrent",
        name="idem concurrent token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="user-idem-concurrent", amount=10.0)

    async def call_once() -> dict:
        return await manager.record_usage(
            token_id=token_id,
            amount=3.0,
            operation="completion",
            idempotency_key="idem-concurrent",
        )

    r1, r2 = await asyncio.gather(call_once(), call_once())
    assert r1["idempotency_key"] == "idem-concurrent"
    assert r2["idempotency_key"] == "idem-concurrent"
    assert await manager.get_balance("user-idem-concurrent") == pytest.approx(7.0)
    history = await manager.get_usage(token_id)
    assert len(history) == 1


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_list_tokens_handles_corrupt_subject_index() -> None:
    storage = InMemoryStorageProvider()
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=storage,
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="user-corrupt",
        name="corrupt token",
        scopes=["read"],
    )
    token_id = created["token_id"]
    await storage.write("xwapi/token_mgmt/subjects/user-corrupt/tokens", {"bad": "shape"})
    tokens = await manager.list_tokens(subject_id="user-corrupt")
    assert tokens == []
    # Restore and verify listing still works once index is corrected.
    await storage.write("xwapi/token_mgmt/subjects/user-corrupt/tokens", [token_id])
    restored = await manager.list_tokens(subject_id="user-corrupt")
    assert len(restored) == 1


@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_get_usage_returns_empty_on_storage_read_failure() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=_ReadFailureStorage("/usage/"),
        payment_provider=InMemoryPaymentProvider(),
    )
    usage = await manager.get_usage("any-token")
    assert usage == []
