import pytest

from backend.models import Device


def test_device_basic_fields():
    d = Device(id="dev1", name="Lamp", type="light")
    assert d.id == "dev1"
    assert d.name == "Lamp"
    assert d.type == "light"
    assert d.reachable is True
    assert isinstance(d.state, dict)
    assert isinstance(d.capabilities, list)


def test_device_to_dict_and_from_dict():
    payload = {
        "id": "dev2",
        "name": "Sensor",
        "type": "sensor",
        "reachable": False,
        "state": {"value": 42},
        "capabilities": ["measure", "report"],
    }

    d = Device.from_dict(payload)
    assert d.id == "dev2"
    assert d.reachable is False
    assert d.state["value"] == 42

    asdict = d.to_dict()
    assert asdict["id"] == payload["id"]
    assert asdict["capabilities"] == payload["capabilities"]


def test_from_dict_missing_fields_raises():
    with pytest.raises(KeyError):
        Device.from_dict({})
