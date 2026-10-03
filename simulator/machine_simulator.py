import time


# -----------------------------------
# Simulator settings
# -----------------------------------

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
    print("Press Ctrl+C to stop.\n")

    while True:
        for reading in READINGS:
            print(f"Sending: {reading}")

            # Bluetooth sending will go here later.
            # For now, we only simulate the machine output.

            time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()