"""
Otomatik güncelleme modülü.

Kullanım:
  - Program açılışta arka planda check_for_updates() çağrılır.
  - Kullanıcı ayarlar menüsünden manuel check_for_updates_manual() çağırabilir.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os

from PyQt6.QtCore import QThread, pyqtSignal, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from core.constants import VERSION

GITHUB_API = "https://api.github.com/repos/IzzmooPro/Deep_Calculator_v2/releases/latest"
OWNER_REPO = "IzzmooPro/Deep_Calculator_v2"


def _parse_version(tag: str) -> tuple[int, ...]:
    """'v2.1.0' → (2, 1, 0)"""
    tag = tag.lstrip("v")
    try:
        return tuple(int(x) for x in tag.split("."))
    except ValueError:
        return (0,)


def _current_version() -> tuple[int, ...]:
    return _parse_version(VERSION)


class UpdateChecker(QThread):
    """Arka planda GitHub API'yi kontrol eden thread."""

    update_available = pyqtSignal(str, str)   # (yeni_sürüm, download_url)
    up_to_date       = pyqtSignal()
    check_failed     = pyqtSignal()

    def run(self) -> None:
        try:
            import urllib.request, json
            req = urllib.request.Request(
                GITHUB_API,
                headers={"User-Agent": "DeepCalculator-Updater/1.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "")
            if not tag:
                self.check_failed.emit()
                return

            assets = data.get("assets", [])
            download_url = ""
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe") and "setup" in name or name.endswith(".exe"):
                    download_url = asset.get("browser_download_url", "")
                    break

            if _parse_version(tag) > _current_version():
                self.update_available.emit(tag, download_url)
            else:
                self.up_to_date.emit()

        except Exception:
            self.check_failed.emit()


class SetupDownloader(QThread):
    """Setup dosyasını indiren thread."""

    progress    = pyqtSignal(int)          # 0-100
    finished_ok = pyqtSignal(str)          # indirilen dosya yolu
    failed      = pyqtSignal()

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url

    def run(self) -> None:
        try:
            import urllib.request

            tmp = tempfile.NamedTemporaryFile(
                suffix="_DeepCalculator_Setup.exe",
                delete=False
            )
            tmp_path = tmp.name
            tmp.close()

            def reporthook(count, block_size, total_size):
                if total_size > 0:
                    pct = int(count * block_size * 100 / total_size)
                    self.progress.emit(min(pct, 99))

            urllib.request.urlretrieve(self._url, tmp_path, reporthook)
            self.progress.emit(100)
            self.finished_ok.emit(tmp_path)

        except Exception:
            self.failed.emit()


def launch_setup_and_quit(setup_path: str) -> None:
    """Setup dosyasını başlatır ve programı kapatır."""
    if sys.platform == "win32":
        os.startfile(setup_path)  # type: ignore
    else:
        subprocess.Popen([setup_path])
    QApplication_quit()


def QApplication_quit() -> None:
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.quit()
