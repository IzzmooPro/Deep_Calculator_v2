"""
CalculatorWindow — ana pencere.

Özellikler:
  - Bellek satırı: MC / MR / M+ / M- / MS
  - Hesap geçmişi paneli: ⏱ butonu ile açılır/kapanır
  - Hata-disable: hata sonrası operatör/fonksiyon butonları grileşir
  - M göstergesi: bellek doluyken display üzerinde küçük "M" etiketi
  - Tek-instance: WINDOW_TITLE sabiti üzerinden pencere bulunur
"""

from __future__ import annotations

from PyQt6.QtCore import QEvent, QPoint, QSettings, Qt, QTimer
from PyQt6.QtGui import (
    QAction, QColor, QFont, QIcon, QKeyEvent,
    QPainter, QPalette, QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QPushButton, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget,
)

from core import (
    OPS, KEY_MAP, FUNCTIONS,
    ThemeName, ORG, APP, DEFAULT_W, DEFAULT_H, CORNER_HIT, WINDOW_TITLE,
    CalculatorEngine, CalculatorState,
    format_display_expr,
)
from assets.icon_data import ICON_DARK, ICON_LIGHT
from ui.grid_layout import GRID
from ui.help_dialog import show_help
from ui.theme import THEMES, ThemePalette, btn_style, main_style
from ui.widgets import AnimatedButton

_DISABLE_ON_ERROR = OPS | frozenset({"%", "1/x", "x²", "2√x", "+/-"})


def _detect_system_theme() -> ThemeName:
    """Windows sistem temasını registry'den okur. Hata durumunda 'light' döner."""
    import sys
    if sys.platform != "win32":
        return "light"
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value else "dark"
    except Exception:
        return "light"


class CalculatorWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self._engine = CalculatorEngine()
        self._settings = QSettings(ORG, APP)
        self._buttons: dict[str, QPushButton] = {}
        self._mem_buttons: dict[str, QPushButton] = {}
        self._history_visible = False
        # Kullanıcı manuel tema seçmediyse her zaman Windows sistem temasını kullan.
        # "theme_user_set" bayrağı yalnızca kullanıcı ayarlar menüsünden tema
        # değiştirdiğinde True yapılır; aksi hâlde sistem teması önceliklidir.
        if self._settings.value("theme_user_set", False, type=bool):
            self._theme_name: ThemeName = self._settings.value("theme")  # type: ignore
        else:
            self._theme_name: ThemeName = _detect_system_theme()  # type: ignore
        self._opacity: float = self._settings.value("opacity", 1.0, type=float)

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(self._icon_for_theme(self._theme_name))
        self.resize(DEFAULT_W, DEFAULT_H)
        self.setMinimumSize(320, 500)

        self._build_ui()
        self._apply_theme()
        self.setWindowOpacity(self._opacity)
        QApplication.instance().installEventFilter(self)  # type: ignore

    # ── UI İnşa ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget(objectName="centralWidget")
        self.setCentralWidget(root)
        main_hbox = QHBoxLayout(root)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)

        calc_widget = QWidget()
        layout = QVBoxLayout(calc_widget)
        layout.setContentsMargins(8, 4, 8, 6)
        layout.setSpacing(2)

        display_panel = QWidget()
        display_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dp_hbox = QHBoxLayout(display_panel)
        dp_hbox.setContentsMargins(4, 0, 0, 0)
        dp_hbox.setSpacing(0)

        left_vbox = QVBoxLayout()
        left_vbox.setContentsMargins(0, 4, 0, 2)
        left_vbox.setSpacing(0)

        self._history_label = QLabel("")
        self._history_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._history_label.setFont(QFont("Segoe UI Variable Text", 9))
        left_vbox.addWidget(self._history_label)

        display_wrap = QWidget()
        dw_hbox = QHBoxLayout(display_wrap)
        dw_hbox.setContentsMargins(0, 0, 0, 0)
        dw_hbox.setSpacing(4)

        self._mem_indicator = QLabel("M")
        self._mem_indicator.setFixedWidth(16)
        self._mem_indicator.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._mem_indicator.setVisible(False)
        dw_hbox.addWidget(self._mem_indicator)

        self._display = QLineEdit("0")
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._display.setFont(QFont("Segoe UI Variable Display", 36, QFont.Weight.Light))
        self._display.setFixedHeight(52)
        self._display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._display.customContextMenuRequested.connect(self._show_display_menu)
        dw_hbox.addWidget(self._display, 1)
        left_vbox.addWidget(display_wrap)

        dp_hbox.addLayout(left_vbox, 1)

        btn_container = QWidget()
        btn_container.setFixedWidth(26)
        btn_vbox = QVBoxLayout(btn_container)
        btn_vbox.setContentsMargins(0, 4, 0, 4)
        btn_vbox.setSpacing(2)

        self._settings_btn = QToolButton()
        self._settings_btn.setText("\uE713")
        self._settings_btn.setFixedSize(22, 22)
        self._settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._settings_btn.setToolTip("Ayarlar")
        self._settings_btn.clicked.connect(self._show_settings_menu)
        btn_vbox.addWidget(self._settings_btn)

        btn_vbox.addStretch()
        dp_hbox.addWidget(btn_container, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(display_panel, 0)

        mem_row = QWidget()
        mem_hbox = QHBoxLayout(mem_row)
        mem_hbox.setContentsMargins(0, 0, 0, 2)
        mem_hbox.setSpacing(2)

        for label in ("MC", "MR", "M+", "M-", "MS"):
            b = QPushButton(label)
            b.setFont(QFont("Segoe UI Variable Text", 9))
            b.setFixedHeight(26)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.clicked.connect(self._on_button_clicked)
            mem_hbox.addWidget(b)
            self._mem_buttons[label] = b

        self._hist_btn = QPushButton("\uE81C")
        self._hist_btn.setFixedSize(26, 26)
        self._hist_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hist_btn.setToolTip("Geçmiş")
        self._hist_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._hist_btn.clicked.connect(self._toggle_history)
        mem_hbox.addWidget(self._hist_btn)

        layout.addWidget(mem_row)

        grid_widget = QWidget()
        grid_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 2, 0, 2)
        grid.setSpacing(2)
        for col in range(4):
            grid.setColumnStretch(col, 1)
        for row in range(6):
            grid.setRowStretch(row, 1)

        for label, row, col, rs, cs in GRID:
            b = AnimatedButton(label)
            b.setFont(QFont("Segoe UI Variable Text", 13))
            b.setMinimumSize(0, 0)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.clicked.connect(self._on_button_clicked)
            grid.addWidget(b, row, col, rs, cs)
            self._buttons[label] = b

        layout.addWidget(grid_widget, 1)
        main_hbox.addWidget(calc_widget, 1)

        self._history_flyout = QFrame(self)
        self._history_flyout.setVisible(False)
        fly_layout = QVBoxLayout(self._history_flyout)
        fly_layout.setContentsMargins(12, 12, 12, 12)
        fly_layout.setSpacing(6)

        fly_title_row = QHBoxLayout()
        fly_title = QLabel("Geçmiş")
        fly_title.setFont(QFont("Segoe UI Variable Text", 11, QFont.Weight.Bold))
        fly_title_row.addWidget(fly_title)
        fly_title_row.addStretch()

        self._clear_hist_btn = QPushButton("Temizle")
        self._clear_hist_btn.setFixedHeight(24)
        self._clear_hist_btn.setFont(QFont("Segoe UI Variable Text", 8))
        self._clear_hist_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_hist_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._clear_hist_btn.clicked.connect(self._clear_history)
        fly_title_row.addWidget(self._clear_hist_btn)
        fly_layout.addLayout(fly_title_row)

        self._history_list = QListWidget()
        self._history_list.setFont(QFont("Segoe UI Variable Text", 10))
        self._history_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._history_list.itemClicked.connect(self._on_history_item_clicked)
        fly_layout.addWidget(self._history_list, 1)

        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        self._fly_anim = QPropertyAnimation(self._history_flyout, b"pos")
        self._fly_anim.setDuration(220)
        self._fly_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── Geçmiş Flyout ─────────────────────────────────────────────────────────

    def _toggle_history(self) -> None:
        self._history_visible = not self._history_visible
        if self._history_visible:
            self._refresh_history_list()
            self._open_history_flyout()
        else:
            self._close_history_flyout()
        self._style_history_panel(THEMES[self._theme_name])

    def _open_history_flyout(self) -> None:
        cw = self.centralWidget()
        w = cw.width()
        h = cw.height()
        # centralWidget'ın QMainWindow içindeki konumu (title bar offseti dahil)
        offset = cw.mapToParent(QPoint(0, 0))
        ox, oy = offset.x(), offset.y()
        fly_h = int(h * 0.72)
        self._history_flyout.setFixedSize(w, fly_h)
        start_y = oy + h
        end_y   = oy + h - fly_h
        self._history_flyout.move(ox, start_y)
        self._history_flyout.setVisible(True)
        self._history_flyout.raise_()
        self._fly_anim.stop()
        self._fly_anim.setStartValue(QPoint(ox, start_y))
        self._fly_anim.setEndValue(QPoint(ox, end_y))
        self._fly_anim.start()
        self._refresh_history_list()

    def _close_history_flyout(self) -> None:
        cw = self.centralWidget()
        h = cw.height()
        fly_h = self._history_flyout.height()
        offset = cw.mapToParent(QPoint(0, 0))
        ox, oy = offset.x(), offset.y()
        self._fly_anim.stop()
        try:
            self._fly_anim.finished.disconnect(self._on_flyout_closed)
        except (RuntimeError, TypeError):
            pass
        self._fly_anim.setStartValue(QPoint(ox, oy + h - fly_h))
        self._fly_anim.setEndValue(QPoint(ox, oy + h))
        self._fly_anim.finished.connect(self._on_flyout_closed)
        self._fly_anim.start()

    def _on_flyout_closed(self) -> None:
        self._history_flyout.setVisible(False)
        try:
            self._fly_anim.finished.disconnect(self._on_flyout_closed)
        except (RuntimeError, TypeError):
            pass

    def _refresh_history_list(self) -> None:
        self._history_list.clear()
        log = self._engine.state.history_log
        if not log:
            placeholder = QListWidgetItem("Henüz hesaplama yapılmadı")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self._history_list.addItem(placeholder)
            return
        for entry in reversed(log):
            if " = " in entry:
                expr, result = entry.rsplit(" = ", 1)
                item = QListWidgetItem(f"{expr.strip()}  =  {result.strip()}")
                item.setData(Qt.ItemDataRole.UserRole, result.strip())
                self._history_list.addItem(item)

    def _on_history_item_clicked(self, item: QListWidgetItem) -> None:
        value = item.data(Qt.ItemDataRole.UserRole)
        if not value:
            return
        # Değeri al; dispatch zinciri item'ı yok edebilir.
        captured = str(value)
        self._history_visible = False
        self._close_history_flyout()
        self._dispatch("C")

        # Türkçe format: binlik=nokta, ondalık=virgül
        # Önce binlik noktaları kaldır, ardından virgülü nokta yap → float parse.
        # Sonra format_display_expr ile yeniden Türkçe gösterime çevir.
        is_negative = captured.startswith("-")
        raw = captured.lstrip("-")
        # Binlik nokta kaldır, ondalık virgülü geçici olarak işaretle
        normalized = raw.replace(".", "").replace(",", ".")
        try:
            num = float(normalized)
        except ValueError:
            return
        # Tamsayı mı yoksa ondalıklı mı kontrol et
        from core.formatter import format_number as _fmt
        formatted = _fmt(num)
        # Karakterleri tek tek dispatch et (Türkçe formatta)
        for ch in formatted:
            if ch.isdigit():
                self._dispatch(ch)
            elif ch == ",":
                self._dispatch(",")
            # binlik noktaları atla — engine kendi ekler
        if is_negative:
            self._dispatch("+/-")

    def _clear_history(self) -> None:
        self._engine.state.history_log.clear()
        QTimer.singleShot(0, self._history_list.clear)

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _set_opacity(self, val: float) -> None:
        self._opacity = val
        self._settings.setValue("opacity", val)
        self.setWindowOpacity(val)

    def _set_theme(self, name: ThemeName) -> None:
        self._theme_name = name
        self._settings.setValue("theme", name)
        self._settings.setValue("theme_user_set", True)  # kullanıcı manuel seçti
        self._apply_theme()

    def _apply_theme(self) -> None:
        p = THEMES[self._theme_name]

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window,          QColor(p.bg))
        palette.setColor(QPalette.ColorRole.WindowText,      QColor(p.text))
        palette.setColor(QPalette.ColorRole.Base,            QColor(p.display_bg))
        palette.setColor(QPalette.ColorRole.Text,            QColor(p.text))
        palette.setColor(QPalette.ColorRole.Button,          QColor(p.surface))
        palette.setColor(QPalette.ColorRole.ButtonText,      QColor(p.text))
        palette.setColor(QPalette.ColorRole.Highlight,       QColor(p.accent))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        QApplication.instance().setPalette(palette)  # type: ignore

        self.setStyleSheet(main_style(p))
        self._display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {p.display_bg}; color: {p.text};
                border: none; border-radius: 4px;
                padding-right: 8px; padding-left: 8px;
            }}
        """)
        self._history_label.setStyleSheet(f"color: {p.history_text}; padding-right: 6px;")
        self._mem_indicator.setStyleSheet(f"color: {p.accent}; font-size: 8pt; font-weight: bold;")

        _tb_css = f"""
            QToolButton {{
                background: transparent; border: none;
                border-radius: 4px; padding: 2px;
                color: {p.history_text};
                font-family: 'Segoe MDL2 Assets'; font-size: 11pt;
            }}
            QToolButton:hover   {{ background: rgba(128,128,128,0.12); color: {p.text}; }}
            QToolButton:pressed {{ background: rgba(128,128,128,0.22); }}
        """
        self._settings_btn.setStyleSheet(_tb_css)

        _mem_css = f"""
            QPushButton {{
                background-color: transparent; color: {p.text};
                border: none; border-radius: 4px; font-size: 9pt;
            }}
            QPushButton:hover   {{ background-color: rgba(128,128,128,0.12); }}
            QPushButton:pressed {{ background-color: rgba(128,128,128,0.22); }}
        """
        for b in self._mem_buttons.values():
            b.setStyleSheet(_mem_css)
        self._hist_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {p.text};
                border: none; border-radius: 4px;
                font-family: 'Segoe MDL2 Assets'; font-size: 13pt;
            }}
            QPushButton:hover   {{ background-color: rgba(128,128,128,0.12); }}
            QPushButton:pressed {{ background-color: rgba(128,128,128,0.22); }}
        """)

        for label, b in self._buttons.items():
            self._style_button(b, label, p)

        self._style_history_panel(p)
        self.setWindowIcon(self._icon_for_theme(self._theme_name))

        # Bellek buton durumlarını tema değişiminde de senkronize et
        mem_active = self._engine.state.memory_active
        for label in ("MC", "MR"):
            b = self._mem_buttons.get(label)
            if b:
                b.setEnabled(mem_active)

    def _style_history_panel(self, p: ThemePalette) -> None:
        self._history_flyout.setStyleSheet(f"""
            QFrame {{
                background-color: {p.surface};
                border-top: 1px solid rgba(128,128,128,0.2);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QLabel {{ color: {p.text}; background: transparent; border: none; }}
            QListWidget {{
                background-color: {p.surface}; border: none; color: {p.text};
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid rgba(128,128,128,0.1);
            }}
            QListWidget::item:selected {{ background-color: {p.accent}; color: #FFF; }}
            QListWidget::item:hover    {{ background-color: rgba(128,128,128,0.1); }}
            QListWidget::item:disabled {{ color: {p.history_text}; }}
        """)
        self._clear_hist_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {p.history_text};
                border: none; border-radius: 4px; padding: 2px 8px; font-size: 8pt;
            }}
            QPushButton:hover {{ background: rgba(128,128,128,0.12); color: {p.text}; }}
        """)

    def _style_button(self, b: QPushButton, label: str, p: ThemePalette) -> None:
        if label == "=":
            style = btn_style(p.btn_equals, p.btn_equals_hover, p.btn_equals_text,
                              fs=20, bold=True, radius=4)
        elif label in OPS:
            style = btn_style(p.btn_operator, p.btn_operator_hover, "#FFFFFF",
                              fs=15, bold=True, radius=4)
        elif label == "+/-":
            # 0 butonu ile aynı numeric stil — açık/koyu temaya tam uyumlu
            style = btn_style(p.btn_numeric, p.btn_numeric_hover, p.text,
                              fs=14, radius=4)
        elif label in FUNCTIONS:
            style = btn_style(p.btn_function, p.btn_function_hover, p.text,
                              fs=12, radius=4)
        else:
            style = btn_style(p.btn_numeric, p.btn_numeric_hover, p.text,
                              fs=14, radius=4)
        b.setStyleSheet(style)

    # ── Olay İşleyiciler ──────────────────────────────────────────────────────

    def _on_button_clicked(self) -> None:
        sender = self.sender()
        if isinstance(sender, QPushButton):
            self._dispatch(sender.text())

    def eventFilter(self, obj, event) -> bool:  # type: ignore
        if event.type() == QEvent.Type.KeyPress:
            if self.isActiveWindow():
                self._handle_key(event)
                return True
        return False

    def _handle_key(self, event: QKeyEvent) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                self._copy_result(); return
            if event.key() == Qt.Key.Key_V:
                self._paste_from_clipboard(); return
        if event.key() == Qt.Key.Key_Escape:
            if self._history_visible:
                self._history_visible = False
                self._close_history_flyout()
                return
        if event.key() == Qt.Key.Key_H:
            self._show_help(); return
        token = KEY_MAP.get(event.key())
        if token:
            self._dispatch(token)

    # ── İkon Çizimi ───────────────────────────────────────────────────────────

    @staticmethod
    def _icon_for_theme(theme_name: str) -> QIcon:
        import base64
        raw = base64.b64decode(ICON_DARK if theme_name == "dark" else ICON_LIGHT)
        pix = QPixmap()
        pix.loadFromData(raw)
        return QIcon(pix)

    def _draw_icon(self, kind: str, active: bool) -> QIcon:
        p = THEMES[self._theme_name]
        color = QColor(p.accent) if active else QColor(p.text)
        color.setAlphaF(0.6 if not active else 1.0)
        size = 18
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(pix)
        ptr.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = ptr.pen()
        pen.setColor(color)
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        ptr.setPen(pen)
        ptr.setBrush(Qt.BrushStyle.NoBrush)
        if kind == "check":
            ptr.drawLine(2, 9, 7, 14); ptr.drawLine(7, 14, 16, 4)
        elif kind == "copy":
            ptr.drawRoundedRect(6, 2, 10, 11, 2, 2)
            ptr.setPen(Qt.PenStyle.NoPen); ptr.setBrush(QColor(p.display_bg))
            ptr.drawRoundedRect(2, 6, 10, 11, 2, 2)
            ptr.setPen(pen); ptr.setBrush(Qt.BrushStyle.NoBrush)
            ptr.drawRoundedRect(2, 6, 10, 11, 2, 2)
        elif kind == "paste":
            ptr.drawRoundedRect(2, 5, 13, 12, 2, 2)
            ptr.setPen(Qt.PenStyle.NoPen); ptr.setBrush(QColor(p.display_bg))
            ptr.drawRect(6, 2, 6, 5)
            ptr.setPen(pen); ptr.setBrush(Qt.BrushStyle.NoBrush)
            ptr.drawRoundedRect(6, 1, 6, 5, 1, 1)
            ptr.drawLine(5, 10, 13, 10); ptr.drawLine(5, 13, 13, 13)
        ptr.end()
        return QIcon(pix)

    # ── Kopyala / Yapıştır ────────────────────────────────────────────────────

    def _copy_result(self) -> None:
        QApplication.clipboard().setText(self._display.text())

    def _paste_from_clipboard(self) -> None:
        text = QApplication.clipboard().text().strip()
        if not text: return
        is_negative = text.startswith("-")
        digits_part = text.lstrip("-+").strip()
        if not digits_part: return
        self._dispatch("C")
        for ch in digits_part:
            if ch.isdigit(): self._dispatch(ch)
            elif ch in (",", "."): self._dispatch(",")
        if is_negative: self._dispatch("+/-")
        self.setFocus(); self.activateWindow()

    # ── Dispatch & Render ─────────────────────────────────────────────────────

    def _dispatch(self, token: str) -> None:
        self._render(self._engine.press(token))

    def _render(self, state: CalculatorState) -> None:
        p = THEMES[self._theme_name]
        base_css = f"""
            QLineEdit {{
                background-color: {p.display_bg}; color: {p.text};
                border: none; border-radius: 4px;
                padding-right: 8px; padding-left: 8px;
            }}
        """
        if state.error:
            self._display.setText(state.error)
            self._display.setStyleSheet(base_css + "QLineEdit { color: #FF3B30; }")
        else:
            text = format_display_expr(state.expression or "0")
            self._display.setText(text)
            self._display.setStyleSheet(base_css)
            fs = 36 if len(text) <= 9 else (26 if len(text) <= 14 else 18)
            self._display.setFont(QFont("Segoe UI Variable Display", fs, QFont.Weight.Light))

        self._history_label.setText(state.history)
        self._mem_indicator.setVisible(state.memory_active)

        for label, b in self._buttons.items():
            if label in _DISABLE_ON_ERROR:
                b.setEnabled(not state.buttons_disabled)

        # MC ve MR: bellek doluysa aktif
        for label in ("MC", "MR"):
            b = self._mem_buttons.get(label)
            if b:
                b.setEnabled(state.memory_active)

        # MS, M+, M-: her zaman aktif (bellek boş da olsa değer yazılabilir)
        for label in ("MS", "M+", "M-"):
            b = self._mem_buttons.get(label)
            if b:
                b.setEnabled(True)

        if self._history_visible:
            self._refresh_history_list()

    # ── Bağlam Menüsü ─────────────────────────────────────────────────────────

    def _show_display_menu(self, pos: QPoint) -> None:
        p = THEMES[self._theme_name]
        menu = QMenu(self._display)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {p.surface}; color: {p.text};
                border: 1px solid rgba(128,128,128,0.25); border-radius: 8px; padding: 4px;
            }}
            QMenu::item {{ padding: 7px 22px 7px 10px; border-radius: 4px; }}
            QMenu::item:selected {{ background-color: {p.accent}; color: #FFF; }}
            QMenu::separator {{ height: 1px; background: rgba(128,128,128,0.2); margin: 3px 6px; }}
        """)
        copy_act = QAction("  Kopyala", self)
        copy_act.setIcon(self._draw_icon("copy", False))
        copy_act.triggered.connect(self._copy_result)
        menu.addAction(copy_act)
        paste_act = QAction("  Yapıştır", self)
        paste_act.setIcon(self._draw_icon("paste", False))
        paste_act.triggered.connect(self._paste_from_clipboard)
        paste_act.setEnabled(bool(QApplication.clipboard().text().strip()))
        menu.addAction(paste_act)
        menu.addSeparator()
        sel_act = QAction("  Tümünü Seç", self)
        sel_act.triggered.connect(self._display.selectAll)
        menu.addAction(sel_act)
        menu.exec(self._display.mapToGlobal(pos))

    # ── Ayarlar Menüsü ────────────────────────────────────────────────────────

    def _show_settings_menu(self) -> None:
        p = THEMES[self._theme_name]
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {p.surface}; color: {p.text};
                border: 1px solid rgba(128,128,128,0.25);
                border-radius: 10px; padding: 4px;
            }}
            QMenu::item {{ padding: 7px 24px 7px 12px; border-radius: 6px; font-size: 9pt; }}
            QMenu::item:selected {{ background-color: {p.accent}; color: #FFF; }}
            QMenu::separator {{ height: 1px; background: rgba(128,128,128,0.2); margin: 4px 8px; }}
        """)
        theme_menu = menu.addMenu("Tema")
        light_action = QAction("Açık",  self, checkable=True)
        dark_action  = QAction("Koyu", self, checkable=True)
        light_action.setChecked(self._theme_name == "light")
        dark_action.setChecked(self._theme_name == "dark")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        dark_action.triggered.connect(lambda:  self._set_theme("dark"))
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        opacity_menu = menu.addMenu("Şeffaflık")
        for label, val in [("Tam opak", 1.0), ("Hafif şeffaf", 0.92), ("Yarı şeffaf", 0.80)]:
            act = QAction(label, self, checkable=True)
            act.setData(val)
            act.setChecked(abs(val - self._opacity) < 0.01)
            act.triggered.connect(lambda checked, v=val: self._set_opacity(v))
            opacity_menu.addAction(act)

        menu.addSeparator()
        help_act = QAction("Kullanım Kılavuzu", self)
        help_act.triggered.connect(self._show_help)
        menu.addAction(help_act)
        about_act = QAction("Hakkında", self)
        about_act.triggered.connect(self._show_about)
        menu.addAction(about_act)

        pos = self._settings_btn.mapToGlobal(self._settings_btn.rect().bottomRight())
        menu.exec(pos)

    # ── Yardım & Hakkında ─────────────────────────────────────────────────────

    def _show_help(self) -> None:
        show_help(self, THEMES[self._theme_name])

    def _show_about(self) -> None:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        p = THEMES[self._theme_name]
        dlg = QDialog(self)
        dlg.setWindowTitle("Hakkında")
        dlg.setFixedSize(300, 280)
        dlg.setStyleSheet(f"QDialog {{ background-color: {p.bg}; }}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 24, 24, 20)
        lay.setSpacing(10)
        title = QLabel("🧮  Deep Calculator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {p.text}; font-size: 14pt; font-weight: 700;")
        lay.addWidget(title)
        version = QLabel("Sürüm 2.0.0  •  2026")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {p.history_text}; font-size: 9pt;")
        lay.addWidget(version)
        lay.addSpacing(8)
        for label, value in [
            ("Geliştirici", "Izzmoo"),
            ("İletişim",    "IzzmooPro@gmail.com"),
            ("Lisans",      "Ücretsiz — kişisel ve ticari"),
        ]:
            row = QLabel(f"<b>{label}:</b>  {value}")
            row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.setStyleSheet(f"color: {p.text}; font-size: 9pt;")
            lay.addWidget(row)

        gh_url = "https://github.com/IzzmooPro/Deep_Calculator_v2"
        gh_link = QLabel(f"<a href='{gh_url}' style='color:{p.accent};text-decoration:none;'>github.com/IzzmooPro/Deep_Calculator_v2</a>")
        gh_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gh_link.setStyleSheet("font-size: 8pt;")
        gh_link.setOpenExternalLinks(False)
        gh_link.setCursor(Qt.CursorShape.PointingHandCursor)
        gh_link.linkActivated.connect(lambda _u=gh_url: QDesktopServices.openUrl(QUrl(_u)))
        lay.addWidget(gh_link)
        lay.addSpacing(4)
        note = QLabel("Kaynak kodu değiştirilemez ve satılamaz.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {p.history_text}; font-size: 8pt;")
        lay.addWidget(note)
        lay.addStretch()
        ok_btn = QPushButton("Tamam")
        ok_btn.setFixedHeight(36)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(dlg.accept)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {p.accent}; color: #FFF;
                border: none; border-radius: 4px;
                font-size: 10pt; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {p.btn_operator_hover}; }}
        """)
        lay.addWidget(ok_btn)
        dlg.exec()

    # ── Pencere Olayları ──────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:  # type: ignore
        super().resizeEvent(event)
        if self._history_visible and self._history_flyout.isVisible():
            cw = self.centralWidget()
            w = cw.width()
            h = cw.height()
            offset = cw.mapToParent(QPoint(0, 0))
            ox, oy = offset.x(), offset.y()
            fly_h = int(h * 0.72)
            self._history_flyout.setFixedSize(w, fly_h)
            self._history_flyout.move(ox, oy + h - fly_h)

    def mousePressEvent(self, event) -> None:  # type: ignore
        if self._history_visible and self._history_flyout.isVisible():
            fly_rect = self._history_flyout.geometry()
            if not fly_rect.contains(event.pos()):
                self._history_visible = False
                self._close_history_flyout()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # type: ignore
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            w, h = self.width(), self.height()
            if any([
                pos.x() < CORNER_HIT and pos.y() < CORNER_HIT,
                pos.x() > w - CORNER_HIT and pos.y() < CORNER_HIT,
                pos.x() < CORNER_HIT and pos.y() > h - CORNER_HIT,
                pos.x() > w - CORNER_HIT and pos.y() > h - CORNER_HIT,
            ]):
                self.resize(DEFAULT_W, DEFAULT_H)
                return
        super().mouseDoubleClickEvent(event)