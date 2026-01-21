from typing import Dict, Iterable, Optional, Any, List
from .zigbee_bridge import ZigbeeBridge


class MockBridge(ZigbeeBridge):
    """A tiny in-memory mock bridge for testing and local runs.

    The mock is pre-populated with a deterministic set of sample devices which
    makes it useful for UI development and automated tests that need stable
    data. Additional devices can be added via `add_device()`.
    """

    def __init__(self, populate_samples: bool = True):
        # simple dict of device_id -> descriptor
        self._devices: Dict[str, Dict[str, Any]] = {}
        if populate_samples:
            self._populate_sample_devices()

    def _populate_sample_devices(self) -> None:
        """Add a small deterministic set of sample devices."""
        samples: List[Dict[str, Any]] = [
            {
                "id": "light-1",
                "name": "Living Room Lamp",
                "type": "light",
                "reachable": True,
                "state": {"on": False, "brightness": 0},
                "capabilities": ["on_off", "brightness"],
            },
            {
                "id": "light-2",
                "name": "Kitchen Light",
                "type": "light",
                "reachable": True,
                "state": {"on": True, "brightness": 75},
                "capabilities": ["on_off", "brightness"],
            },
            {
                "id": "sensor-1",
                "name": "Temperature Sensor",
                "type": "sensor",
                "reachable": True,
                "state": {"value": 21.5},
                "capabilities": ["measure_temperature"],
            },
        ]

        for s in samples:
            self.add_device(s)

    def add_device(self, desc: Dict[str, Any]) -> None:
        self._devices[desc["id"]] = dict(desc)

    def discover_devices(self) -> Iterable[Dict[str, Any]]:
        return list(self._devices.values())

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        return self._devices.get(device_id)

    def set_power(self, device_id: str, state: bool) -> bool:
        dev = self._devices.get(device_id)
        if not dev:
            return False
        dev.setdefault("state", {})["on"] = bool(state)
        return True

    def set_brightness(self, device_id: str, value: int) -> bool:
        dev = self._devices.get(device_id)
        if not dev:
            return False
        dev.setdefault("state", {})["brightness"] = int(value)
        return True


def sample_bridge() -> MockBridge:
    """Return a MockBridge prefilled with deterministic sample devices.

    Convenience helper for tests and quick development runs.
    """
    return MockBridge(populate_samples=True)
