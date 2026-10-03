import time


# -----------------------------------
# Simulator settings
# -----------------------------------

RFCOMM_DEVICE = "/dev/rfcomm0"

READINGS = [
    "36.75kg",
    "37.60kg",
    "34.50kg",
]

DELAY_SECONDS = 5


# -----------------------------------
# Main simulator
# -----------------------------------

def main():
    print("Machine simulator started.")
    print(f"Bluetooth device: {RFCOMM_DEVICE}")
    print("Press Ctrl+C to stop.\n")

    try:
        with open(RFCOMM_DEVICE, "w") as bluetooth:
            while True:
                for reading in READINGS:
                    message = f"{reading}\n"

                    bluetooth.write(message)
                    bluetooth.flush()

                    print(f"Sending: {reading}")

                    time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\nMachine simulator stopped.")


if __name__ == "__main__":
    main()