from datetime import datetime

from app.receiver import Receiver
from app.diagnostics.recorder import DiagnosticRecorder
from app.formatter import format_reading


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def receive():
    receiver = Receiver()
    recorder = DiagnosticRecorder()

    try:
        device_identifier = receiver.transport.device_identifier
    except AttributeError:
        device_identifier = None

    if not device_identifier:
        device_identifier = "Unknown Device"

    # -----------------------------------
    # Connecting
    # -----------------------------------

    connecting_message = (
        f"{timestamp()} Connecting to "
        f"{device_identifier} ..."
    )

    print(connecting_message)

    try:
        recorder.start(device_identifier)
        recorder.record(
            f"Connecting to {device_identifier} ..."
        )
    except OSError as error:
        recorder = None

        print(
            f"Diagnostic recording unavailable: "
            f"{error}"
        )

    # -----------------------------------
    # Connect
    # -----------------------------------

    if not receiver.connect():
        print(
            f"{timestamp()} Connection failed."
        )

        if recorder is not None:
            try:
                recorder.record("Connection failed.")
                recorder.stop()
            except OSError:
                recorder.stop()

        return

    print(f"{timestamp()} Connected")

    if recorder is not None:
        try:
            recorder.record("Connected")
        except OSError:
            recorder.stop()
            recorder = None

    # -----------------------------------
    # Receive
    # -----------------------------------

    try:
        while True:
            data = receiver.transport.read()

            if not data:
                continue

            # Diagnostic recording happens silently.
            if recorder is not None:
                try:
                    recorder.record(
                        f"RAW: {data.rstrip()!r}"
                    )
                except OSError:
                    recorder.stop()
                    recorder = None

            readings = receiver.process_data(data)

            for reading in readings:
                message = (
                    f"{timestamp()}   "
                    f"{format_reading(reading)}"
                )

                # Client-facing output only.
                print(message)

                # Diagnostic copy of the parsed reading.
                if recorder is not None:
                    try:
                        recorder.record(
                            f"  "
                            f"{reading['weight']:.2f}"
                            f"{reading['unit']}"
                        )
                    except OSError:
                        recorder.stop()
                        recorder = None

    except KeyboardInterrupt:
        print(
            f"\n{timestamp()} Stopping receiver..."
        )

    finally:
        if recorder is not None:
            try:
                recorder.record("Disconnected")
                recorder.stop()
            except OSError:
                recorder.stop()

        receiver.disconnect()

        print(f"{timestamp()} Disconnected")


if __name__ == "__main__":
    receive()