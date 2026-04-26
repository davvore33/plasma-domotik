# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**plasma-domotik** is a KDE Plasma home automation widget for controlling IKEA TRÅDFRI Zigbee devices. It has three layers:

1. **Plasmoid** (QML/Plasma 6) — desktop widget UI
2. **Node Adapter** (Node.js, port 8765) — HTTP bridge between Plasmoid and TRÅDFRI gateway
3. **Python Backend** — device model, abstract bridge interface, mock/real adapters, optional DBus service

## Commands

### Python

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip pytest && pip install -r requirements.txt

pytest                          # run all 21 tests
pytest backend/tests/test_device.py::test_device_basic_fields  # single test
pytest -q                       # quiet output
```

### BDD (Behave)

```bash
pip install behave
behave features/
```

### Node Adapter

```bash
npm install
node backend/service/tradfri_node_adapter.mjs   # starts HTTP server on :8765
```

### Python Service (no DBus)

```bash
python3 -c "from backend.service.runner import main; main()"
```

## Architecture

```
Plasmoid (QML)
    │  HTTP localhost:8765
    ▼
Node Adapter (tradfri_node_adapter.mjs)
    │  node-tradfri-client / CoAP
    ▼
IKEA TRÅDFRI Gateway (default 192.168.1.116)
```

**Key source files:**

| File | Role |
|------|------|
| `backend/models/device.py` | `Device` dataclass — id, name, type, reachable, state, capabilities |
| `backend/service/zigbee_bridge.py` | Abstract `ZigbeeBridge` interface |
| `backend/service/tradfri_adapter.py` | PyTradfri implementation; persists PSK to `~/.config/plasma-domotik/tradfri_psk.json` |
| `backend/service/tradfri_node_adapter.mjs` | Node HTTP server; endpoints: `/connect`, `/devices`, `/power`, `/brightness`; device cache + auto-reconnect (5 s) |
| `backend/service/mock_bridge.py` | In-memory mock for tests |
| `backend/service/dbus_service.py` | Optional DBus wrapper (`io.github.davvore33.PlasmaDomotik`) |
| `plasmoid/package/contents/ui/main.qml` | QML widget; polls Node Adapter every 10 s |
| `plasmoid/package/contents/config/main.xml` | KCfg schema (gatewayHost, securityCode) |

## Node Adapter REST API

| Method | Endpoint | Body |
|--------|----------|------|
| POST | `/connect` | `{ host, securityCode }` |
| GET | `/devices` | — |
| POST | `/power` | `{ deviceId, state: bool }` |
| POST | `/brightness` | `{ deviceId, level: 0-254 }` |

## Workflow & Conventions

### General Rules
- **Code** - Write all code in English (variables, functions, comments, commit messages)
- **Tests** - Modify only when code patterns change, not for every small change
- **Branches** - Every modification on a separate feature/hotfix branch
- **Commits** - Descriptive messages; reference issues with `#<number>` or `Closes #<number>`

### Branch Naming
```
feature/<short-description>
hotfix/<short-description>
```

### Commit Message Format
```
<type>: <description>

[Optional body]

Fixes #<issue>
```
Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md) for epics and backlog.

## Configuration

Copy `config.json.example` → `config.json` and fill in `gatewayHost` and `securityCode`. The Plasmoid stores these values via KCfg (editable in widget settings).
