from app.bluetooth.rfcomm import RFCOMMTransport
from app.bluetooth.simulator import SimulatorTransport


def create_transport(transport_type="rfcomm"):
    if transport_type == "rfcomm":
        return RFCOMMTransport()

    if transport_type == "simulator":
        return SimulatorTransport()

    raise ValueError(f"Unsupported transport: {transport_type}")