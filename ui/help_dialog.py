"""
Kullanım Kılavuzu Diyaloğu.

Düzeltme #10: window.py'dan ayrıştırıldı; window.py artık çok daha sade.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from ui.theme import ThemePalette
from core.i18n import t


def show_help(parent, palette: ThemePalette) -> None:
    """Kullanım kılavuzu diyalogunu göster."""
    p = palette

    dlg = QDialog(parent)
    dlg.setWindowTitle(t("help.title"))
    dlg.setFixedSize(380, 520)
    dlg.setStyleSheet(f"""
        QDialog {{ background-color: {p.bg}; }}
        QScrollArea {{ border: none; background: transparent; }}
        QWidget#scrollContent {{ background: transparent; }}
    """)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    header = QLabel(t("help.header"))
    header.setFixedHeight(56)
    header.setStyleSheet(f"""
        QLabel {{
            background-color: {p.surface}; color: {p.text};
            font-size: 12pt; font-weight: 600;
            border-bottom: 1px solid rgba(128,128,128,0.15);
            padding-left: 8px;
        }}
    """)
    outer.addWidget(header)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_content = QWidget(objectName="scrollContent")
    scroll.setWidget(scroll_content)
    vbox = QVBoxLayout(scroll_content)
    vbox.setContentsMargins(16, 14, 16, 14)
    vbox.setSpacing(10)
    outer.addWidget(scroll, 1)

    card_style = f"""
        QFrame {{
            background-color: {p.surface};
            border-radius: 10px;
            border: 1px solid rgba(128,128,128,0.12);
        }}
    """

    def make_card(icon: str, title: str, rows: list[tuple]) -> QFrame:
        card = QFrame()
        card.setStyleSheet(card_style)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 10, 14, 12)
        cl.setSpacing(0)

        t_lbl = QLabel(f"{icon}  {title}")
        t_lbl.setStyleSheet(f"""
            color: {p.accent}; font-size: 8.5pt; font-weight: 700;
            letter-spacing: 0.8px; padding-bottom: 8px;
        """)
        cl.addWidget(t_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            "border: none; border-top: 1px solid rgba(128,128,128,0.15); margin-bottom: 8px;"
        )
        cl.addWidget(sep)

        for key, desc in rows:
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent; border: none;")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(8)

            key_lbl = QLabel(key)
            key_lbl.setFixedWidth(130)
            key_lbl.setStyleSheet(f"""
                background-color: rgba(128,128,128,0.1);
                color: {p.text}; font-size: 8.5pt; font-weight: 600;
                border-radius: 4px; padding: 3px 7px;
                font-family: 'Consolas', 'Courier New', monospace;
            """)
            key_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {p.text}; font-size: 8.5pt; background: transparent; border: none;"
            )

            rl.addWidget(key_lbl)
            rl.addWidget(desc_lbl, 1)
            cl.addWidget(row_w)

        return card

    vbox.addWidget(make_card("⌨️", t("help.kbd.title"), [
        ("0 – 9",          t("help.kbd.digits")),
        ("+ / - / * / /",  t("help.kbd.ops")),
        ("Enter  /  =",    t("help.kbd.enter")),
        ("Backspace",      t("help.kbd.backspace")),
        ("Esc",            t("help.kbd.esc")),
        ("Delete",         t("help.kbd.delete")),
        (",  /  .",        t("help.kbd.decimal")),
        ("%",              t("help.kbd.percent")),
        ("F9",             t("help.kbd.sign")),
        ("Ctrl + C",       t("help.kbd.copy")),
        ("Ctrl + V",       t("help.kbd.paste")),
        ("H",              t("help.kbd.help")),
    ]))
    vbox.addWidget(make_card("🔢", t("help.btn.title"), [
        ("CE",   t("help.btn.ce")),
        ("C",    t("help.btn.c")),
        ("⌫",   t("help.btn.back")),
        ("+/-",  t("help.btn.sign")),
        ("%",    t("help.btn.percent")),
        ("1/x",  t("help.btn.inv")),
        ("x²",   t("help.btn.sq")),
        ("2√x",  t("help.btn.sqrt")),
    ]))
    vbox.addWidget(make_card("⛓️", t("help.chain.title"), [
        ("5 + 2 + 3 =",  t("help.chain.1")),
        ("= (x2)",        t("help.chain.2")),
        ("History",       t("help.chain.3")),
    ]))
    vbox.addWidget(make_card("📋", t("help.clip.title"), [
        ("Display →",    t("help.clip.1")),
        ("Ctrl + C",     t("help.clip.2")),
        ("Ctrl + V",     t("help.clip.3")),
    ]))
    vbox.addWidget(make_card("🎨", t("help.view.title"), [
        (f"{t('settings.theme')} →",    t("help.view.1")),
        (f"{t('settings.opacity')} →",  t("help.view.2")),
        ("2x Click →",                  t("help.view.3")),
    ]))
    vbox.addStretch()

    close_btn = QPushButton(t("help.close"))
    close_btn.setFixedHeight(40)
    close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    close_btn.clicked.connect(dlg.accept)
    close_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {p.accent}; color: #FFF;
            border: none; font-size: 10pt; font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {p.btn_operator_hover}; }}
    """)
    outer.addWidget(close_btn)
    dlg.exec()
