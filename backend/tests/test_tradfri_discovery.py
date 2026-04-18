import socket
from unittest.mock import MagicMock, patch

import pytest

from backend.service.tradfri_adapter import TradfriAdapter


class FakeSocket:
    def __init__(self, responses):
        # responses is a list of (data_bytes, addr)
        self._responses = list(responses)
        self.timeout = None

    def settimeout(self, t):
        self.timeout = t

    def setsockopt(self, a, b, c):
        pass

    def sendto(self, data, addr):
        # ignore
        return len(data)

    def recvfrom(self, bufsize):
        if not self._responses:
            raise socket.timeout()
        return self._responses.pop(0)

    def close(self):
        pass


def make_response(location: str, addr=('192.168.1.42', 1900)):
    body = (
        'HTTP/1.1 200 OK\r\n'
        f'LOCATION: {location}\r\n'
        'ST: upnp:rootdevice\r\n'
        '\r\n'
    )
    return (body.encode('utf-8'), addr)


def test_discover_gateways_with_location_header(monkeypatch):
    # simulate two devices responding with LOCATION headers
    resp1 = make_response('http://192.168.1.100:80/description.xml')
    resp2 = make_response('http://192.168.1.101:80/desc')

    fake_sock = FakeSocket([resp1, resp2])

    with patch('backend.service.tradfri_adapter.socket.socket', return_value=fake_sock):
        hosts = TradfriAdapter.discover_gateways(timeout=0.5)
    assert '192.168.1.100' in hosts
    assert '192.168.1.101' in hosts


def test_discover_gateways_fallback_to_sender(monkeypatch):
    # simulate a response without LOCATION header
    body = 'HTTP/1.1 200 OK\r\nST: something\r\n\r\n'
    resp = (body.encode('utf-8'), ('10.0.0.5', 1900))
    fake_sock = FakeSocket([resp])

    with patch('backend.service.tradfri_adapter.socket.socket', return_value=fake_sock):
        hosts = TradfriAdapter.discover_gateways(timeout=0.5)
    assert hosts == ['10.0.0.5']
