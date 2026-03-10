from __future__ import annotations
from dataclasses import dataclass
from core import ThemeName


@dataclass(frozen=True)
class ThemePalette:
    name:               ThemeName
    bg:                 str
    surface:            str
    text:               str
    btn_numeric:        str
    btn_numeric_hover:  str
    btn_operator:       str
    btn_operator_hover: str
    btn_function:       str
    btn_function_hover: str
    btn_equals:         str
    btn_equals_hover:   str
    btn_equals_text:    str
    display_bg:         str
    history_text:       str
    accent:             str


LIGHT = ThemePalette(
    name="light",
    bg="#F2F2F7",            surface="#FFFFFF",
    text="#1A1A2E",
    btn_numeric="#FFFFFF",   btn_numeric_hover="#E5E5EA",
    btn_operator="#FF9500",  btn_operator_hover="#E08500",
    btn_function="#E5E5EA",  btn_function_hover="#D1D1D6",
    btn_equals="#FF9500",    btn_equals_hover="#E08500",  btn_equals_text="#FFFFFF",
    display_bg="#F2F2F7",    history_text="#8E8E93",
    accent="#FF9500",
)

DARK = ThemePalette(
    name="dark",
    bg="#1C1C1E",            surface="#2C2C2E",
    text="#F2F2F7",
    btn_numeric="#3A3A3C",   btn_numeric_hover="#48484A",
    btn_operator="#FF9F0A",  btn_operator_hover="#E08500",
    btn_function="#2C2C2E",  btn_function_hover="#3A3A3C",
    btn_equals="#FF9F0A",    btn_equals_hover="#E08500",  btn_equals_text="#FFFFFF",
    display_bg="#1C1C1E",    history_text="#636366",
    accent="#FF9F0A",
)

THEMES: dict[ThemeName, ThemePalette] = {"light": LIGHT, "dark": DARK}


def btn_style(bg: str, hover: str, fg: str,
              fs: int = 13, bold: bool = False, radius: int = 4) -> str:
    w = "bold" if bold else "normal"
    return (
        f"QPushButton {{"
        f"background-color:{bg};color:{fg};"
        f"border:none;border-radius:{radius}px;"
        f"font-size:{fs}pt;font-weight:{w};font-family:'Segoe UI Variable Text','Segoe UI',sans-serif;}}"
        f"QPushButton:hover{{background-color:{hover};}}"
        f"QPushButton:pressed{{background-color:{hover};}}"
        f"QPushButton:disabled{{background-color:{bg};color:rgba(120,120,120,0.5);}}"
    )


def main_style(p: ThemePalette) -> str:
    return f"""
        QMainWindow, QWidget#centralWidget {{ background-color: {p.bg}; }}
        QMenu {{
            background-color: {p.surface}; color: {p.text};
            border: 1px solid rgba(128,128,128,0.25); border-radius: 8px; padding: 4px;
        }}
        QMenu::item {{ padding: 6px 20px 6px 10px; border-radius: 4px; }}
        QMenu::item:selected {{ background-color: {p.accent}; color: #FFF; border-radius: 4px; }}
        QMenu::separator {{ height: 1px; background: rgba(128,128,128,0.2); margin: 3px 6px; }}
    """