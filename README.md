# plasma-domotik

Small example repository used for prototyping adapters and a simple backend.

## Overview

- `backend/` - Python package containing adapters, domain models, service code, and tests.
- `docs/` - project documentation and notes.
- `scripts/` - utility scripts used by the project (e.g., issue creation helper).

The repo contains a minimal `Device` model used across adapters and planned DBus APIs.

## Quickstart (development)

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install test deps (if any):

```bash
pip install -U pip pytest
```

3. Run the test suite:

```bash
pytest -q
```

## Contributing

- Please run tests before opening PRs.
- Keep changes small and focused; add tests for new behavior.
