from backend.models.device import Device


def test_device_to_dict():
    d = Device(
        id="light-1",
        name="Lamp",
        type="light",
        reachable=True,
        state={"on": True, "brightness": 75},
        capabilities=["on_off", "brightness"],
    )
    result = d.to_dict()
    assert result["id"] == "light-1"
    assert result["name"] == "Lamp"
    assert result["type"] == "light"
    assert result["reachable"] is True
    assert result["state"]["on"] is True
    assert result["capabilities"] == ["on_off", "brightness"]


def test_device_from_dict_minimal():
    d = Device.from_dict({"id": "x"})
    assert d.id == "x"
    assert d.name == ""
    assert d.type == ""
    assert d.reachable is True
    assert d.state == {}
    assert d.capabilities == []


def test_device_from_dict_full():
    data = {
        "id": "plug-1",
        "name": "Coffee Maker",
        "type": "plug",
        "reachable": False,
        "state": {"on": False},
        "capabilities": ["on_off"],
    }
    d = Device.from_dict(data)
    assert d.id == "plug-1"
    assert d.name == "Coffee Maker"
    assert d.type == "plug"
    assert d.reachable is False
    assert d.state["on"] is False
    assert d.capabilities == ["on_off"]


def test_device_defaults():
    d = Device(id="1", name="Test", type="sensor")
    assert d.reachable is True
    assert d.state == {}
    assert d.capabilities == []
