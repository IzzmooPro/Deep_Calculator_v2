import pytest

from core.formatter import (
    format_display_expr, format_number, parse_number, parse_pasted_number,
)


@pytest.mark.parametrize("value, expected", [
    (0, "0"),
    (0.0, "0"),
    (1234567.89, "1.234.567,89"),
    (-1234.5, "-1.234,5"),
    (0.1 + 0.2, "0,3"),
    (0.00001, "0,00001"),
    (123456789012345.0, "123.456.789.012.345"),
    (1e16, "1e16"),
    (-2.5e20, "-2,5e20"),
    (2.5e-11, "2,5e-11"),
])
def test_format_number(value, expected):
    assert format_number(value) == expected


@pytest.mark.parametrize("value", [
    1234567.89, -0.5, 1e16, 9.99999980000000e15, -3.25e-12, 42.0, 1e-5,
])
def test_format_parse_roundtrip(value):
    assert parse_number(format_number(value)) == pytest.approx(value, rel=1e-11)


def test_format_number_rejects_non_finite():
    with pytest.raises(ValueError):
        format_number(float("inf"))


@pytest.mark.parametrize("text, expected", [
    ("1.234,5", 1234.5),        # uygulamanın kendi kopyaladığı biçim
    ("1.234.567", 1234567),
    ("1.234", 1234),            # belirsiz → TR binlik
    ("1,234.56", 1234.56),      # İngilizce
    ("1234.56", 1234.56),
    ("1234,56", 1234.56),
    ("1 234,5", 1234.5),
    ("-42", -42),
    ("−7", -7),
    ("1,5e16", 1.5e16),
    ("2.5E-3", 0.0025),
])
def test_parse_pasted_number(text, expected):
    assert parse_pasted_number(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["", "abc", "12a", "1,2,3.4.5x", "1e999"])
def test_parse_pasted_number_invalid(text):
    with pytest.raises(ValueError):
        parse_pasted_number(text)


def test_format_display_expr():
    assert format_display_expr("1234+5678,5") == "1.234+5.678,5"
    assert format_display_expr("1,5e16×2") == "1,5e16×2"
