import pytest

from app.bluetooth.transport import BluetoothTransport


def test_transport_cannot_be_created_directly():
    with pytest.raises(TypeError):
        BluetoothTransport()