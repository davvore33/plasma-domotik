from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class Device:
    """Common Device model for adapters and DBus API.

    Minimum fields:
    - id: unique identifier (string)
    - name: human-friendly name
    - type: device type string (e.g., "light", "sensor")
    - reachable: whether the device is reachable
    - state: opaque mapping representing the device state
    - capabilities: list of capability strings supported by the device
    """

    id: str
    name: str
    type: str
    reachable: bool = True
    state: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict representation of the device."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        """Create a Device instance from a mapping.

        This does not perform deep validation; it assumes the minimal
        required keys are present and will raise TypeError/KeyError
        naturally if they are missing or of the wrong type.
        """
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            type=data.get("type", ""),
            reachable=bool(data.get("reachable", True)),
            state=dict(data.get("state", {})),
            capabilities=list(data.get("capabilities", [])),
        )
