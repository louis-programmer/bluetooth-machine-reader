from app.bluetooth.rfcomm import RFCOMMTransport
import os
import tty


def test_rfcomm_starts_disconnected():
    transport = RFCOMMTransport()

    assert transport.is_connected() is False


def test_rfcomm_connects_successfully(monkeypatch):
    class FakeConnection:

        def fileno(self):
            return 1

        def close(self):
            pass

    connection = FakeConnection()

    def fake_open(device, mode, buffering=0):
        return connection

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(tty, "setraw", lambda fd: None)

    transport = RFCOMMTransport("/fake/device")

    result = transport.connect()

    assert result is True
    assert transport.is_connected() is True
    assert transport.connection is connection


def test_rfcomm_connection_error(monkeypatch):
    def fake_open(device, mode, buffering=0):
        raise OSError("Device unavailable")

    monkeypatch.setattr("builtins.open", fake_open)

    transport = RFCOMMTransport("/fake/device")

    result = transport.connect()

    assert result is False
    assert transport.is_connected() is False
    assert transport.connection is None


def test_rfcomm_disconnects(monkeypatch):
    class FakeConnection:

        def __init__(self):
            self.closed = False

        def fileno(self):
            return 1

        def close(self):
            self.closed = True

    connection = FakeConnection()

    def fake_open(device, mode, buffering=0):
        return connection

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(tty, "setraw", lambda fd: None)

    transport = RFCOMMTransport("/fake/device")

    transport.connect()
    transport.disconnect()

    assert connection.closed is True
    assert transport.is_connected() is False


def test_rfcomm_read(monkeypatch):
    class FakeConnection:

        def fileno(self):
            return 1

        def close(self):
            pass

    def fake_open(device, mode, buffering=0):
        assert mode == "rb"
        return FakeConnection()

    def fake_read(fd, size):
        assert fd == 1
        assert size == 1024
        return b"37.00kg\n"

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(tty, "setraw", lambda fd: None)
    monkeypatch.setattr(os, "read", fake_read)

    transport = RFCOMMTransport("/fake/device")

    transport.connect()

    result = transport.read()

    assert result == "37.00kg\n"

def test_rfcomm_read_error_is_propagated(monkeypatch):
    class FakeConnection:

        def fileno(self):
            return 1

        def close(self):
            pass

    def fake_open(device, mode, buffering=0):
        return FakeConnection()

    def fake_read(fd, size):
        raise OSError("Bluetooth connection lost")

    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(tty, "setraw", lambda fd: None)
    monkeypatch.setattr(os, "read", fake_read)

    transport = RFCOMMTransport("/fake/device")
    transport.connect()

    import pytest

    with pytest.raises(OSError, match="Bluetooth connection lost"):
        transport.read()

