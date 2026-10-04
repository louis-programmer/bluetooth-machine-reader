import pytest

from app.bluetooth.factory import create_transport
from app.bluetooth.rfcomm import RFCOMMTransport
from app.bluetooth.simulator import SimulatorTransport


def test_create_rfcomm_transport():
    transport = create_transport("rfcomm")

    assert isinstance(transport, RFCOMMTransport)


def test_create_simulator_transport():
    transport = create_transport("simulator")

    assert isinstance(transport, SimulatorTransport)


def test_unsupported_transport():
    with pytest.raises(ValueError):
        create_transport("unknown")