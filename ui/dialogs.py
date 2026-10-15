"""
Yardımcı diyaloglar: Hakkında, Geri Bildirim, Güncelleme bildirimi, İndirme.

window.py'dan ayrıştırıldı. Arka plan işleri (UpdateChecker,
SetupDownloader) ana pencereye bağlanır (parent); böylece diyalog kapansa
bile çalışan bir iş silinip programı çökertmez.
"""

from __future__ import annotations

import urllib.parse
from typing import Callable

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

from core.constants import VERSION
from core.i18n import t
from core.updater import (
    OWNER_REPO, RELEASES_URL, SetupDownloader, UpdateChecker, launch_setup_and_quit,
)
from ui.theme import ThemePalette, dialog_button_style

REPO_URL = f"https://github.com/{OWNER_REPO}"

# (yeni_sürüm, download_url, sha256)
UpdateCallback = Callable[[str, str, str], None]


# ── Ortak yardımcılar ─────────────────────────────────────────────────────────

def open_releases_page() -> None:
    QDesktopServices.openUrl(QUrl(RELEASES_URL))


def _make_dialog(parent: QWidget, p: ThemePalette, title: str,
                 w: int, h: int, margins: tuple[int, int, int, int], spacing: int,
                 ) -> tuple[QDialog, QVBoxLayout]:
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setFixedSize(w, h)
    dlg.setStyleSheet(f"QDialog {{ background-color: {p.bg}; }}")
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(*margins)
    lay.setSpacing(spacing)
    return dlg, lay


def _make_button(p: ThemePalette, text: str, primary: bool = False, padding: int = 14) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(32)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(dialog_button_style(p, primary, padding))
    return btn


def _label(text: str, css: str, center: bool = False, wrap: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(css)
    if center:
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(wrap)
    return lbl


# ── Hakkında ──────────────────────────────────────────────────────────────────

def show_about(parent: QWidget, p: ThemePalette, on_update: UpdateCallback) -> None:
    dlg, lay = _make_dialog(parent, p, t("about.title"), 300, 340, (24, 24, 24, 20), 10)

    lay.addWidget(_label("🧮  Deep Calculator",
                         f"color: {p.text}; font-size: 14pt; font-weight: 700;", center=True))
    lay.addWidget(_label(t("about.version", version=VERSION),
                         f"color: {p.history_text}; font-size: 9pt;", center=True))
    lay.addSpacing(6)

    for label, value in [
        (t("about.developer"), "Izzmoo"),
        (t("about.contact"),   "IzzmooPro@gmail.com"),
        (t("about.license"),   t("about.license.value")),
    ]:
        lay.addWidget(_label(f"<b>{label}:</b>  {value}",
                             f"color: {p.text}; font-size: 9pt;", center=True))

    gh_link = _label(
        f"<a href='{REPO_URL}' style='color:{p.accent};text-decoration:none;'>"
        f"github.com/{OWNER_REPO}</a>",
        "font-size: 8pt;", center=True)
    gh_link.setOpenExternalLinks(False)
    gh_link.setCursor(Qt.CursorShape.PointingHandCursor)
    gh_link.linkActivated.connect(lambda _u: QDesktopServices.openUrl(QUrl(REPO_URL)))
    lay.addWidget(gh_link)

    lay.addWidget(_label(t("about.note"), f"color: {p.history_text}; font-size: 8pt;",
                         center=True, wrap=True))

    # ── Güncelleme bölümü ──
    lay.addSpacing(6)
    sep = QLabel()
    sep.setFixedHeight(1)
    sep.setStyleSheet("background-color: rgba(128,128,128,0.2);")
    lay.addWidget(sep)
    lay.addSpacing(6)

    idle_css = f"color: {p.history_text}; font-size: 9pt;"
    update_status = _label(t("about.update.idle"), idle_css, center=True, wrap=True)
    lay.addWidget(update_status)

    btn_row = QHBoxLayout()
    check_btn = _make_button(p, t("about.update.btn"))
    btn_row.addWidget(check_btn)
    ok_btn = _make_button(p, t("about.ok"), primary=True)
    ok_btn.clicked.connect(dlg.accept)
    btn_row.addWidget(ok_btn)
    lay.addLayout(btn_row)

    checkers: list[UpdateChecker] = []

    def do_check() -> None:
        check_btn.setEnabled(False)
        check_btn.setText(t("about.update.checking.btn"))
        update_status.setText(t("about.update.checking"))
        update_status.setStyleSheet(idle_css)

        # parent = ana pencere: diyalog kapansa da iş güvenle tamamlanır.
        checker = UpdateChecker(parent)
        checkers.append(checker)

        def on_available(tag: str, url: str, digest: str) -> None:
            update_status.setText(t("about.update.available", tag=tag))
            update_status.setStyleSheet(f"color: {p.accent}; font-size: 9pt; font-weight: 600;")
            check_btn.setText(t("about.update.do"))
            check_btn.setEnabled(True)
            check_btn.setStyleSheet(dialog_button_style(p, primary=True))
            try:
                check_btn.clicked.disconnect()
            except TypeError:
                pass
            check_btn.clicked.connect(lambda: (dlg.accept(), on_update(tag, url, digest)))

        def on_up_to_date() -> None:
            update_status.setText(t("about.update.uptodate"))
            update_status.setStyleSheet(f"color: {p.text}; font-size: 9pt;")
            check_btn.setText(t("about.update.btn"))
            check_btn.setEnabled(True)

        def on_failed() -> None:
            update_status.setText(t("about.update.failed"))
            update_status.setStyleSheet("color: #FF3B30; font-size: 9pt;")
            check_btn.setText(t("about.update.retry"))
            check_btn.setEnabled(True)

        checker.update_available.connect(on_available)
        checker.up_to_date.connect(on_up_to_date)
        checker.check_failed.connect(on_failed)
        checker.start()

    check_btn.clicked.connect(do_check)
    dlg.exec()

    # Diyalog silinmeden önce, hâlâ sürebilecek kontrollerin bu diyaloğun
    # etiketlerine yazmasını engelle.
    for checker in checkers:
        for signal in (checker.update_available, checker.up_to_date, checker.check_failed):
            try:
                signal.disconnect()
            except TypeError:
                pass
        checker.deleteLater()
    dlg.deleteLater()


# ── Geri Bildirim ─────────────────────────────────────────────────────────────

def feedback_issue_url(category: str, body: str) -> str:
    """Seçilen kategori ve metinden GitHub 'yeni issue' adresini üretir."""
    if not body:
        body = t("feedback.empty_body")
    full_body = f"{body}\n\n---\n_Deep Calculator v{VERSION}_"
    label = {
        t("feedback.cat.suggest"): "enhancement",
        t("feedback.cat.bug"):     "bug",
        t("feedback.cat.general"): "question",
    }.get(category, "question")
    query = urllib.parse.urlencode(
        {"title": f"{category} — Deep Calculator", "body": full_body, "labels": label},
        quote_via=urllib.parse.quote,
    )
    return f"{REPO_URL}/issues/new?{query}"


def show_feedback(parent: QWidget, p: ThemePalette) -> None:
    dlg, lay = _make_dialog(parent, p, t("feedback.title"), 320, 280, (24, 20, 24, 20), 10)

    lay.addWidget(_label(t("feedback.heading"),
                         f"color: {p.text}; font-size: 12pt; font-weight: 700;"))
    lay.addWidget(_label(t("feedback.subtitle"),
                         f"color: {p.history_text}; font-size: 8pt;", wrap=True))

    category = QComboBox()
    category.addItems([t("feedback.cat.suggest"), t("feedback.cat.bug"), t("feedback.cat.general")])
    category.setStyleSheet(f"""
        QComboBox {{
            background-color: {p.btn_function}; color: {p.text};
            border: none; border-radius: 4px;
            padding: 6px 10px; font-size: 9pt;
        }}
        QComboBox::drop-down {{ border: none; width: 20px; }}
        QComboBox QAbstractItemView {{
            background-color: {p.surface}; color: {p.text};
            border: 1px solid rgba(128,128,128,0.2);
            selection-background-color: {p.accent};
        }}
    """)
    lay.addWidget(category)

    text_edit = QTextEdit()
    text_edit.setPlaceholderText(t("feedback.placeholder"))
    text_edit.setFixedHeight(90)
    text_edit.setStyleSheet(f"""
        QTextEdit {{
            background-color: {p.btn_function}; color: {p.text};
            border: none; border-radius: 4px;
            padding: 8px; font-size: 9pt;
        }}
    """)
    lay.addWidget(text_edit)

    btn_row = QHBoxLayout()
    cancel_btn = _make_button(p, t("feedback.cancel"))
    cancel_btn.clicked.connect(dlg.reject)
    send_btn = _make_button(p, t("feedback.send"), primary=True)

    def send() -> None:
        url = feedback_issue_url(category.currentText(), text_edit.toPlainText().strip())
        QDesktopServices.openUrl(QUrl(url))
        dlg.accept()

    send_btn.clicked.connect(send)
    btn_row.addWidget(cancel_btn)
    btn_row.addStretch()
    btn_row.addWidget(send_btn)
    lay.addLayout(btn_row)

    dlg.exec()
    dlg.deleteLater()


# ── Güncelleme ────────────────────────────────────────────────────────────────

def show_update_prompt(parent: QWidget, p: ThemePalette, new_version: str,
                       download_url: str, digest: str, on_update: UpdateCallback) -> None:
    """Yeni sürüm bildirim penceresi."""
    dlg, lay = _make_dialog(parent, p, t("update.title"), 320, 180, (24, 24, 24, 20), 12)

    lay.addWidget(_label(f"🔄  {t('update.title')}",
                         f"color: {p.text}; font-size: 12pt; font-weight: 700;"))
    lay.addWidget(_label(t("update.info", current=VERSION, new=new_version),
                         f"color: {p.history_text}; font-size: 9pt;", wrap=True))

    btn_row = QHBoxLayout()
    btn_row.addStretch()
    later_btn = _make_button(p, t("update.later"), padding=16)
    later_btn.clicked.connect(dlg.reject)
    update_btn = _make_button(p, t("update.do"), primary=True, padding=16)
    update_btn.clicked.connect(lambda: (dlg.accept(), on_update(new_version, download_url, digest)))
    btn_row.addWidget(later_btn)
    btn_row.addWidget(update_btn)
    lay.addLayout(btn_row)

    dlg.exec()
    dlg.deleteLater()


def run_download(parent: QWidget, p: ThemePalette, new_version: str,
                 download_url: str, digest: str = "") -> SetupDownloader | None:
    """
    Kurulum dosyasını indirir (ilerleme penceresiyle). Başarılıysa kurulumu
    başlatıp programı kapatır; başarısızsa sürüm sayfasını açar.
    URL yoksa (ör. Windows dışı sistem) doğrudan sürüm sayfası açılır.
    """
    if not download_url:
        open_releases_page()
        return None

    dlg, lay = _make_dialog(parent, p, t("update.downloading"), 300, 130, (24, 24, 24, 20), 12)
    dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

    lay.addWidget(_label(t("update.progress", version=new_version),
                         f"color: {p.text}; font-size: 10pt;"))

    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(0)
    bar.setStyleSheet(f"""
        QProgressBar {{
            background-color: {p.btn_function}; border-radius: 4px; height: 8px;
            text-align: center; color: transparent;
        }}
        QProgressBar::chunk {{ background-color: {p.accent}; border-radius: 4px; }}
    """)
    lay.addWidget(bar)

    downloader = SetupDownloader(download_url, digest, parent)
    downloader.progress.connect(bar.setValue)
    downloader.finished_ok.connect(lambda path: (dlg.accept(), launch_setup_and_quit(path)))
    downloader.failed.connect(lambda: (dlg.accept(), open_releases_page()))
    downloader.start()

    dlg.exec()
    dlg.deleteLater()
    return downloader
