from backend.service.mock_bridge import MockBridge


def test_sample_devices():
    bridge = MockBridge()
    devices = list(bridge.discover_devices())
    assert len(devices) == 3
    ids = {d["id"] for d in devices}
    assert ids == {"light-1", "light-2", "sensor-1"}


def test_set_power():
    bridge = MockBridge()
    assert bridge.set_power("light-1", True) is True
    dev = bridge.get_device("light-1")
    assert dev["state"]["on"] is True

    assert bridge.set_power("nonexistent", True) is False


def test_set_brightness():
    bridge = MockBridge()
    assert bridge.set_brightness("light-1", 50) is True
    dev = bridge.get_device("light-1")
    assert dev["state"]["brightness"] == 50

    assert bridge.set_brightness("nonexistent", 50) is False


def test_get_device():
    bridge = MockBridge()
    dev = bridge.get_device("light-1")
    assert dev is not None
    assert dev["name"] == "Living Room Lamp"

    assert bridge.get_device("nonexistent") is None


def test_add_device():
    bridge = MockBridge(populate_samples=False)
    bridge.add_device({
        "id": "custom-1",
        "name": "Custom Device",
        "type": "light",
        "reachable": True,
        "state": {"on": False},
        "capabilities": ["on_off"],
    })
    devices = list(bridge.discover_devices())
    assert len(devices) == 1
    assert devices[0]["id"] == "custom-1"


def test_sample_bridge_helper():
    bridge = MockBridge()
    from backend.service.mock_bridge import sample_bridge
    other = sample_bridge()
    assert list(bridge.discover_devices()) == list(other.discover_devices())
