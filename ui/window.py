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
from core.formatter import parse_number, parse_pasted_number
from assets.icon_data import ICON_DARK, ICON_LIGHT
from ui.grid_layout import GRID
from ui.help_dialog import show_help
from ui.dialogs import run_download, show_about, show_feedback, show_update_prompt
from ui.theme import (
    THEMES, ThemePalette, btn_style, flat_button_style, main_style, menu_style,
)
from ui.widgets import AnimatedButton
from core.updater import SetupDownloader, UpdateChecker
from core.i18n import t, set_language, get_language, SUPPORTED_LANGUAGES

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

        # Kayıtlı dili yükle
        saved_lang = self._settings.value("language", "tr", type=str)
        set_language(saved_lang)

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(self._icon_for_theme(self._theme_name))
        self.resize(DEFAULT_W, DEFAULT_H)
        self.setMinimumSize(320, 500)

        self._build_ui()
        self._apply_theme()
        self.setWindowOpacity(self._opacity)
        QApplication.instance().installEventFilter(self)  # type: ignore

        # Arka planda güncelleme kontrolü
        self._update_checker: UpdateChecker | None = None
        self._downloader: SetupDownloader | None = None
        QTimer.singleShot(3000, self._auto_check_update)

        # Sonuç animasyonu için son token takibi
        self._last_token: str = ""

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
        self._settings_btn.setToolTip(t("tooltip.settings"))
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
        self._hist_btn.setToolTip(t("tooltip.history"))
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
        self._fly_title = QLabel(t("history.title"))
        self._fly_title.setFont(QFont("Segoe UI Variable Text", 11, QFont.Weight.Bold))
        fly_title_row.addWidget(self._fly_title)
        fly_title_row.addStretch()

        self._clear_hist_btn = QPushButton(t("history.clear"))
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
            placeholder = QListWidgetItem(t("history.empty"))
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
        try:
            num = parse_number(captured)  # geçmişteki değer uygulamanın kendi formatında
        except ValueError:
            return
        self._load_value(num)

    def _clear_history(self) -> None:
        self._engine.state.history_log.clear()
        QTimer.singleShot(0, self._history_list.clear)

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _set_language(self, lang: str) -> None:
        set_language(lang)
        self._settings.setValue("language", lang)
        self._settings_btn.setToolTip(t("tooltip.settings"))
        self._hist_btn.setToolTip(t("tooltip.history"))
        self._fly_title.setText(t("history.title"))
        self._clear_hist_btn.setText(t("history.clear"))
        self._refresh_history_list()

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

        _mem_css = flat_button_style(p, "font-size: 9pt;")
        for b in self._mem_buttons.values():
            b.setStyleSheet(_mem_css)
        self._hist_btn.setStyleSheet(
            flat_button_style(p, "font-family: 'Segoe MDL2 Assets'; font-size: 13pt;"))

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
        try:
            num = parse_pasted_number(text)
        except ValueError:
            return  # sayı olmayan metin yok sayılır
        self._load_value(num)
        self.setFocus(); self.activateWindow()

    def _load_value(self, value: float) -> None:
        """Yapıştırılan / geçmişten seçilen değeri son operand olarak yükler."""
        self._last_token = ""
        self._render(self._engine.load_value(value))

    # ── Dispatch & Render ─────────────────────────────────────────────────────

    def _dispatch(self, token: str) -> None:
        self._last_token = token
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
            self._display.setText(t(state.error))
            self._display.setStyleSheet(base_css + "QLineEdit { color: #FF3B30; }")
        else:
            text = format_display_expr(state.expression or "0")
            fs = 36 if len(text) <= 9 else (26 if len(text) <= 14 else 18)
            self._display.setFont(QFont("Segoe UI Variable Display", fs, QFont.Weight.Light))

            # "=" basıldığında sonuç animasyonu
            if self._last_token == "=" and text != self._display.text():
                self._animate_result(text, base_css)
            else:
                self._display.setText(text)
                self._display.setStyleSheet(base_css)

        self._history_label.setText(state.history)
        self._mem_indicator.setVisible(state.memory_active)

        for label, b in self._buttons.items():
            if label in _DISABLE_ON_ERROR:
                b.setEnabled(not state.buttons_disabled)

        for label in ("MC", "MR"):
            b = self._mem_buttons.get(label)
            if b:
                b.setEnabled(state.memory_active)

        for label in ("MS", "M+", "M-"):
            b = self._mem_buttons.get(label)
            if b:
                b.setEnabled(True)

        if self._history_visible:
            self._refresh_history_list()

    def _animate_result(self, text: str, base_css: str) -> None:
        """Apple tarzı sonuç animasyonu — fade + hafif yukarıdan kayış."""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        from PyQt6.QtWidgets import QGraphicsOpacityEffect

        self._display.setText(text)
        self._display.setStyleSheet(base_css)

        # Opacity animasyonu — 0'dan 1'e fade in
        effect = QGraphicsOpacityEffect(self._display)
        self._display.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_finished():
            self._display.setGraphicsEffect(None)

        anim.finished.connect(on_finished)
        anim.start()
        self._result_anim = anim

    # ── Bağlam Menüsü ─────────────────────────────────────────────────────────

    def _show_display_menu(self, pos: QPoint) -> None:
        p = THEMES[self._theme_name]
        menu = QMenu(self._display)
        menu.setStyleSheet(menu_style(p))
        copy_act = QAction(t("menu.copy"), self)
        copy_act.setIcon(self._draw_icon("copy", False))
        copy_act.triggered.connect(self._copy_result)
        menu.addAction(copy_act)
        paste_act = QAction(t("menu.paste"), self)
        paste_act.setIcon(self._draw_icon("paste", False))
        paste_act.triggered.connect(self._paste_from_clipboard)
        paste_act.setEnabled(bool(QApplication.clipboard().text().strip()))
        menu.addAction(paste_act)
        menu.addSeparator()
        sel_act = QAction(t("menu.selectall"), self)
        sel_act.triggered.connect(self._display.selectAll)
        menu.addAction(sel_act)
        menu.exec(self._display.mapToGlobal(pos))

    # ── Ayarlar Menüsü ────────────────────────────────────────────────────────

    def _show_settings_menu(self) -> None:
        p = THEMES[self._theme_name]
        menu = QMenu(self)
        menu.setStyleSheet(menu_style(p, radius=10, item_padding="7px 24px 7px 12px",
                                      item_radius=6, item_extra="font-size: 9pt;",
                                      separator_margin="4px 8px"))
        theme_menu = menu.addMenu(t("settings.theme"))
        light_action = QAction(t("settings.theme.light"), self, checkable=True)
        dark_action  = QAction(t("settings.theme.dark"),  self, checkable=True)
        light_action.setChecked(self._theme_name == "light")
        dark_action.setChecked(self._theme_name == "dark")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        dark_action.triggered.connect(lambda:  self._set_theme("dark"))
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

        opacity_menu = menu.addMenu(t("settings.opacity"))
        for label, val in [
            (t("settings.opacity.full"),   1.0),
            (t("settings.opacity.slight"), 0.92),
            (t("settings.opacity.half"),   0.80),
        ]:
            act = QAction(label, self, checkable=True)
            act.setData(val)
            act.setChecked(abs(val - self._opacity) < 0.01)
            act.triggered.connect(lambda checked, v=val: self._set_opacity(v))
            opacity_menu.addAction(act)

        lang_menu = menu.addMenu(t("settings.language"))
        for code, name in SUPPORTED_LANGUAGES:
            act = QAction(name, self, checkable=True)
            act.setChecked(get_language() == code)
            act.triggered.connect(lambda checked, c=code: self._set_language(c))
            lang_menu.addAction(act)

        menu.addSeparator()
        help_act = QAction(t("settings.help"), self)
        help_act.triggered.connect(self._show_help)
        menu.addAction(help_act)
        feedback_act = QAction(t("settings.feedback"), self)
        feedback_act.triggered.connect(self._show_feedback_dialog)
        menu.addAction(feedback_act)
        about_act = QAction(t("settings.about"), self)
        about_act.triggered.connect(self._show_about)
        menu.addAction(about_act)


        pos = self._settings_btn.mapToGlobal(self._settings_btn.rect().bottomRight())
        menu.exec(pos)

    # ── Yardım & Hakkında ─────────────────────────────────────────────────────

    def _show_help(self) -> None:
        show_help(self, THEMES[self._theme_name])

    def _show_about(self) -> None:
        show_about(self, THEMES[self._theme_name], self._start_download)

    def _show_feedback_dialog(self) -> None:
        show_feedback(self, THEMES[self._theme_name])

    # ── Güncelleme ────────────────────────────────────────────────────────────

    def _auto_check_update(self) -> None:
        """Program açılıştan 3 sn sonra arka planda kontrol eder."""
        self._update_checker = UpdateChecker(self)
        self._update_checker.update_available.connect(self._on_update_available)
        self._update_checker.start()

    def _on_update_available(self, new_version: str, download_url: str, digest: str) -> None:
        """Yeni sürüm bulunduğunda bildirim göster."""
        show_update_prompt(self, THEMES[self._theme_name],
                           new_version, download_url, digest, self._start_download)

    def _start_download(self, new_version: str, download_url: str, digest: str = "") -> None:
        """İndirme başlatır, progress penceresi gösterir."""
        self._downloader = run_download(
            self, THEMES[self._theme_name], new_version, download_url, digest)

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