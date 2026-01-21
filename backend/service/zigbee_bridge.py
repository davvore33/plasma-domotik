from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional


class ZigbeeBridge(ABC):
    """Abstract interface representing a Zigbee bridge.

    Implementations should provide device discovery and basic control
    operations required by the project: power and brightness control.
    """

    @abstractmethod
    def discover_devices(self) -> Iterable[Dict[str, Any]]:
        """Discover devices connected to the Zigbee bridge.

        Returns an iterable of device descriptors (dictionaries) containing at
        minimum an identifier and human-friendly metadata.
        """

    @abstractmethod
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Return the device descriptor for `device_id` or `None` if not found."""

    @abstractmethod
    def set_power(self, device_id: str, state: bool) -> bool:
        """Set the power state of the device.

        Args:
            device_id: Identifier of the device to control.
            state: True to turn on, False to turn off.

        Returns:
            True on success, False otherwise.
        """

    @abstractmethod
    def set_brightness(self, device_id: str, value: int) -> bool:
        """Set the brightness for a dimmable device.

        Args:
            device_id: Identifier of the device to control.
            value: Brightness value (0-100).

        Returns:
            True on success, False otherwise.
        """
