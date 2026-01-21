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

## Dependencies

Install runtime dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Note: `pytradfri` is listed in `requirements.txt` and is required to use the `TradfriAdapter`. The adapter is safe to import in environments without `pytradfri`, but attempting to instantiate it without the package installed will raise an error.

## Using the Tradfri adapter (notes)

- The `TradfriAdapter` is implemented in `backend/service/tradfri_adapter.py` and provides basic device listing.
- For real gateway usage you must provide authentication (identity and pre-shared key). Proper APIFactory usage and persistence of identity/PSK are required for full functionality.
- Running the service against a real gateway is not yet wired into `runner.py`; you can create a small script that constructs `TradfriAdapter(host, identity, psk)` and calls `connect()` then `discover_devices()`.

Example quick test (requires a reachable gateway and valid credentials):

```python
from backend.service.tradfri_adapter import TradfriAdapter

adapter = TradfriAdapter("192.168.1.100", identity="my-id", psk="my-psk")
if adapter.connect():
	print(list(adapter.discover_devices()))
```

## Contributing

- Please run tests before opening PRs.
- Keep changes small and focused; add tests for new behavior.
