# Epic 1 — Plasmoid Visual Polish

**Goal:** make the widget look like a real KDE applet, not a prototype.

**Status:** done

---

## User Stories

### 1.1 — Device icons
Each device row shows an appropriate icon from the KDE Breeze icon theme.
Icon is chosen from the device `type` field (`light`, `plug`, `sensor`, …).
Unreachable devices show a greyed-out variant.

**Acceptance criteria:**
- [x] Light devices → bulb icon
- [x] Plug devices → power/socket icon
- [x] Unknown types → generic device icon
- [x] Unreachable devices → icon rendered at reduced opacity

---

### 1.2 — Default widget size + scrollable list
The widget has a sensible minimum size that comfortably displays 3–4 device rows
without truncation. When more devices are present a `ScrollView` lets the user
scroll to reach them. The widget is resizable and remembers its last size.

**Acceptance criteria:**
- [x] Default height fits ~4 rows without scrolling
- [x] 5+ devices trigger a scrollbar
- [ ] Widget can be resized by the user on the desktop
