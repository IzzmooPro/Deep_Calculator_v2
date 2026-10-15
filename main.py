"""
Deep Calculator — giriş noktası.

Tek instance kontrolü: program zaten açıksa ikinci kopya açılmaz;
mevcut pencere öne getirilir. Öne getirme isteği yerel bir soket
(QLocalServer) üzerinden gönderilir — pencere başlığına bakılmaz; böylece
başlık çevrilebilir ve Windows'un kendi "Hesap Makinesi" penceresiyle
karışmaz.
"""

from __future__ import annotations

import sys
import traceback

# ── Import hataları da yakalanır — CMD asla sessizce kapanmaz ────────────────
try:
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QApplication

    from PyQt6.QtNetwork import QLocalServer, QLocalSocket

    from core import ORG, APP
    from ui import CalculatorWindow
except Exception:
    traceback.print_exc()
    input("\nBAŞLATMA HATASI — Devam etmek için Enter'a basın...")
    sys.exit(1)


# ── Tek Instance Kontrolü ─────────────────────────────────────────────────────

def _server_name() -> str:
    """Kullanıcıya özel yerel soket adı (farklı kullanıcılar birbirini görmez)."""
    import getpass
    try:
        user = getpass.getuser()
    except Exception:
        user = "user"
    return f"DeepCalculator-{user}"


def _check_single_instance() -> bool:
    """
    Platform bağımsız giriş noktası.
    True döndürürse program zaten çalışıyor → çık.
    """
    if sys.platform == "win32":
        return _already_running_windows()
    return _already_running_unix()


def _already_running_windows() -> bool:
    """Windows: Named Mutex ile tek instance kontrolü."""
    import ctypes

    MUTEX_NAME = "Global\\DeepCalculator_SingleInstance_Mutex"
    handle = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    last_error = ctypes.windll.kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        _bring_existing_window_to_front()
        return True

    _already_running_windows._mutex_handle = handle  # type: ignore[attr-defined]
    return False


def _bring_existing_window_to_front() -> None:
    """Açık olan kopyaya yerel soket üzerinden "öne gel" mesajı gönderir."""
    if sys.platform == "win32":
        # Kullanıcının az önce başlattığı bu süreç ön plana geçme hakkına
        # sahiptir; bu hakkı açık olan kopyaya devreder.
        import ctypes
        ASFW_ANY = -1
        ctypes.windll.user32.AllowSetForegroundWindow(ASFW_ANY)

    sock = QLocalSocket()
    sock.connectToServer(_server_name())
    if sock.waitForConnected(1000):
        sock.write(b"show")
        sock.waitForBytesWritten(1000)
        sock.disconnectFromServer()


def _listen_for_other_instances(window: "CalculatorWindow") -> "QLocalServer":
    """İkinci kopyadan gelen "öne gel" isteklerini dinler."""
    server = QLocalServer(window)
    QLocalServer.removeServer(_server_name())  # önceki çökmeden kalan soket
    server.listen(_server_name())

    def on_connection() -> None:
        conn = server.nextPendingConnection()
        if conn is not None:
            conn.disconnected.connect(conn.deleteLater)
        window.bring_to_front()

    server.newConnection.connect(on_connection)
    return server


def _already_running_unix() -> bool:
    """Unix/macOS: Dosya kilidi ile tek instance kontrolü."""
    import fcntl, tempfile, os
    lock_path = os.path.join(tempfile.gettempdir(), "deep_calculator.lock")
    try:
        lf = open(lock_path, "w")
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _already_running_unix._lock_file = lf  # type: ignore[attr-defined]
        return False
    except OSError:
        _bring_existing_window_to_front()
        return True


# ── Ana Fonksiyon ─────────────────────────────────────────────────────────────

def _install_excepthook(app: "QApplication") -> None:
    """Yakalanmayan tüm Python hatalarını dialog ile göster."""
    from PyQt6.QtWidgets import QMessageBox

    def _hook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(msg, file=sys.stderr, flush=True)
        try:
            box = QMessageBox()
            box.setWindowTitle("Uygulama Hatası")
            box.setIcon(QMessageBox.Icon.Critical)
            box.setText("Beklenmeyen bir hata oluştu:")
            box.setDetailedText(msg)
            box.exec()
        except Exception:
            pass

    sys.excepthook = _hook


def main() -> None:
    if _check_single_instance():
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName(APP)
    app.setOrganizationName(ORG)
    if sys.platform == "darwin":
        _font = "SF Pro Display"
    elif sys.platform == "win32":
        _font = "Segoe UI Variable"
    else:
        _font = "Segoe UI"
    app.setFont(QFont(_font, 10))

    _install_excepthook(app)

    window = CalculatorWindow()
    window.show()
    _listen_for_other_instances(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass  # sys.exit() normal akış — sessizce çık
    except Exception:
        traceback.print_exc()
        input("\nÇALIŞMA HATASI — Devam etmek için Enter'a basın...")
