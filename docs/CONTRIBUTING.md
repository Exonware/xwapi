# Contributing to xwapi

Thanks for helping improve **exonware-xwapi**.

## Before you start

- For **security issues**, see [SECURITY.md](SECURITY.md) — do not file those as public issues.
- For **features or large changes**, open an issue first so we can align on scope.

## Development setup

```bash
git clone https://github.com/exonware/xwapi.git
cd xwapi
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -e ".[dev]"
```

Run tests:

```bash
python tests/runner.py --core
# or full suite:
python tests/runner.py
```

## Pull requests

- Target the default branch unless maintainers specify otherwise.
- Keep changes focused; match existing style and patterns.
- Ensure tests pass locally (`python tests/runner.py` or the layers you touched).
- Do not commit secrets or large generated artifacts unless required by the task.

## Code of conduct

Be respectful and constructive. Report abuse to **connect@exonware.com**.
