from backend.service.mock_bridge import MockBridge, sample_bridge


def test_sample_bridge_has_devices():
    b = sample_bridge()
    devices = list(b.discover_devices())
    assert len(devices) >= 3


def test_get_device_and_state_manipulation():
    b = MockBridge(populate_samples=True)
    dev = b.get_device("light-1")
    assert dev is not None
    assert dev["state"].get("on") is False

    assert b.set_power("light-1", True) is True
    assert b.get_device("light-1")["state"]["on"] is True

    assert b.set_brightness("light-1", 50) is True
    assert b.get_device("light-1")["state"]["brightness"] == 50


def test_set_operations_on_missing_device_return_false():
    b = MockBridge(populate_samples=False)
    assert b.set_power("no-such", True) is False
    assert b.set_brightness("no-such", 10) is False
