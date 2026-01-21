from unittest.mock import MagicMock, patch

import pytest

from backend.service.tradfri_adapter import TradfriAdapter, _HAS_PYTRADFRI


class DummyDevice:
    def __init__(self, id, name, typ='light', reachable=True, is_on=False):
        self.id = id
        self.name = name
        self.type = typ
        self.reachable = reachable
        self.is_on = is_on


def test_tradfri_adapter_requires_pytradfri():
    # If pytradfri isn't available the module should have set the flag
    assert isinstance(_HAS_PYTRADFRI, bool)


def test_discover_devices_maps_fields(monkeypatch):
    # Create a fake api with a 'devices' attribute
    fake_devices = [DummyDevice('d1', 'Lamp 1', is_on=True), DummyDevice('d2', 'Sensor', typ='sensor')]

    fake_api = MagicMock()
    fake_api.devices = fake_devices

    # Patch the TradfriAdapter to inject a connected _api instance
    adapter = TradfriAdapter.__new__(TradfriAdapter)
    adapter._api = fake_api

    devices = list(adapter.discover_devices())
    assert len(devices) == 2
    ids = {d['id'] for d in devices}
    assert 'd1' in ids and 'd2' in ids
    d1 = next(d for d in devices if d['id'] == 'd1')
    assert d1['name'] == 'Lamp 1'
    assert d1['state']['on'] is True
