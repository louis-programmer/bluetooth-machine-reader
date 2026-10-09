from app.diagnostics.recorder import DiagnosticRecorder


def test_recorder_starts(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    path = recorder.start("CPF25015")

    assert path.exists()
    assert path.name.startswith("CPF25015_")
    assert path.suffix == ".txt"

    recorder.stop()


def test_recorder_writes_message(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    recorder.start("CPF25015")

    recorder.record("RAW: 31.00kg")

    recorder.stop()

    files = list(tmp_path.glob("*.txt"))

    assert len(files) == 1

    content = files[0].read_text()

    assert "RAW: 31.00kg" in content


def test_recorder_writes_multiple_messages(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    recorder.start("CPF25015")

    recorder.record("CONNECT")
    recorder.record("RAW: 31.00kg")
    recorder.record("RAW: 33.00kg")
    recorder.record("DISCONNECT")

    recorder.stop()

    files = list(tmp_path.glob("*.txt"))

    content = files[0].read_text()

    assert "CONNECT" in content
    assert "RAW: 31.00kg" in content
    assert "RAW: 33.00kg" in content
    assert "DISCONNECT" in content


def test_recorder_ignores_message_before_start(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    recorder.record("RAW: 31.00kg")

    files = list(tmp_path.glob("*.txt"))

    assert files == []


def test_recorder_can_be_stopped_safely(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    recorder.start("CPF25015")

    recorder.stop()
    recorder.stop()

    assert recorder.file is None


def test_recorder_closes_previous_file_when_restarted(tmp_path):
    recorder = DiagnosticRecorder(tmp_path)

    recorder.start("CPF25015")
    previous_file = recorder.file

    recorder.start("CPF25015")

    assert previous_file.closed is True
    assert recorder.file is not previous_file

    recorder.stop()