# Epic 2 — Capability Discovery & Dynamic Controls

**Goal:** the plasmoid renders the right controls for each device instead of
a single on/off toggle for everything.

**Status:** planned

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
- [ ] `capabilities` is never empty for a reachable device
- [ ] Capability strings match the taxonomy defined in 2.3

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
- [ ] Toggle-only devices show only the toggle
- [ ] Dimmable devices show toggle + brightness slider
- [ ] Controls are hidden when the device is unreachable

---

### 2.3 — Capability taxonomy
Define and document the canonical capability string set and the mapping from
CoAP accessory types to capabilities. The mapping lives in the Node Adapter
as the single source of truth.

**Acceptance criteria:**
- [ ] Mapping documented in this epic (or a linked ADR)
- [ ] Node Adapter uses the mapping exclusively — no ad-hoc strings elsewhere
