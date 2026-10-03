from app.parser import parse_reading
import time


# -----------------------------------
# Bluetooth receiver settings
# -----------------------------------

RFCOMM_DEVICE = "/dev/rfcomm0"


# -----------------------------------
# Bluetooth receiver
# -----------------------------------

def receive():
    print("Bluetooth receiver started.")
    print(f"Device: {RFCOMM_DEVICE}")
    print("Waiting for machine data...\n")

    buffer = ""

    with open(RFCOMM_DEVICE, "r") as bluetooth:
        while True:
            data = bluetooth.read(1)

            if not data:
                time.sleep(0.01)
                continue

            buffer += data

            if "\n" in buffer:
                lines = buffer.split("\n")

                buffer = lines.pop()

                for line in lines:
                    line = line.strip()

                    if not line:
                        continue

                    reading = parse_reading(line)

                    if reading is None:
                        print(f"Invalid reading: {line}")
                        continue

                    print(
                        f"Weight: {reading['weight']:.2f} "
                        f"{reading['unit']}"
                    )


if __name__ == "__main__":
    receive()