from typing import Dict, Iterable, Optional, Any
from .zigbee_bridge import ZigbeeBridge


class MockBridge(ZigbeeBridge):
    """A tiny in-memory mock bridge for testing and local runs."""

    def __init__(self):
        # simple dict of device_id -> descriptor
        self._devices: Dict[str, Dict[str, Any]] = {}

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
