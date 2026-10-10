import pytest

from app import bluetooth_receiver


class FakeTransport:

    def __init__(self):
        self.connected = False
        self.disconnected = False

    @property
    def device_identifier(self):
        return "CPF25015"

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
        self.disconnected = True

    def read(self):
        raise OSError("Bluetooth connection lost")

    def is_connected(self):
        return self.connected

def test_read_error_is_handled_and_connection_is_closed(
    monkeypatch,
    capsys,
    tmp_path,
):
    transport = FakeTransport()

    class FakeReceiver:

        def __init__(self):
            self.transport = transport

        def connect(self):
            return self.transport.connect()

        def disconnect(self):
            self.transport.disconnect()

        def process_data(self, data):
            return []

    class FakeRecorder:

        def __init__(self):
            self.messages = []
            self.stopped = False

        def start(self, device_identifier):
            return tmp_path / "diagnostics.txt"

        def record(self, message):
            self.messages.append(message)

        def stop(self):
            self.stopped = True

    recorder = FakeRecorder()

    monkeypatch.setattr(
        bluetooth_receiver,
        "Receiver",
        FakeReceiver,
    )

    monkeypatch.setattr(
        bluetooth_receiver,
        "DiagnosticRecorder",
        lambda: recorder,
    )

    # The application should handle the read error without
    # allowing the exception to escape.
    bluetooth_receiver.receive()

    output = capsys.readouterr().out

    assert "CPF25015" in output
    assert "Bluetooth connection lost" in output
    assert transport.disconnected is True
    assert recorder.stopped is True

    assert any(
        "Bluetooth connection lost" in message
        for message in recorder.messages
    )

    assert "Disconnected" in recorder.messages



def test_receiver_stops_when_transport_disconnects(
    monkeypatch,
    capsys,
    tmp_path,
):
    class FakeTransport:
        def __init__(self):
            self.connected = False
            self.disconnected = False
            self.read_count = 0

        @property
        def device_identifier(self):
            return "CPF25015"

        def connect(self):
            self.connected = True
            return True

        def disconnect(self):
            self.connected = False
            self.disconnected = True

        def read(self):
            self.read_count += 1

            if self.read_count == 1:
                self.connected = False
                return ""

            raise AssertionError(
                "Receiver continued reading after disconnect"
            )

        def is_connected(self):
            return self.connected

    transport = FakeTransport()

    class FakeReceiver:
        def __init__(self):
            self.transport = transport

        def connect(self):
            return self.transport.connect()

        def disconnect(self):
            self.transport.disconnect()

        def process_data(self, data):
            return []

    class FakeRecorder:
        def __init__(self):
            self.messages = []
            self.stopped = False

        def start(self, device_identifier):
            return tmp_path / "diagnostics.txt"

        def record(self, message):
            self.messages.append(message)

        def stop(self):
            self.stopped = True

    recorder = FakeRecorder()

    monkeypatch.setattr(
        bluetooth_receiver,
        "Receiver",
        FakeReceiver,
    )

    monkeypatch.setattr(
        bluetooth_receiver,
        "DiagnosticRecorder",
        lambda: recorder,
    )

    bluetooth_receiver.receive()

    output = capsys.readouterr().out

    assert transport.read_count == 1
    assert transport.disconnected is True
    assert recorder.stopped is True
    assert "Disconnected" in output
    assert "Bluetooth read error" not in output


def test_receiver_state_is_disconnected_after_transport_loss(
    monkeypatch,
    tmp_path,
):
    class FakeTransport:
        def __init__(self):
            self.connected = False

        @property
        def device_identifier(self):
            return "CPF25015"

        def connect(self):
            self.connected = True
            return True

        def disconnect(self):
            self.connected = False

        def read(self):
            self.connected = False
            return ""

        def is_connected(self):
            return self.connected

    transport = FakeTransport()

    class FakeReceiver:
        def __init__(self):
            from app.receiver import ReceiverState

            self.transport = transport
            self.state = ReceiverState.DISCONNECTED

        def connect(self):
            from app.receiver import ReceiverState

            result = self.transport.connect()

            if result:
                self.state = ReceiverState.CONNECTED

            return result

        def disconnect(self):
            from app.receiver import ReceiverState

            self.transport.disconnect()
            self.state = ReceiverState.DISCONNECTED

    class FakeRecorder:
        def start(self, device_identifier):
            return tmp_path / "diagnostics.txt"

        def record(self, message):
            pass

        def stop(self):
            pass

    receiver = FakeReceiver()

    monkeypatch.setattr(
        bluetooth_receiver,
        "Receiver",
        lambda: receiver,
    )

    monkeypatch.setattr(
        bluetooth_receiver,
        "DiagnosticRecorder",
        FakeRecorder,
    )

    bluetooth_receiver.receive()

    from app.receiver import ReceiverState

    assert receiver.state == ReceiverState.DISCONNECTED
    assert transport.connected is False

def test_connection_failure_stops_recorder_and_disconnects(
    monkeypatch,
    capsys,
    tmp_path,
):
    class FakeTransport:
        device_identifier = "CPF25015"

        def __init__(self):
            self.disconnected = False

        def disconnect(self):
            self.disconnected = True

    transport = FakeTransport()

    class FakeReceiver:
        def __init__(self):
            self.transport = transport
            self.disconnect_called = False

        def connect(self):
            return False

        def disconnect(self):
            self.disconnect_called = True
            self.transport.disconnect()

    class FakeRecorder:
        def __init__(self):
            self.messages = []
            self.stopped = False

        def start(self, device_identifier):
            return tmp_path / "diagnostics.txt"

        def record(self, message):
            self.messages.append(message)

        def stop(self):
            self.stopped = True

    receiver = FakeReceiver()
    recorder = FakeRecorder()

    monkeypatch.setattr(
        bluetooth_receiver,
        "Receiver",
        lambda: receiver,
    )
    monkeypatch.setattr(
        bluetooth_receiver,
        "DiagnosticRecorder",
        lambda: recorder,
    )

    bluetooth_receiver.receive()

    output = capsys.readouterr().out

    assert "Connection failed" in output
    assert recorder.stopped is True
    assert receiver.disconnect_called is True
    assert transport.disconnected is True
    assert "Connection failed." in recorder.messages