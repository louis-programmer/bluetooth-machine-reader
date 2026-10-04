from app.receiver import Receiver
from app.config import TRANSPORT

def receive():
    receiver = Receiver()

    print("Bluetooth receiver started.")
    print(f"Transport: {TRANSPORT}")
    print("Connecting...\n")

    if not receiver.connect():
        print("Connection failed.")
        return

    print("Connected.\n")

    buffer = ""

    try:
        while True:
            data = receiver.transport.read()

            if not data:
                continue

            buffer += data

            if "\n" in buffer:
                lines = buffer.split("\n")
                buffer = lines.pop()

                for line in lines:
                    line = line.strip()

                    if not line:
                        continue

                    reading = receiver.receive_line(line)

                    if reading is None:
                        print(f"Invalid reading: {line}")
                        continue

                    print(
                        f"Weight: {reading['weight']:.2f} "
                        f"{reading['unit']}"
                    )

    except KeyboardInterrupt:
        print("\nStopping receiver...")

    finally:
        receiver.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    receive()