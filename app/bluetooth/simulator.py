import time

from app.bluetooth.transport import BluetoothTransport


class SimulatorTransport(BluetoothTransport):

    def __init__(self):
        self.connected = False
        self.readings = [
            "37.00kg\n",
            "36.95kg\n",
        ]
        self.index = 0
        self.last_read = 0

    def connect(self):
        self.connected = True
        self.last_read = time.time()
        return True

    def disconnect(self):
        self.connected = False

    def read(self):
        if not self.connected:
            return ""

        if time.time() - self.last_read < 2:
            return ""

        reading = self.readings[self.index]

        self.index = (self.index + 1) % len(self.readings)
        self.last_read = time.time()

        return reading

    def is_connected(self):
        return self.connected