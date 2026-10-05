from datetime import datetime
from pathlib import Path


class DiagnosticRecorder:

    def __init__(self, directory="diagnostics"):
        self.directory = Path(directory)
        self.file = None

    def start(self, device_identifier):
        self.directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = (
            f"{device_identifier}_{timestamp}.txt"
        )

        path = self.directory / filename

        self.file = open(path, "a", encoding="utf-8")

        return path

    def record(self, message):
        if self.file is None:
            return

        timestamp = datetime.now().strftime(
            "%H:%M:%S.%f"
        )[:-3]

        self.file.write(
            f"{timestamp} {message}\n"
        )

        self.file.flush()

    def stop(self):
        if self.file is not None:
            self.file.close()
            self.file = None