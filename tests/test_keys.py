import pytest
from PyQt6.QtCore import Qt

from core.constants import key_to_token

K = Qt.Key


@pytest.mark.parametrize("key, text, expected", [
    # Türkçe Q klavye: tuş kodu yanlış gelse bile karakter esas alınır
    (K.Key_5, "%", "%"),          # Shift+5
    (K.Key_7, "/", "÷"),          # Shift+7
    (K.Key_4, "+", "+"),          # Shift+4
    (K.Key_Asterisk, "*", "×"),
    (K.Key_Minus, "-", "−"),
    (K.Key_Period, ".", ","),
    (K.Key_Comma, ",", ","),
    (K.Key_7, "7", "7"),
    (K.Key_0, "=", "="),          # Shift+0 (Türkçe Q)
    # Karakter üretmeyen tuşlar tuş kodundan okunur
    (K.Key_Return, "\r", "="),
    (K.Key_Enter, "\r", "="),
    (K.Key_Backspace, "\x08", "⌫"),
    (K.Key_Escape, "\x1b", "C"),
    (K.Key_Delete, "\x7f", "CE"),
    (K.Key_F9, "", "+/-"),
    (K.Key_Percent, "", "%"),
    (K.Key_A, "a", None),
])
def test_key_to_token(key, text, expected):
    assert key_to_token(key, text) == expected
