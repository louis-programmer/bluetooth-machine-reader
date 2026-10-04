import tty

from app.bluetooth.transport import BluetoothTransport


class RFCOMMTransport(BluetoothTransport):

    def __init__(self, device="/dev/rfcomm0"):
        self.device = device
        self.connection = None

    def connect(self):
        try:
            self.connection = open(self.device, "r")
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

        return self.connection.read(1)

    def is_connected(self):
        return self.connection is not None