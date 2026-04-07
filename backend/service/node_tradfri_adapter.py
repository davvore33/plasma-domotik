"""Node.js-backed Tradfri adapter.

This adapter spawns a Node.js HTTP server (tradfri_node_adapter.mjs) that uses
node-tradfri-client to communicate with the IKEA gateway, and proxies the
ZigbeeBridge interface over HTTP.
"""

from typing import Any, Dict, Iterable, Optional, List
import json
import logging
import os
import subprocess
import urllib.request
import urllib.error
import atexit
import time

from backend.service.zigbee_bridge import ZigbeeBridge

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 8765
NODE_ADAPTER_PATH = os.path.join(os.path.dirname(__file__), "tradfri_node_adapter.mjs")


def _find_node():
    """Find a usable node binary."""
    for candidate in ["node", "nodejs"]:
        try:
            subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
    return None


class NodeTradfriAdapter(ZigbeeBridge):
    """Adapter that proxies calls to a Node.js tradfri_node_adapter process.

    The Node side handles DTLS communication with the IKEA gateway using
    node-tradfri-client, which has better compatibility than pytradfri/aiocoap.
    """

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self._node_process: Optional[subprocess.Popen] = None
        self._node_bin: Optional[str] = None

    def _ensure_node_server(self) -> bool:
        """Start the Node.js adapter server if not already running."""
        # Check if already running
        try:
            resp = self._get("/connect")
            if resp is not None:
                return True
        except Exception:
            pass

        # Start the Node.js server
        self._node_bin = _find_node()
        if not self._node_bin:
            _LOGGER.error("No node.js binary found")
            return False

        if not os.path.exists(NODE_ADAPTER_PATH):
            _LOGGER.error("Node adapter script not found: %s", NODE_ADAPTER_PATH)
            return False

        try:
            self._node_process = subprocess.Popen(
                [self._node_bin, NODE_ADAPTER_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            atexit.register(self._stop_node_server)
            # Wait for server to be ready
            for _ in range(20):
                time.sleep(0.5)
                try:
                    resp = self._get("/connect")
                    if resp is not None:
                        _LOGGER.info("Node adapter server started on port %d", self.port)
                        return True
                except Exception:
                    pass
            _LOGGER.error("Node adapter server did not start in time")
            return False
        except Exception:
            _LOGGER.exception("Failed to start Node adapter server")
            return False

    def _stop_node_server(self) -> None:
        """Stop the Node.js adapter server."""
        try:
            self._get("/disconnect")
        except Exception:
            pass
        if self._node_process and self._node_process.poll() is None:
            self._node_process.terminate()
            try:
                self._node_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._node_process.kill()
        self._node_process = None

    def _get(self, path: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make a GET request to the Node adapter."""
        url = f"{self.base_url}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            _LOGGER.exception("HTTP GET %s failed", path)
            return None

    def connect(self, timeout: int = 5) -> bool:
        """Ensure the Node.js adapter server is running."""
        return self._ensure_node_server()

    def disconnect(self) -> None:
        """Stop the Node.js adapter server."""
        self._stop_node_server()

    def discover_devices(self) -> Iterable[Dict[str, Any]]:
        """Discover devices via the Node adapter."""
        if not self._ensure_node_server():
            return []
        result = self._get("/devices", timeout=15)
        if result is None:
            return []
        return result

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get a single device by ID."""
        if not self._ensure_node_server():
            return None
        return self._get(f"/device?id={device_id}", timeout=10)

    def set_power(self, device_id: str, state: bool) -> bool:
        """Set power state of a device."""
        if not self._ensure_node_server():
            return False
        result = self._get(f"/power?id={device_id}&state={str(state).lower()}", timeout=10)
        if result is None:
            return False
        return result.get("success", False)

    def set_brightness(self, device_id: str, value: int) -> bool:
        """Set brightness of a light device."""
        if not self._ensure_node_server():
            return False
        result = self._get(f"/brightness?id={device_id}&value={int(value)}", timeout=10)
        if result is None:
            return False
        return result.get("success", False)
