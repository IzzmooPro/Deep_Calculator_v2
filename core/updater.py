"""
Otomatik güncelleme modülü.

Kullanım:
  - Program açılışta arka planda UpdateChecker ile kontrol eder.
  - Kullanıcı "Hakkında" penceresinden manuel kontrol başlatabilir.

Güvenlik:
  - Kurulum dosyası yalnızca Windows'ta ve yalnızca https://github.com/
    adresinden indirilir; diğer sistemlerde sürüm sayfası açılır.
  - GitHub, sürüm dosyaları için SHA-256 özeti ("digest") yayımlıyorsa
    indirilen dosya bu özetle doğrulanır; uyuşmazsa dosya silinir ve
    çalıştırılmaz.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

from PyQt6.QtCore import QThread, pyqtSignal

from core.constants import VERSION

OWNER_REPO   = "IzzmooPro/Deep_Calculator_v2"
GITHUB_API   = f"https://api.github.com/repos/{OWNER_REPO}/releases/latest"
RELEASES_URL = f"https://github.com/{OWNER_REPO}/releases/latest"

_ALLOWED_DOWNLOAD_PREFIX = "https://github.com/"
_USER_AGENT = "DeepCalculator-Updater/1.0"


def _parse_version(tag: str) -> tuple[int, ...]:
    """'v2.1.0' → (2, 1, 0)"""
    tag = tag.lstrip("v")
    try:
        return tuple(int(x) for x in tag.split("."))
    except ValueError:
        return (0,)


def _current_version() -> tuple[int, ...]:
    return _parse_version(VERSION)


def _pick_setup_asset(assets: list[dict]) -> dict | None:
    """Önce adında 'setup' geçen .exe'yi, yoksa herhangi bir .exe'yi seçer."""
    exes = [a for a in assets if a.get("name", "").lower().endswith(".exe")]
    for asset in exes:
        if "setup" in asset.get("name", "").lower():
            return asset
    return exes[0] if exes else None


def _sha256_from_digest(digest: str) -> str:
    """GitHub 'digest' alanı: 'sha256:<hex>' → '<hex>' (başka algoritma ise '')."""
    algo, _, value = (digest or "").partition(":")
    return value.lower() if algo.lower() == "sha256" and value else ""


class UpdateChecker(QThread):
    """Arka planda GitHub API'yi kontrol eden thread."""

    update_available = pyqtSignal(str, str, str)   # (yeni_sürüm, download_url, sha256)
    up_to_date       = pyqtSignal()
    check_failed     = pyqtSignal()

    def run(self) -> None:
        try:
            req = urllib.request.Request(GITHUB_API, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "")
            if not tag:
                self.check_failed.emit()
                return

            download_url, sha256 = "", ""
            # Otomatik kurulum yalnızca Windows'ta; diğer sistemlerde URL boş
            # bırakılır ve UI sürüm sayfasını açar.
            if sys.platform == "win32":
                asset = _pick_setup_asset(data.get("assets", []))
                if asset:
                    url = asset.get("browser_download_url", "")
                    if url.startswith(_ALLOWED_DOWNLOAD_PREFIX):
                        download_url = url
                        sha256 = _sha256_from_digest(asset.get("digest", ""))

            if _parse_version(tag) > _current_version():
                self.update_available.emit(tag, download_url, sha256)
            else:
                self.up_to_date.emit()

        except Exception:
            self.check_failed.emit()


class SetupDownloader(QThread):
    """Setup dosyasını indiren (ve varsa SHA-256 ile doğrulayan) thread."""

    progress    = pyqtSignal(int)          # 0-100
    finished_ok = pyqtSignal(str)          # indirilen dosya yolu
    failed      = pyqtSignal()

    def __init__(self, url: str, expected_sha256: str = "") -> None:
        super().__init__()
        self._url = url
        self._expected_sha256 = expected_sha256.lower()

    def run(self) -> None:
        tmp_path = ""
        try:
            if not self._url.startswith(_ALLOWED_DOWNLOAD_PREFIX):
                raise ValueError("İzin verilmeyen indirme adresi")

            fd, tmp_path = tempfile.mkstemp(suffix="_DeepCalculator_Setup.exe")
            hasher = hashlib.sha256()
            req = urllib.request.Request(self._url, headers={"User-Agent": _USER_AGENT})

            with os.fdopen(fd, "wb") as out, urllib.request.urlopen(req, timeout=30) as resp:
                total = int(resp.headers.get("Content-Length") or 0)
                done = 0
                while chunk := resp.read(64 * 1024):
                    out.write(chunk)
                    hasher.update(chunk)
                    done += len(chunk)
                    if total > 0:
                        self.progress.emit(min(int(done * 100 / total), 99))

            if self._expected_sha256 and hasher.hexdigest() != self._expected_sha256:
                raise ValueError("SHA-256 doğrulaması başarısız")

            self.progress.emit(100)
            self.finished_ok.emit(tmp_path)

        except Exception:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            self.failed.emit()


def launch_setup_and_quit(setup_path: str) -> None:
    """Setup dosyasını başlatır ve programı kapatır."""
    if sys.platform == "win32":
        os.startfile(setup_path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen([setup_path])
    _quit_app()


def _quit_app() -> None:
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.quit()
