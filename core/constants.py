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
VERSION    = "2.0.0"

DEFAULT_W  = 320
DEFAULT_H  = 500
CORNER_HIT = 24

# Tek-instance kontrolünde pencereyi bulmak için kullanılan başlık sabiti.
# window.py'deki setWindowTitle() ile buradaki değer her zaman eşleşmelidir.
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

# ── AST Güvenli Node Tipleri ──────────────────────────────────────────────────

ALLOWED_NODES: tuple[type, ...] = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
)
