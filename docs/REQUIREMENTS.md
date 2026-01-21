# Plasma Zigbee Controller  
## Project Requirements and TODO

---

## 1. Project Goal

Develop a KDE Plasma plasmoid to control home Zigbee devices via IP-based bridges, using a modular and interchangeable architecture.

The project must:
- initially support IKEA TRÅDFRI
- not be tightly coupled to a specific bridge
- allow future integration of other backends (e.g. Zigbee2MQTT, Hue, Home Assistant)

---

## 2. Initial Scope (MVP)

### Included features
- Device discovery
- Device list visualization
- On/off control for light-type devices
- Manual state refresh

### Excluded features (for now)
- Scenes
- Groups and rooms
- Color and color temperature
- Automations
- Push notifications

---

## 3. General Architecture

### Main components

```

Plasma Plasmoid (QML)
↓
DBus API
↓
Zigbee Controller Service (Python)
↓
Bridge Adapter Layer
↓
Zigbee Bridge

````

### Architectural principles
- Clear separation between UI, logic, and integration
- Backend independent from Plasma
- Stable and documented API
- Interchangeable bridges via abstraction

---

## 4. Backend (Python Service)

### Responsibilities
- Expose a stable DBus API
- Manage devices and their states
- Translate generic commands into bridge-specific commands
- Isolate each bridge into a dedicated adapter

### Technologies
- Python 3.10 or newer
- DBus (pydbus or equivalent)
- systemd user service
- Structured logging

---

## 5. Core Abstractions

### 5.1 ZigbeeBridge (abstract interface)

```python
class ZigbeeBridge:
    def discover_devices(self) -> list:
        pass

    def get_device(self, device_id: str):
        pass

    def set_power(self, device_id: str, state: bool) -> None:
        pass

    def set_brightness(self, device_id: str, value: int) -> None:
        pass
````

---

### 5.2 Device (common model)

Minimum fields:

* id
* name
* type (light, plug, sensor, etc.)
* reachable
* state (on/off)
* capabilities

---

## 6. Bridge Adapters

### TradfriAdapter (first implementation)

Responsibilities:

* Gateway authentication
* Mapping TRÅDFRI APIs to the ZigbeeBridge interface
* Error and timeout handling

Dependencies:

* pytradfri

---

## 7. DBus API (first version)

### Methods

* ListDevices() → array
* GetDevice(device_id) → dict
* SetPower(device_id, state)
* Refresh()

### Signals

* DeviceUpdated(device_id)
* DeviceAdded(device_id)
* DeviceRemoved(device_id)

---

## 8. Plasma Plasmoid

### Responsibilities

* UI rendering
* User interaction handling
* No Zigbee-related logic

### Technologies

* QML
* Kirigami
* Plasma Components 3
* DBus client

### Minimal UI

* Device list
* On/off toggle
* Backend connection status

---

## 9. Security

* No credentials stored in the plasmoid
* All keys handled by the backend
* Backend executed as a user service

---

## 10. TODO List

### Phase 1 – Foundations

* Create the repository
* Define backend directory structure
* Define the ZigbeeBridge interface
* Define the Device model

### Phase 2 – Core backend

* Implement base DBus service
* Implement a mock bridge for testing
* Logging and error handling

### Phase 3 – Tradfri adapter

* Integrate pytradfri
* Gateway discovery
* Authentication
* Map devices to Device model
* On/off commands

### Phase 4 – Plasmoid

* KDE plasmoid scaffold
* DBus client in QML
* Device list
* State toggle

### Phase 5 – Stabilization

* systemd user service
* Installation documentation
* Gateway disconnection handling
* Manual testing

---

## 11. Future Extensions

* Zigbee2MQTT support
* Home Assistant support
* Scenes and groups
* Colors and color temperatures
* State caching
* Push events

---

## 12. Project Philosophy

Simple UI, solid backend, interchangeable bridges.

The project should remain:

* readable
* extensible
* consistent with the KDE ecosystem

