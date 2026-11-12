import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk, filedialog, messagebox

from app.receiver import Receiver
from app.bluetooth.simulator import SimulatorTransport


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def filename_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M")


class BluetoothMachineGUI:
    def __init__(self, root):
        self.root = root

        self.root.title("Bluetooth Machine Reader")
        self.root.geometry("800x600")
        self.root.minsize(680, 500)

        self.reading_count = 0
        self.events = queue.Queue()
        self.worker = None
        self.stop_event = threading.Event()
        self.receiver = None
        self.demo_running = False
        self.closing = False

        # Timestamped session lines for TXT export.
        self.session_log = []

        self._configure_style()
        self._build_interface()

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self._process_events)

    def _configure_style(self):
        style = ttk.Style()

        style.configure(
            "Title.TLabel",
            font=("TkDefaultFont", 18, "bold"),
        )

        style.configure(
            "Weight.TLabel",
            font=("TkDefaultFont", 36, "bold"),
        )

    def _build_interface(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(
            header,
            text="Bluetooth Machine Reader",
            style="Title.TLabel",
        ).pack(side="left")

        connection_frame = ttk.LabelFrame(
            main,
            text="Connection",
            padding=12,
        )
        connection_frame.pack(fill="x", pady=(0, 16))

        self.status_label = ttk.Label(
            connection_frame,
            text="Disconnected",
        )
        self.status_label.pack(anchor="w")

        self.device_label = ttk.Label(
            connection_frame,
            text="Device: None",
        )
        self.device_label.pack(anchor="w", pady=(6, 0))

        controls = ttk.Frame(connection_frame)
        controls.pack(fill="x", pady=(12, 0))

        self.demo_button = ttk.Button(
            controls,
            text="Start Demo",
            command=self.start_demo,
        )
        self.demo_button.pack(side="left", padx=(0, 8))

        self.stop_button = ttk.Button(
            controls,
            text="Stop",
            command=self.stop_receiver,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=(0, 8))

        self.export_button = ttk.Button(
            controls,
            text="Export TXT",
            command=self.export_txt,
        )
        self.export_button.pack(side="left")

        reading_frame = ttk.LabelFrame(
            main,
            text="Latest Reading",
            padding=20,
        )
        reading_frame.pack(fill="x", pady=(0, 16))

        self.weight_label = ttk.Label(
            reading_frame,
            text="--.-- kg",
            style="Weight.TLabel",
        )
        self.weight_label.pack()

        self.counter_label = ttk.Label(
            reading_frame,
            text="Readings received: 0",
        )
        self.counter_label.pack(pady=(8, 0))

        log_frame = ttk.LabelFrame(
            main,
            text="Event Log",
            padding=10,
        )
        log_frame.pack(fill="both", expand=True)

        self.event_log = tk.Text(
            log_frame,
            height=10,
            wrap="word",
            state="disabled",
        )
        self.event_log.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.event_log.yview,
        )
        scrollbar.pack(side="right", fill="y")

        self.event_log.configure(
            yscrollcommand=scrollbar.set,
        )

        self.log_event("Application started.")
        self.log_event("Waiting for a connection.")

    def log_event(self, message):
        self.event_log.configure(state="normal")
        self.event_log.insert(
            "end",
            f"{timestamp()} {message}\n",
        )
        self.event_log.see("end")
        self.event_log.configure(state="disabled")

    def record_session_event(self, message):
        """Record one timestamped line for the exported session."""
        self.session_log.append(
            f"{timestamp()} {message}"
        )

    def start_demo(self):
        if self.worker and self.worker.is_alive():
            return

        self.stop_event.clear()
        self.events = queue.Queue()
        self.reading_count = 0
        self.demo_running = True
        self.session_log = []

        self.weight_label.configure(text="--.-- kg")
        self.counter_label.configure(
            text="Readings received: 0"
        )
        self.status_label.configure(text="Connecting...")
        self.device_label.configure(text="Device: Simulator")

        self.demo_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        self.log_event("Connecting to Simulator...")
        self.record_session_event("Connecting to Simulator ...")

        self.worker = threading.Thread(
            target=self._receiver_worker,
            daemon=True,
        )
        self.worker.start()

    def _receiver_worker(self):
        receiver = Receiver(SimulatorTransport())
        self.receiver = receiver

        try:
            if not receiver.connect():
                self.events.put(
                    ("error", "Demo connection failed.")
                )
                return

            self.events.put(("connected", "Simulator"))

            while not self.stop_event.is_set():
                data = receiver.transport.read()

                if self.stop_event.is_set():
                    break

                if not data:
                    self.stop_event.wait(0.05)
                    continue

                readings = receiver.process_data(data)

                for reading in readings:
                    self.events.put(("reading", reading))

        except Exception as error:
            self.events.put(
                ("error", f"Demo receiver error: {error}")
            )

        finally:
            try:
                receiver.disconnect()
            except OSError:
                pass

            self.events.put(("stopped", None))

    def stop_receiver(self):
        if self.stop_event.is_set():
            return

        self.stop_event.set()
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Stopping...")

    def _process_events(self):
        if self.closing:
            return

        while True:
            try:
                event, data = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "connected":
                self.status_label.configure(text="Connected")
                self.device_label.configure(
                    text=f"Device: {data}"
                )
                self.log_event("Connected")
                self.record_session_event("Connected")

            elif event == "reading":
                weight = data["weight"]
                unit = data["unit"]

                self.reading_count += 1

                self.weight_label.configure(
                    text=f"{weight:.2f} {unit}"
                )
                self.counter_label.configure(
                    text=(
                        "Readings received: "
                        f"{self.reading_count}"
                    )
                )

                reading_line = f"{weight:.2f}{unit}"
                self.log_event(reading_line)
                self.record_session_event(reading_line)

            elif event == "error":
                self.status_label.configure(text="Error")
                self.log_event(data)

                # Preserve a connection failure in the report.
                self.record_session_event(
                    f"Connection error: {data}"
                )

            elif event == "stopped":
                self.status_label.configure(text="Disconnected")
                self.log_event("Disconnected")
                self.record_session_event("Disconnected")

                self.demo_running = False
                self.demo_button.configure(state="normal")
                self.stop_button.configure(state="disabled")

        self.root.after(100, self._process_events)

    def export_txt(self):
        if not self.session_log:
            messagebox.showinfo(
                "Nothing to Export",
                "Start a session and collect some events first.",
                parent=self.root,
            )
            return

        default_name = (
            f"serial_{filename_timestamp()}.txt"
        )

        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Weighing Session",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.session_log))
                file.write("\n")

        except OSError as error:
            messagebox.showerror(
                "Export Failed",
                f"Could not save the file:\n{error}",
                parent=self.root,
            )
            return

        self.log_event(f"Exported session to {path}")

        messagebox.showinfo(
            "Export Successful",
            f"Session saved to:\n{path}",
            parent=self.root,
        )

    def close(self):
        self.closing = True
        self.stop_event.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    BluetoothMachineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()