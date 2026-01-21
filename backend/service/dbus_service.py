from typing import Dict, Any, List, Callable, Optional
import logging

from backend.models.device import Device
from .zigbee_bridge import ZigbeeBridge

try:
    from pydbus import SessionBus
    from gi.repository import GLib  # type: ignore
    _HAS_PYDBUS = True
except Exception:
    SessionBus = None  # type: ignore
    GLib = None  # type: ignore
    _HAS_PYDBUS = False

_LOGGER = logging.getLogger(__name__)


class BaseService:
    """Core service logic separated from DBus exposure for testing."""

    def __init__(self, bridge: ZigbeeBridge):
        self.bridge = bridge
        # internal device store: id -> Device
        self._devices: Dict[str, Device] = {}
        # callbacks for signals: name -> list[callable(device_id)]
        self._signal_listeners: Dict[str, List[Callable[[str], None]]] = {
            "DeviceUpdated": [],
            "DeviceAdded": [],
            "DeviceRemoved": [],
        }

    # Signal API for in-process use/tests
    def on(self, signal_name: str, cb: Callable[[str], None]) -> None:
        if signal_name not in self._signal_listeners:
            raise ValueError(f"Unknown signal {signal_name}")
        self._signal_listeners[signal_name].append(cb)

    def _emit(self, signal_name: str, device_id: str) -> None:
        _LOGGER.debug("Emit %s for %s", signal_name, device_id)
        for cb in list(self._signal_listeners.get(signal_name, [])):
            try:
                cb(device_id)
            except Exception:
                _LOGGER.exception("Signal listener failed")

    # API methods
    def ListDevices(self) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self._devices.values()]

    def GetDevice(self, device_id: str) -> Optional[Dict[str, Any]]:
        d = self._devices.get(device_id)
        return d.to_dict() if d else None

    def Refresh(self) -> None:
        discovered = list(self.bridge.discover_devices())
        discovered_ids = set()
        for desc in discovered:
            discovered_ids.add(desc["id"])
            if desc["id"] in self._devices:
                # update existing
                self._devices[desc["id"]] = Device.from_dict(desc)
                self._emit("DeviceUpdated", desc["id"])
            else:
                self._devices[desc["id"]] = Device.from_dict(desc)
                self._emit("DeviceAdded", desc["id"])

        # removed devices
        to_remove = [did for did in self._devices if did not in discovered_ids]
        for did in to_remove:
            del self._devices[did]
            self._emit("DeviceRemoved", did)

    def SetPower(self, device_id: str, state: bool) -> bool:
        success = self.bridge.set_power(device_id, bool(state))
        if success:
            dev = self._devices.get(device_id)
            if dev:
                dev.state["on"] = bool(state)
                self._emit("DeviceUpdated", device_id)
        return bool(success)


class DBusServiceWrapper:
    """Wraps BaseService and exposes a DBus interface when pydbus is available.

    The DBus interface follows the API described in docs: methods and signals.
    """

    DBUS_NAME = "io.github.davvore33.PlasmaDomotik"
    DBUS_PATH = "/io/github/davvore33/PlasmaDomotik"

    def __init__(self, base: BaseService):
        self.base = base
        self._bus = None
        self._loop = None

    def start(self) -> None:
        if not _HAS_PYDBUS:
            raise RuntimeError("pydbus not available in this environment")
        self._bus = SessionBus()
        # register object exposing the methods and signals
        iface = {
            "ListDevices": self.base.ListDevices,
            "GetDevice": self.base.GetDevice,
            "SetPower": self.base.SetPower,
            "Refresh": self.base.Refresh,
        }
        self._bus.publish(self.DBUS_NAME, (self.DBUS_PATH, iface))
        _LOGGER.info("DBus service published: %s", self.DBUS_NAME)
        self._loop = GLib.MainLoop()
        try:
            self._loop.run()
        except KeyboardInterrupt:
            _LOGGER.info("DBus service interrupted")

    def stop(self) -> None:
        if self._loop:
            self._loop.quit()
