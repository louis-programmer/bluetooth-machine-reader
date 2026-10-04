from app.receiver import Receiver, ReceiverState


class FakeTransport:

    def __init__(self, connect_result=True):
        self.connect_result = connect_result
        self.connected = False
        self.disconnected = False

    def connect(self):
        self.connected = self.connect_result
        return self.connect_result

    def disconnect(self):
        self.connected = False
        self.disconnected = True

    def read(self):
        return ""

    def is_connected(self):
        return self.connected


def test_receiver_starts_disconnected():
    receiver = Receiver(FakeTransport())

    assert receiver.state == ReceiverState.DISCONNECTED


def test_receiver_connects_successfully():
    transport = FakeTransport()

    receiver = Receiver(transport)

    result = receiver.connect()

    assert result is True
    assert receiver.state == ReceiverState.CONNECTED
    assert transport.connected is True


def test_receiver_connection_error():
    transport = FakeTransport(connect_result=False)

    receiver = Receiver(transport)

    result = receiver.connect()

    assert result is False
    assert receiver.state == ReceiverState.ERROR
    assert transport.connected is False


def test_receiver_disconnects():
    transport = FakeTransport()

    receiver = Receiver(transport)

    receiver.connect()
    receiver.disconnect()

    assert transport.disconnected is True
    assert transport.connected is False
    assert receiver.state == ReceiverState.DISCONNECTED


def test_receiver_error():
    receiver = Receiver(FakeTransport())

    receiver.error()

    assert receiver.state == ReceiverState.ERROR


def test_receiver_processes_reading():
    receiver = Receiver(FakeTransport())

    result = receiver.receive_line("37.00kg")

    assert result == {
        "weight": 37.00,
        "unit": "kg",
    }

    assert receiver.state == ReceiverState.RECEIVING


def test_receiver_rejects_invalid_reading():
    receiver = Receiver(FakeTransport())

    result = receiver.receive_line("hello")

    assert result is None
    assert receiver.state == ReceiverState.RECEIVING