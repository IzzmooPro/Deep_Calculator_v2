"""
Sabitler ve klavye haritası.
"""

from __future__ import annotations

import ast
from typing import Literal

from PyQt6.QtCore import Qt

# ── Uygulama Sabitleri ────────────────────────────────────────────────────────

ORG        = "DeepCalc"
APP        = "Calculator"
VERSION    = "2.0.1"

DEFAULT_W  = 320
DEFAULT_H  = 500
CORNER_HIT = 24

# Varsayılan (Türkçe) pencere başlığı. Asıl başlık seçili dile göre
# t("app.title") ile belirlenir; tek-instance kontrolü başlığa bağlı değildir.
WINDOW_TITLE = "Hesap Makinesi"

# ── Tip Takma Adları ──────────────────────────────────────────────────────────

ThemeName = Literal["light", "dark"]

# ── Operatör & Fonksiyon Setleri ──────────────────────────────────────────────

OPS: frozenset[str] = frozenset({"+", "−", "×", "÷"})

# Public — engine ve UI katmanları bu seti doğrudan kullanabilir.
FUNCTIONS: frozenset[str] = frozenset({"1/x", "x²", "2√x", "%", "⌫", "CE", "C", "+/-"})

# ── Klavye → Token Haritası ───────────────────────────────────────────────────

KEY_MAP: dict[int, str] = {
    Qt.Key.Key_0: "0",         Qt.Key.Key_1: "1",
    Qt.Key.Key_2: "2",         Qt.Key.Key_3: "3",
    Qt.Key.Key_4: "4",         Qt.Key.Key_5: "5",
    Qt.Key.Key_6: "6",         Qt.Key.Key_7: "7",
    Qt.Key.Key_8: "8",         Qt.Key.Key_9: "9",
    Qt.Key.Key_Plus: "+",      Qt.Key.Key_Minus: "−",
    Qt.Key.Key_Asterisk: "×",  Qt.Key.Key_Slash: "÷",
    Qt.Key.Key_Comma: ",",     Qt.Key.Key_Period: ",",
    Qt.Key.Key_Return: "=",    Qt.Key.Key_Enter: "=",
    Qt.Key.Key_Backspace: "⌫", Qt.Key.Key_Escape: "C",
    Qt.Key.Key_Delete: "CE",   Qt.Key.Key_Percent: "%",
    Qt.Key.Key_F9: "+/-",
}

# Klavyenin ürettiği karakter → token. Klavye düzeninden bağımsızdır:
# Türkçe Q klavyede "%" Shift+5, "/" Shift+7, "+" Shift+4 ile yazılır; bu
# durumlarda tuş kodu her platformda güvenilir değildir, karakter ise doğrudur.
KEY_TEXT_MAP: dict[str, str] = {
    "+": "+", "-": "−", "−": "−",
    "*": "×", "×": "×",
    "/": "÷", "÷": "÷",
    "%": "%",
    ",": ",", ".": ",",
    "=": "=",
}


def key_to_token(key: int, text: str) -> str | None:
    """Klavye olayını token'a çevirir: önce üretilen karaktere, sonra tuş koduna bakar."""
    if len(text) == 1:
        if text.isdigit():
            return text
        if text in KEY_TEXT_MAP:
            return KEY_TEXT_MAP[text]
    return KEY_MAP.get(key)

# ── AST Güvenli Node Tipleri ──────────────────────────────────────────────────

ALLOWED_NODES: tuple[type, ...] = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
)
