"""
Ortak sayı formatlama — Türkçe gösterim (nokta=binlik, virgül=ondalık).
Engine ve UI her ikisi de bu modülü kullanır; tekrar yoktur.
"""

from __future__ import annotations

import re

# Operatör karakterleri (UI ve engine'de ortak kullanım için burada tanımlı)
_OPS_CHARS = "+−×÷"


def format_number(value: float | int) -> str:
    """
    float/int → Türkçe gösterim.
    Örnek: 1234567.89 → "1.234.567,89"
    """
    if isinstance(value, float):
        if abs(value) >= 1e15:
            return f"{value:.6e}"
        if value.is_integer():
            value = int(value)
        else:
            value = float(f"{value:.12g}")

    raw = str(value)
    int_part, dec_part = raw.split(".") if "." in raw else (raw, "")
    dec_part = dec_part.rstrip("0")

    sign = ""
    if int_part.startswith("-"):
        sign, int_part = "-", int_part[1:]

    rev = int_part[::-1]
    chunks = [rev[i: i + 3] for i in range(0, len(rev), 3)]
    fmt_int = sign + (".".join(chunks))[::-1]

    return f"{fmt_int},{dec_part}" if dec_part else fmt_int


def format_display_expr(expr: str) -> str:
    """
    Girilen ifadedeki tüm tam sayı operandlara binlik nokta uygula.
    Operatörler (+, −, ×, ÷) bölücü olarak kullanılır.
    Örnek: "1234+5678" → "1.234+5.678"
    """
    parts = re.split(f"([{re.escape(_OPS_CHARS)}])", expr)
    result = []
    for part in parts:
        if not part or part in _OPS_CHARS:
            result.append(part)
            continue

        sign = ""
        p = part
        if p.startswith("-"):
            sign, p = "-", p[1:]

        int_str, dec_str = (p.split(",", 1) if "," in p else (p, None))
        int_clean = int_str.replace(".", "")

        if not int_clean or not int_clean.isdigit():
            result.append(part)
            continue

        rev = int_clean[::-1]
        chunks = [rev[i: i + 3] for i in range(0, len(rev), 3)]
        fmt_int = sign + (".".join(chunks))[::-1]
        result.append(f"{fmt_int},{dec_str}" if dec_str is not None else fmt_int)

    return "".join(result)
