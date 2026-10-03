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

                    if line:
                        print(f"Received: {line}")


if __name__ == "__main__":
    receive()