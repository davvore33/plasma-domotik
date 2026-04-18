from unittest.mock import MagicMock, patch
import asyncio

import pytest

from backend.service.tradfri_adapter import TradfriAdapter, _HAS_PYTRADFRI


class FakeLight:
    def __init__(self, state=False, dimmer=None, color_temp=None, hex_color=None):
        self.state = state
        self.dimmer = dimmer
        self.color_temp = color_temp
        self.hex_color = hex_color


class FakeLightControl:
    def __init__(self, lights):
        self.lights = lights


class FakeSocketControl:
    def __init__(self, sockets):
        self.sockets = sockets


class FakeDevice:
    def __init__(self, id, name, reachable=True, has_light=False, is_on=False, dimmer=None):
        self.id = id
        self.name = name
        self.reachable = reachable
        self.has_light_control = has_light
        self.has_blind_control = False
        self.has_socket_control = False
        self.has_sensor_control = not has_light
        self.light_control = FakeLightControl([FakeLight(state=is_on, dimmer=dimmer)]) if has_light else FakeLightControl([])
        self.socket_control = FakeSocketControl([])


def test_tradfri_adapter_requires_pytradfri():
    assert isinstance(_HAS_PYTRADFRI, bool)


def test_discover_devices_maps_fields(monkeypatch):
    fake_devices = [
        FakeDevice('d1', 'Lamp 1', has_light=True, is_on=True, dimmer=128),
        FakeDevice('d2', 'Sensor', has_light=False),
    ]

    adapter = TradfriAdapter.__new__(TradfriAdapter)
    adapter._api = MagicMock()
    adapter._gateway = MagicMock()

    async def fake_fetch():
        return fake_devices

    with patch.object(adapter, '_fetch_devices', fake_fetch):
        devices = list(adapter.discover_devices())

    assert len(devices) == 2
    ids = {d['id'] for d in devices}
    assert 'd1' in ids and 'd2' in ids
    d1 = next(d for d in devices if d['id'] == 'd1')
    assert d1['name'] == 'Lamp 1'
    assert d1['state']['on'] is True
    assert d1['state']['brightness'] == 128
    assert d1['capabilities'] == ['on_off', 'brightness']
