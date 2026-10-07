import os
import tty

from app.bluetooth.transport import BluetoothTransport


class RFCOMMTransport(BluetoothTransport):

    def __init__(
        self,
        device="/dev/rfcomm0",
        device_identifier=None
    ):
        self.device = device
        self.device_identifier = device_identifier
        self.connection = None

    def connect(self):
        try:
            self.connection = open(self.device, "rb", buffering=0)
            tty.setraw(self.connection.fileno())
        except OSError:
            self.connection = None
            return False

        return True

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def read(self):
        if self.connection is None:
            return ""

        data = os.read(
            self.connection.fileno(),
            1024
        )

        return data.decode(
            "utf-8",
            errors="replace"
        )

    def is_connected(self):
        return self.connection is not None