from app.bluetooth.rfcomm import RFCOMMTransport
from app.bluetooth.simulator import SimulatorTransport
from app.config import DEVICE_IDENTIFIER


def create_transport(transport_type="rfcomm"):
    if transport_type == "rfcomm":
        return RFCOMMTransport(
            device_identifier=DEVICE_IDENTIFIER
        )

    if transport_type == "simulator":
        return SimulatorTransport()

    raise ValueError(f"Unsupported transport: {transport_type}")