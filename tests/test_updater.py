from core.updater import _parse_version, _pick_setup_asset, _sha256_from_digest


def test_parse_version():
    assert _parse_version("v2.1.0") == (2, 1, 0)
    assert _parse_version("2.0.1") > _parse_version("v2.0.0")
    assert _parse_version("v2.1.0-beta") == (0,)


def test_pick_setup_asset_prefers_setup():
    assets = [
        {"name": "DeepCalculator.exe"},
        {"name": "notes.txt"},
        {"name": "DeepCalculator_Setup.exe"},
    ]
    assert _pick_setup_asset(assets)["name"] == "DeepCalculator_Setup.exe"


def test_pick_setup_asset_fallbacks():
    assert _pick_setup_asset([{"name": "app.EXE"}])["name"] == "app.EXE"
    assert _pick_setup_asset([{"name": "app.zip"}]) is None
    assert _pick_setup_asset([]) is None


def test_sha256_from_digest():
    assert _sha256_from_digest("sha256:ABCDEF") == "abcdef"
    assert _sha256_from_digest("md5:abc") == ""
    assert _sha256_from_digest("") == ""


def test_background_task_delivers_signal_to_main_thread():
    import threading
    import time

    from PyQt6.QtCore import QCoreApplication, pyqtSignal

    from core.updater import _BackgroundTask

    app = QCoreApplication.instance() or QCoreApplication([])

    class Task(_BackgroundTask):
        done = pyqtSignal(str)

        def run(self) -> None:
            self.done.emit(threading.current_thread().name)

    received: list[tuple[str, str]] = []
    task = Task()
    task.done.connect(lambda worker: received.append((worker, threading.current_thread().name)))
    task.start()

    deadline = time.time() + 2
    while not received and time.time() < deadline:
        app.processEvents()
        time.sleep(0.01)

    assert received, "sinyal ulaşmadı"
    worker, receiver = received[0]
    assert worker != "MainThread"      # iş arka planda çalıştı
    assert receiver == "MainThread"    # slot ana thread'de çağrıldı
