"""
Hesap makinesi butonu — QPushButton subclass'ı.
İleride animasyon veya özel davranış eklemek için hazır taban sınıf.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    """
    Hesap makinesi butonları için taban sınıf.
    Şu an ek davranış içermez; QPushButton'ı doğrudan genişletir.
    İleride tıklama animasyonu, ripple efekti vb. buraya eklenebilir.
    """

    def __init__(self, label: str, parent=None) -> None:
        super().__init__(label, parent)
