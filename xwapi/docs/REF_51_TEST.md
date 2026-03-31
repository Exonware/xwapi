# xwapi — Test Status and Coverage

**Last Updated:** 31-Mar-2026

`xwapi` follows a 4-layer strategy:

- `tests/0.core/` — critical contracts and high-value smoke coverage
- `tests/1.unit/` — component and behavior unit tests
- `tests/2.integration/` — end-to-end behavior across server/middleware/admin flows
- `tests/3.advance/` — stress/reliability and advanced scenarios

## Areas explicitly covered in recent hardening

- Engine-agnostic error contract and adapter behavior.
- Admin security/protection controls.
- Pause/resume behavior and error-path consistency.
- Outbox store behavior, leasing/retry/dead transitions.
- Singleton background worker behavior and restart semantics.
- API token lifecycle (create/list/revoke).
- Usage metering, idempotency, and compensation logic.
- Scope-enforcement behavior and unmapped-route policy.
- Integration endpoints for token management and admin APIs.
- Advance-level stress tests for token idempotency and pipeline bulk processing.

## Execute tests

Full:

```bash
python tests/runner.py
```

By layer:

```bash
pytest tests/0.core/
pytest tests/1.unit/
pytest tests/2.integration/
pytest tests/3.advance/
```

## Evidence

- Current and historical run reports are stored in `docs/tests/` and `docs/logs/tests/` as `TEST_*_SUMMARY.md`.
