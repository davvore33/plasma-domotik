import logging
import time
from backend.service.mock_bridge import MockBridge
from backend.service.dbus_service import BaseService, DBusServiceWrapper, _HAS_PYDBUS

_LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    bridge = MockBridge()
    # add a sample device
    bridge.add_device({
        "id": "dev1",
        "name": "Test Lamp",
        "type": "light",
        "reachable": True,
        "state": {"on": False, "brightness": 50},
        "capabilities": ["onoff", "brightness"],
    })

    base = BaseService(bridge)

    if _HAS_PYDBUS:
        wrapper = DBusServiceWrapper(base)
        wrapper.start()
    else:
        _LOGGER.info("pydbus not available — running in-process loop")
        base.Refresh()
        # simple loop to keep process alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            _LOGGER.info("Shutting down")


if __name__ == "__main__":
    main()
