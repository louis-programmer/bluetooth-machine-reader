from enum import Enum

from app.parser import parse_reading
from app.bluetooth.factory import create_transport
from app.config import TRANSPORT

class ReceiverState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECEIVING = "receiving"
    ERROR = "error"


class Receiver:
    def __init__(self, transport=None):
        if transport is None:
            transport = create_transport(TRANSPORT)

        self.transport = transport
        self.state = ReceiverState.DISCONNECTED

    def connect(self):
        self.state = ReceiverState.CONNECTING

        if not self.transport.connect():
            self.state = ReceiverState.ERROR
            return False

        self.state = ReceiverState.CONNECTED
        return True

    def receive_line(self, line):
        """
        Parse one complete line received from the machine.

        Returns:
            Parsed reading dictionary, or None for invalid data.
        """

        self.state = ReceiverState.RECEIVING

        return parse_reading(line)

    def disconnect(self):
        self.transport.disconnect()
        self.state = ReceiverState.DISCONNECTED

    def error(self):
        self.state = ReceiverState.ERROR