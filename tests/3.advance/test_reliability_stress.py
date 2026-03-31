from __future__ import annotations

import asyncio
import threading
import time

import pytest

from exonware.xwapi.providers import InMemoryPaymentProvider, InMemoryStorageProvider, LocalAuthProvider
from exonware.xwapi.server import XWApiServer
from exonware.xwapi.token_management import APITokenManager


def _wait_until(predicate, timeout: float = 6.0, interval: float = 0.05) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


@pytest.mark.xwapi_advance
@pytest.mark.xwapi_performance
@pytest.mark.asyncio
async def test_advance_token_idempotency_concurrency_stress() -> None:
    manager = APITokenManager(
        auth_provider=LocalAuthProvider(),
        storage_provider=InMemoryStorageProvider(),
        payment_provider=InMemoryPaymentProvider(),
    )
    created = await manager.create_token(
        subject_id="advance-user",
        name="advance-idempotency-token",
        scopes=["infer"],
    )
    token_id = created["token_id"]
    await manager.recharge(subject_id="advance-user", amount=200.0)

    async def consume_once(key: str) -> dict:
        return await manager.record_usage(
            token_id=token_id,
            amount=1.0,
            operation="stress",
            idempotency_key=key,
        )

    # For each key, two concurrent requests should result in one debit.
    for i in range(60):
        key = f"stress-{i}"
        r1, r2 = await asyncio.gather(consume_once(key), consume_once(key))
        assert r1["idempotency_key"] == key
        assert r2["idempotency_key"] == key

    balance = await manager.get_balance("advance-user")
    assert balance == pytest.approx(140.0)
    usage = await manager.get_usage(token_id)
    assert len(usage) == 60


@pytest.mark.xwapi_advance
@pytest.mark.xwapi_performance
def test_advance_pipeline_bulk_processing_stress() -> None:
    server = XWApiServer(engine="fastapi")
    observed: list[int] = []
    lock = threading.Lock()

    def handler(payload: dict[str, int]) -> dict[str, bool]:
        with lock:
            observed.append(payload["idx"])
        return {"ok": True}

    server.register_pipeline_handler("advance.bulk", handler)
    try:
        server.start_pipeline_worker()
        for idx in range(120):
            server.enqueue_pipeline_job("advance.bulk", {"idx": idx})
        assert _wait_until(lambda: len(observed) == 120, timeout=8.0)
        assert len(set(observed)) == 120
    finally:
        server.stop_pipeline_worker()
