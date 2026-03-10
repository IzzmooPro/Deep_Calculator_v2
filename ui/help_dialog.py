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


def show_help(parent, palette: ThemePalette) -> None:
    """Kullanım kılavuzu diyalogunu göster."""
    p = palette

    dlg = QDialog(parent)
    dlg.setWindowTitle("Kullanım Kılavuzu")
    dlg.setFixedSize(380, 520)
    dlg.setStyleSheet(f"""
        QDialog {{ background-color: {p.bg}; }}
        QScrollArea {{ border: none; background: transparent; }}
        QWidget#scrollContent {{ background: transparent; }}
    """)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    header = QLabel("  🧮  Kullanım Kılavuzu")
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

        t = QLabel(f"{icon}  {title}")
        t.setStyleSheet(f"""
            color: {p.accent}; font-size: 8.5pt; font-weight: 700;
            letter-spacing: 0.8px; padding-bottom: 8px;
        """)
        cl.addWidget(t)

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

    vbox.addWidget(make_card("⌨️", "Klavye Kısayolları", [
        ("0 – 9",           "Rakam girişi"),
        ("+ / - / * / /",   "Dört işlem operatörleri"),
        ("Enter  veya  =",  "Hesapla"),
        ("Backspace",       "Son karakteri sil"),
        ("Esc",             "Her şeyi temizle (C)"),
        ("Delete",          "Son operandı sil (CE)"),
        (",  veya  .",      "Ondalık virgül gir"),
        ("%",               "Yüzde"),
        ("F9",              "İşaret değiştir (+/-)"),   # Düzeltme #6
        ("Ctrl + C",        "Sonucu panoya kopyala"),
        ("Ctrl + V",        "Panodan sayı yapıştır"),
        ("H",               "Bu kılavuzu aç"),
    ]))
    vbox.addWidget(make_card("🔢", "Buton Referansı", [
        ("CE",   "Son operandı sil, operatörü koru"),
        ("C",    "Her şeyi sıfırla"),
        ("⌫",   "Son karakteri sil"),
        ("+/-",  "İşaret değiştir (±)"),
        ("%",    "Yüzdeye çevir (÷ 100)"),
        ("1/x",  "Tersini al (1 ÷ x)"),
        ("x²",   "Karesini al"),
        ("2√x",  "Karekök al"),
    ]))
    vbox.addWidget(make_card("⛓️", "Zincir İşlemler", [
        ("5 + 2 + 3 =",   "Ara sonuç gösterir → 10 → 13"),
        ("= (tekrar)",     "Son işlemi tekrarlar: 8+3=11 → =→14"),
        ("History satırı", "Tam ifadeyi gösterir: 5+2+3 ="),
    ]))
    vbox.addWidget(make_card("📋", "Kopyala & Yapıştır", [
        ("Display sağ tık", "Kopyala / Yapıştır / Tümünü Seç"),
        ("Ctrl + C",        "Sonucu panoya kopyala"),
        ("Ctrl + V",        "Panodan sayı yapıştır"),
    ]))
    vbox.addWidget(make_card("🎨", "Görünüm & Pencere", [
        ("Ayarlar → Tema",       "Açık / Koyu tema (kaydedilir)"),
        ("Ayarlar → Şeffaflık",  "Pencere opaklığı — 3 seviye"),
        ("Köşeye çift tık",      "Varsayılan boyuta sıfırla"),
    ]))
    vbox.addStretch()

    close_btn = QPushButton("Tamam")
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
