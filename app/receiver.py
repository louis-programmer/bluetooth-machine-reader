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
        self.buffer = ""

    def connect(self):
        self.state = ReceiverState.CONNECTING

        if not self.transport.connect():
            self.state = ReceiverState.ERROR
            return False

        self.state = ReceiverState.CONNECTED
        self.buffer = ""

        return True

    def receive_line(self, line):
        """
        Parse one complete line received from the machine.

        Returns:
            Parsed reading dictionary, or None for invalid data.
        """

        self.state = ReceiverState.RECEIVING

        return parse_reading(line)

    def process_data(self, data):
        """
        Process raw data received from the Bluetooth transport.

        Bluetooth is a stream, so one call may contain:
            - part of a message
            - one complete message
            - several complete messages

        Returns:
            A list of parsed readings.
        """

        if not data:
            return []

        self.buffer += data

        readings = []

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)

            line = line.strip()

            if not line:
                continue

            reading = self.receive_line(line)

            if reading is not None:
                readings.append(reading)

        return readings

    def disconnect(self):
        self.transport.disconnect()
        self.buffer = ""
        self.state = ReceiverState.DISCONNECTED

    def error(self):
        self.state = ReceiverState.ERROR