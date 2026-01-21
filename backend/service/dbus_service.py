from typing import Dict, Any, List, Callable, Optional
import logging
import concurrent.futures
import functools
import time

from backend.logging import setup_logging

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

setup_logging()
_LOGGER = logging.getLogger(__name__)

# default timeout for bridge operations (seconds)
BRIDGE_OP_TIMEOUT = 5


def _with_timeout(fn: Callable, timeout: int, *args, **kwargs):
    """Run `fn` in a thread and raise on timeout or propagate exceptions."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn, *args, **kwargs)
        try:
            return fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            fut.cancel()
            raise TimeoutError(f"Operation timed out after {timeout}s")


class BaseService:
    """Core service logic separated from DBus exposure for testing."""

    def __init__(self, bridge: ZigbeeBridge):
        self.bridge = bridge
        # internal device store: id -> Device
        self._devices: Dict[str, Device] = {}
        # last error seen from adapter operations
        self.last_error: Optional[str] = None
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
        _LOGGER.debug("Listing devices", extra={"extra": {"count": len(self._devices)}})
        return [d.to_dict() for d in self._devices.values()]

    def GetDevice(self, device_id: str) -> Optional[Dict[str, Any]]:
        d = self._devices.get(device_id)
        _LOGGER.debug("GetDevice called", extra={"extra": {"device_id": device_id, "found": bool(d)}})
        return d.to_dict() if d else None

    def Refresh(self) -> None:
        try:
            discovered = list(_with_timeout(self.bridge.discover_devices, BRIDGE_OP_TIMEOUT))
            self.last_error = None
        except TimeoutError as e:
            self.last_error = str(e)
            _LOGGER.exception("Device discovery timed out", extra={"extra": {}})
            return
        except Exception as e:
            self.last_error = str(e)
            _LOGGER.exception("Device discovery failed", extra={"extra": {}})
            return
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
        to_remove = [did for did in list(self._devices) if did not in discovered_ids]
        for did in to_remove:
            del self._devices[did]
            self._emit("DeviceRemoved", did)

    def SetPower(self, device_id: str, state: bool) -> bool:
        try:
            success = bool(_with_timeout(self.bridge.set_power, BRIDGE_OP_TIMEOUT, device_id, bool(state)))
        except TimeoutError as e:
            self.last_error = str(e)
            _LOGGER.exception("set_power timed out", extra={"extra": {"device_id": device_id}})
            return False
        except Exception as e:
            self.last_error = str(e)
            _LOGGER.exception("set_power failed", extra={"extra": {"device_id": device_id}})
            return False
        if success:
            dev = self._devices.get(device_id)
            if dev:
                dev.state["on"] = bool(state)
                self._emit("DeviceUpdated", device_id)
        return bool(success)

    def Status(self) -> Dict[str, Optional[str]]:
        """Return basic service status including last adapter error (if any)."""
        return {"ok": None if self.last_error else "true", "last_error": self.last_error}


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
            "Status": self.base.Status,
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
