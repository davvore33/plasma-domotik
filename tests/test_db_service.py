from backend.service.dbus_service import BaseService


class FailingBridge:
    def discover_devices(self):
        raise RuntimeError('bridge error')

    def set_power(self, device_id, state):
        raise RuntimeError('set failed')


def test_status_and_error_handling():
    b = FailingBridge()
    s = BaseService(b)
    # Refresh should catch the exception and set last_error
    s.Refresh()
    assert s.last_error is not None
    st = s.Status()
    assert 'last_error' in st and st['last_error'] is not None

    # SetPower should return False and set last_error
    ok = s.SetPower('x', True)
    assert ok is False
    assert s.last_error is not None
