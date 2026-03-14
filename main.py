"""
Deep Calculator — giriş noktası.

Tek instance kontrolü: program zaten açıksa ikinci kopya açılmaz;
mevcut pencere öne getirilir.
"""

from __future__ import annotations

import sys
import traceback

# ── Import hataları da yakalanır — CMD asla sessizce kapanmaz ────────────────
try:
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QApplication

    from core import ORG, APP, WINDOW_TITLE
    from ui import CalculatorWindow
except Exception:
    traceback.print_exc()
    input("\nBAŞLATMA HATASI — Devam etmek için Enter'a basın...")
    sys.exit(1)


# ── Tek Instance Kontrolü ─────────────────────────────────────────────────────

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
    """Açık olan hesap makinesi penceresini öne getirir."""
    import ctypes
    hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW_TITLE)
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)


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

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass  # sys.exit() normal akış — sessizce çık
    except Exception:
        traceback.print_exc()
        input("\nÇALIŞMA HATASI — Devam etmek için Enter'a basın...")
