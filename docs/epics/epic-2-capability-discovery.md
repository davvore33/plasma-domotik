# Epic 2 — Capability Discovery & Dynamic Controls

**Goal:** the plasmoid renders the right controls for each device instead of
a single on/off toggle for everything.

**Status:** done

---

## User Stories

### 2.1 — Capability detection in Node Adapter
`/devices` response includes a `capabilities` array per device, populated from
CoAP accessory data.

Examples:
- smart plug → `["power"]`
- dimmable bulb → `["power", "brightness"]`
- white-spectrum bulb → `["power", "brightness", "color_temp"]`

The `Device` model already has the `capabilities` field — the adapter must fill it.

**Acceptance criteria:**
- [x] `capabilities` is never empty for a reachable device
- [x] Capability strings match the taxonomy defined in 2.3

---

### 2.2 — Dynamic QML controls
The device row renders controls based on `capabilities`:

| Capability | Control | Endpoint |
|------------|---------|----------|
| `power` | on/off toggle | `POST /power` |
| `brightness` | slider 0–254 | `POST /brightness` |
| `color_temp` | slider (Kelvin range TBD) | TBD |
| `color_rgb` | color picker (low priority) | TBD |

**Acceptance criteria:**
- [x] Toggle-only devices show only the toggle
- [x] Dimmable devices show toggle + brightness slider
- [x] Controls are hidden when the device is unreachable

---

### 2.3 — Capability taxonomy
Define and document the canonical capability string set and the mapping from
CoAP accessory types to capabilities. The mapping lives in the Node Adapter
as the single source of truth.

**Capability taxonomy (source of truth — `tradfri_node_adapter.mjs`):**

| Device type | Capabilities |
|-------------|--------------|
| Smart plug | `power` |
| Dimmable bulb | `power`, `brightness` |
| White-spectrum bulb | `power`, `brightness`, `color_temp` |
| Color bulb | `power`, `brightness`, `color_temp`, `color` |
| Blind/roller | `position` |

Capability strings:

| String | Meaning | Control | Endpoint |
|--------|---------|---------|----------|
| `power` | on/off | toggle switch | `GET /power?id=&state=` |
| `brightness` | dim level 0–100 % (mapped to 0–254 CoAP) | slider | `GET /brightness?id=&value=` |
| `color_temp` | colour temperature | slider (future) | TBD |
| `color` | RGB colour | colour picker (future) | TBD |
| `position` | blind position | slider (future) | TBD |

**Acceptance criteria:**
- [x] Mapping documented in this epic (or a linked ADR)
- [x] Node Adapter uses the mapping exclusively — no ad-hoc strings elsewhere
