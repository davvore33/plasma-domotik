from typing import Any, Dict, Iterable, Optional, List
import asyncio
import json
import logging
import os
import re
import socket
import uuid
from urllib.parse import urlparse

from backend.service.zigbee_bridge import ZigbeeBridge

_LOGGER = logging.getLogger(__name__)

try:
    from pytradfri import Gateway
    from pytradfri.api.aiocoap_api import APIFactory
    from pytradfri.device import Device as TradfriDevice
    from pytradfri.error import PytradfriError
    _HAS_PYTRADFRI = True
except Exception:
    Gateway = None  # type: ignore
    APIFactory = None  # type: ignore
    TradfriDevice = None  # type: ignore
    PytradfriError = None  # type: ignore
    _HAS_PYTRADFRI = False

DEFAULT_CONFIG_DIR = os.path.expanduser("~/.config/plasma-domotik")
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "tradfri_psk.json")


def _map_device_type(dev: TradfriDevice) -> str:
    if dev.has_light_control:
        return "light"
    if dev.has_blind_control:
        return "blind"
    if dev.has_socket_control:
        return "plug"
    if dev.has_sensor_control:
        return "sensor"
    return "unknown"


def _map_capabilities(dev: TradfriDevice) -> List[str]:
    caps: List[str] = []
    if dev.has_light_control:
        caps.append("on_off")
        light = dev.light_control.lights[0]
        if light.dimmer is not None:
            caps.append("brightness")
        if hasattr(light, "color_temp") and light.color_temp is not None:
            caps.append("color_temp")
        if hasattr(light, "hex_color") and light.hex_color is not None:
            caps.append("color")
    if dev.has_blind_control:
        caps.append("position")
    if dev.has_socket_control:
        caps.append("on_off")
    return caps


def _device_to_dict(dev: TradfriDevice) -> Dict[str, Any]:
    desc: Dict[str, Any] = {
        "id": str(dev.id),
        "name": dev.name or "Unknown",
        "type": _map_device_type(dev),
        "reachable": dev.reachable,
        "state": {},
        "capabilities": _map_capabilities(dev),
    }

    if dev.has_light_control and dev.light_control.lights:
        light = dev.light_control.lights[0]
        desc["state"]["on"] = bool(light.state)
        if light.dimmer is not None:
            desc["state"]["brightness"] = int(light.dimmer)
    elif dev.has_socket_control and dev.socket_control.sockets:
        sock = dev.socket_control.sockets[0]
        desc["state"]["on"] = bool(sock.state)

    return desc


class TradfriAdapter(ZigbeeBridge):
    """Adapter for IKEA TRADFRI gateways using pytradfri.

    Supports automatic PSK generation from the gateway security code
    and persists credentials to a JSON config file.
    """

    def __init__(
        self,
        host: str,
        identity: Optional[str] = None,
        psk: Optional[str] = None,
        security_code: Optional[str] = None,
        config_path: str = DEFAULT_CONFIG_FILE,
    ):
        if not _HAS_PYTRADFRI:
            raise RuntimeError("pytradfri is not installed")
        self.host = host
        self.identity = identity
        self.psk = psk
        self.security_code = security_code
        self.config_path = config_path
        self._api_factory = None
        self._api = None
        self._gateway = Gateway()

    def _load_stored_credentials(self) -> bool:
        """Load identity/psk from config file if available."""
        try:
            with open(self.config_path) as f:
                conf = json.load(f)
            entry = conf.get(self.host)
            if entry:
                self.identity = entry.get("identity")
                self.psk = entry.get("key")
                return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return False

    def _save_credentials(self) -> None:
        """Persist identity/psk to config file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path) as f:
                conf = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            conf = {}
        conf[self.host] = {"identity": self.identity, "key": self.psk}
        with open(self.config_path, "w") as f:
            json.dump(conf, f, indent=4)

    def connect(self, timeout: int = 5) -> bool:
        """Establish connection to the gateway.

        If identity/psk are not provided, attempts to load from config file.
        If still missing and security_code is available, performs PSK generation.

        Returns True on success, False otherwise.
        """
        try:
            if not self.identity or not self.psk:
                if not self._load_stored_credentials():
                    if not self.security_code:
                        _LOGGER.error("No credentials and no security_code provided")
                        return False
                    return self._run_async(self._generate_psk())

            return self._run_async(self._init_api())
        except Exception as exc:
            _LOGGER.exception("Failed to connect to Tradfri gateway: %s", exc)
            return False

    async def _generate_psk(self) -> bool:
        """Generate PSK using the security code."""
        from aiocoap import Context
        identity = uuid.uuid4().hex

        original_create = Context.create_client_context

        async def patched_create(*args, **kwargs):
            kwargs["transports"] = ["tinydtls"]
            return await original_create(*args, **kwargs)

        Context.create_client_context = patched_create
        try:
            api_factory = await APIFactory.init(host=self.host, psk_id=identity)
            psk = await api_factory.generate_psk(self.security_code)
            self.identity = identity
            self.psk = psk
            self._save_credentials()
            self._api_factory = api_factory
            self._api = api_factory.request
            _LOGGER.info("Generated and saved new PSK for %s", self.host)
            return True
        finally:
            Context.create_client_context = original_create

    async def _init_api(self) -> bool:
        """Initialize API with stored credentials."""
        from aiocoap import Context

        original_create = Context.create_client_context

        async def patched_create(*args, **kwargs):
            kwargs["transports"] = ["tinydtls"]
            return await original_create(*args, **kwargs)

        Context.create_client_context = patched_create
        try:
            api_factory = await APIFactory.init(
                host=self.host, psk_id=self.identity, psk=self.psk
            )
            self._api_factory = api_factory
            self._api = api_factory.request
            # Verify connectivity
            gateway = Gateway()
            await self._api(gateway.get_devices())
            return True
        finally:
            Context.create_client_context = original_create

    def disconnect(self) -> None:
        """Shutdown the API factory and release resources."""
        if self._api_factory:
            self._run_async(self._api_factory.shutdown())
            self._api_factory = None
            self._api = None

    def discover_devices(self) -> Iterable[Dict[str, Any]]:
        if not self._api:
            raise RuntimeError("Not connected to Tradfri gateway")

        try:
            devices = self._run_async(self._fetch_devices())
            return [_device_to_dict(d) for d in devices]
        except Exception:
            _LOGGER.exception("Error while discovering devices from Tradfri gateway")
            return []

    async def _fetch_devices(self) -> List[TradfriDevice]:
        devices_command = self._gateway.get_devices()
        devices_commands = await self._api(devices_command)
        return await self._api(devices_commands)

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        if not self._api:
            raise RuntimeError("Not connected to Tradfri gateway")

        try:
            devices = self._run_async(self._fetch_devices())
            for d in devices:
                if str(d.id) == device_id:
                    return _device_to_dict(d)
        except Exception:
            _LOGGER.exception("Error fetching device %s", device_id)
        return None

    def set_power(self, device_id: str, state: bool) -> bool:
        if not self._api:
            raise RuntimeError("Not connected to Tradfri gateway")

        try:
            return self._run_async(self._set_power_async(device_id, state))
        except Exception:
            _LOGGER.exception("set_power failed for %s", device_id)
            return False

    async def _set_power_async(self, device_id: str, state: bool) -> bool:
        dev = await self._get_device_by_id(device_id)
        if dev is None:
            return False

        if dev.has_light_control:
            cmd = dev.light_control.set_state(state)
        elif dev.has_socket_control:
            cmd = dev.socket_control.set_state(state)
        else:
            return False

        await self._api(cmd)
        return True

    def set_brightness(self, device_id: str, value: int) -> bool:
        if not self._api:
            raise RuntimeError("Not connected to Tradfri gateway")

        try:
            return self._run_async(self._set_brightness_async(device_id, value))
        except Exception:
            _LOGGER.exception("set_brightness failed for %s", device_id)
            return False

    async def _set_brightness_async(self, device_id: str, value: int) -> bool:
        dev = await self._get_device_by_id(device_id)
        if dev is None or not dev.has_light_control:
            return False

        # pytradfri uses 0-254 range for dimmer
        dimmer_value = max(0, min(254, int(value * 254 / 100)))
        cmd = dev.light_control.set_dimmer(dimmer_value)
        await self._api(cmd)
        return True

    async def _get_device_by_id(self, device_id: str) -> Optional[TradfriDevice]:
        devices_command = self._gateway.get_devices()
        devices_commands = await self._api(devices_command)
        devices = await self._api(devices_commands)
        for d in devices:
            if str(d.id) == device_id:
                return d
        return None

    @staticmethod
    def _run_async(coro):
        """Run an async coroutine from sync context."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        # If already in an event loop, run in a new thread
        import concurrent.futures
        import threading

        result = None
        exception = None

        def _runner():
            nonlocal result, exception
            try:
                result = asyncio.run(coro)
            except Exception as e:
                exception = e

        t = threading.Thread(target=_runner)
        t.start()
        t.join()
        if exception:
            raise exception
        return result

    @staticmethod
    def discover_gateways(timeout: float = 2.0) -> list[str]:
        """Discover IKEA TRÅDFRI gateways on the local network via SSDP/UPnP."""
        MSEARCH = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            'ST: upnp:rootdevice\r\n'
            'MX: 2\r\n'
            '\r\n'
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        gateways: list[str] = []
        try:
            sock.sendto(MSEARCH.encode(), ('239.255.255.250', 1900))
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode('utf-8', errors='ignore')
                    match = re.search(
                        r'^LOCATION:\s*(.+)$', response, re.MULTILINE | re.IGNORECASE
                    )
                    if match:
                        parsed = urlparse(match.group(1).strip())
                        if parsed.hostname:
                            gateways.append(parsed.hostname)
                    else:
                        gateways.append(addr[0])
                except socket.timeout:
                    break
        finally:
            sock.close()
        return list(dict.fromkeys(gateways))
