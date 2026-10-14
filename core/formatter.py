"""
Ortak sayı formatlama — Türkçe gösterim (nokta=binlik, virgül=ondalık).
Engine ve UI her ikisi de bu modülü kullanır; tekrar yoktur.

Çok büyük / çok küçük sayılar bilimsel gösterimle yazılır: "1,5e16", "2,5e-11".
Üs kısmında "+" kullanılmaz (operatör sanılır), eksi işareti ASCII "-" dir
(operatör olan "−" ile karışmaz). Böylece formatlanan her değer
parse_number() ile ve hesaplama motorunda kayıpsız geri okunabilir.
"""

from __future__ import annotations

import math
import re
from decimal import Decimal

# Operatör karakterleri (UI ve engine'de ortak kullanım için burada tanımlı)
_OPS_CHARS = "+−×÷"

# Bu aralığın dışındaki (sıfır olmayan) değerler bilimsel gösterimle yazılır.
_SCI_UPPER = 1e15
_SCI_LOWER = 1e-10

# Hesaplamalarda tutulan anlamlı basamak sayısı (float hatalarını gizler).
_SIG_DIGITS = 12


def _group_thousands(int_digits: str) -> str:
    rev = int_digits[::-1]
    chunks = [rev[i: i + 3] for i in range(0, len(rev), 3)]
    return (".".join(chunks))[::-1]


def format_number(value: float | int) -> str:
    """
    float/int → Türkçe gösterim.
    Örnek: 1234567.89 → "1.234.567,89",  1e16 → "1e16",  -2.5e-11 → "-2,5e-11"
    """
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Sonlu olmayan değer: {value}")
        if value == 0:
            return "0"
        if abs(value) >= _SCI_UPPER or abs(value) < _SCI_LOWER:
            mantissa, exp = f"{value:.{_SIG_DIGITS - 1}e}".split("e")
            mantissa = mantissa.rstrip("0").rstrip(".").replace(".", ",")
            return f"{mantissa}e{int(exp)}"
        if value.is_integer():
            value = int(value)
        else:
            # .12g bilimsel gösterime kaçabilir; Decimal ile düz yazıya çevir.
            raw = format(Decimal(f"{value:.{_SIG_DIGITS}g}"), "f")
            return _format_plain(raw)

    return _format_plain(str(value))


def _format_plain(raw: str) -> str:
    int_part, dec_part = raw.split(".") if "." in raw else (raw, "")
    dec_part = dec_part.rstrip("0")

    sign = ""
    if int_part.startswith("-"):
        sign, int_part = "-", int_part[1:]

    fmt_int = sign + _group_thousands(int_part)
    return f"{fmt_int},{dec_part}" if dec_part else fmt_int


def parse_number(text: str) -> float:
    """
    format_number() çıktısını (Türkçe gösterim) float'a çevirir.
    Örnek: "1.234,5" → 1234.5,  "1,5e16" → 1.5e16.  Boş metin → 0.0
    Geçersiz metinde ValueError fırlatır.
    """
    cleaned = text.strip().replace(".", "").replace(",", ".")
    return float(cleaned) if cleaned else 0.0


def parse_pasted_number(text: str) -> float:
    """
    Panodan gelen sayıyı esnek biçimde okur. Desteklenenler:
      "1.234,56" (TR), "1,234.56" (EN), "1234.56", "1234,56", "1 234,56",
      "1,5e16", "-42".
    Ayraç belirsizse (tek nokta + tam 3 basamak, ör. "1.234") uygulamanın
    kendi gösterimi esas alınır → binlik ayracı.
    Geçersiz metinde ValueError fırlatır.
    """
    s = text.strip().replace(" ", "").replace(" ", "").replace("−", "-")
    if not s:
        raise ValueError("Boş metin")

    mantissa, exp = s, ""
    m = re.fullmatch(r"(.*?)[eE]([+-]?\d+)", s)
    if m:
        mantissa, exp = m.group(1), "e" + m.group(2)

    if "." in mantissa and "," in mantissa:
        # Son görünen ayraç ondalık ayracıdır.
        if mantissa.rfind(",") > mantissa.rfind("."):
            mantissa = mantissa.replace(".", "").replace(",", ".")
        else:
            mantissa = mantissa.replace(",", "")
    elif "," in mantissa:
        if mantissa.count(",") > 1:
            mantissa = mantissa.replace(",", "")
        else:
            mantissa = mantissa.replace(",", ".")
    elif "." in mantissa:
        if mantissa.count(".") > 1 or re.fullmatch(r"[+-]?\d{1,3}\.\d{3}", mantissa):
            mantissa = mantissa.replace(".", "")

    if not re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)", mantissa):
        raise ValueError(f"Sayı değil: {text!r}")
    value = float(mantissa + exp)
    if not math.isfinite(value):
        raise ValueError(f"Sonlu olmayan değer: {text!r}")
    return value


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

        fmt_int = sign + _group_thousands(int_clean)
        result.append(f"{fmt_int},{dec_str}" if dec_str is not None else fmt_int)

    return "".join(result)
