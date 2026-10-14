import pytest

from core.engine import CalculatorEngine


def run(tokens):
    engine = CalculatorEngine()
    state = None
    for tok in tokens:
        state = engine.press(tok)
    return state


def result(tokens):
    state = run(tokens)
    return state.error or state.expression


def keys(text):
    """'12+3=' → ['1','2','+','3','=']  (çok karakterli tokenlar liste olarak verilir)"""
    return list(text)


# ── Temel işlemler ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("tokens, expected", [
    (keys("12+3="), "15"),
    (["7", "−", "9", "="], "-2"),
    (["6", "×", "7", "="], "42"),
    (["1", "÷", "4", "="], "0,25"),
    (["0", ",", "1", "+", "0", ",", "2", "="], "0,3"),
    (["5", "+", "3", "=", "=", "="], "14"),          # son işlem tekrarı
    (["5", "+", "2", "+", "3", "="], "10"),
])
def test_basic(tokens, expected):
    assert result(tokens) == expected


def test_divide_by_zero():
    state = run(["5", "÷", "0", "="])
    assert state.error == "error.div_zero"
    assert state.buttons_disabled


# ── Büyük sayılar / bilimsel gösterim ─────────────────────────────────────────

def test_large_result_can_be_reused():
    tokens = keys("99999999") + ["×"] + keys("99999999") + ["=", "×", "2", "="]
    value = float(result(tokens).replace(",", "."))
    assert value == pytest.approx(99999999 ** 2 * 2, rel=1e-11)


def test_large_result_chain_with_plus():
    tokens = keys("100000000") + ["×"] + keys("100000000") + ["=", "+", "1", "="]
    assert result(tokens) == "1e16"


def test_overflow_is_error_not_crash():
    engine = CalculatorEngine()
    for tok in keys("99999999"):
        engine.press(tok)
    errors = {engine.press("x²").error for _ in range(10)}
    assert "error.overflow" in errors


def test_backspace_on_scientific_clears_operand():
    state = run(keys("99999999") + ["x²", "x²", "⌫"])
    assert state.expression == "0"
    assert not state.error


def test_digit_after_scientific_starts_new_number():
    assert result(keys("99999999") + ["x²", "x²", "5"]) == "5"


# ── Yüzde (Windows davranışı) ─────────────────────────────────────────────────

@pytest.mark.parametrize("tokens, expected", [
    (keys("200") + ["+"] + keys("10") + ["%", "="], "220"),
    (keys("200") + ["−"] + keys("10") + ["%", "="], "180"),
    (keys("50") + ["×"] + keys("10") + ["%", "="], "5"),
    (keys("50") + ["÷"] + keys("10") + ["%", "="], "500"),
    (keys("25") + ["%"], "0,25"),
])
def test_percent(tokens, expected):
    assert result(tokens) == expected


# ── Tek girdili fonksiyonlar ──────────────────────────────────────────────────

def test_unary_functions():
    assert result(["9", "2√x"]) == "3"
    assert result(["4", "1/x"]) == "0,25"
    assert result(["1", "2", "x²"]) == "144"
    assert result(["0", "1/x"]) == "error.div_zero"
    assert result(["4", "+/-", "2√x"]) == "error.neg_sqrt"


# ── Geri silme ────────────────────────────────────────────────────────────────

def test_backspace_negative_number():
    # "-5" → ⌫ → "-" kalmamalı
    assert result(["5", "+/-", "⌫"]) == "0"
    assert result(["5", "+/-", "⌫", "+", "3", "="]) == "3"


def test_backspace_removes_operator():
    assert result(["5", "+", "⌫"]) == "5"
    assert result(["5", "+", "⌫", "×", "3", "="]) == "15"


def test_backspace_in_second_operand():
    assert result(["8", "+", "1", "2", "⌫"]) == "8+1"


# ── Dışarıdan değer yükleme (yapıştır / geçmiş) ──────────────────────────────

def test_load_value_replaces_current_operand():
    engine = CalculatorEngine()
    for tok in ["5", "+"]:
        engine.press(tok)
    engine.load_value(1234.5)
    assert engine.state.expression == "5+1.234,5"
    assert engine.press("=").expression == "1.239,5"


def test_load_value_after_result_starts_fresh():
    engine = CalculatorEngine()
    for tok in ["2", "+", "2", "="]:
        engine.press(tok)
    engine.load_value(-3)
    assert engine.state.expression == "-3"
    assert engine.press("+").expression == "-3+"


# ── Bellek ────────────────────────────────────────────────────────────────────

def test_memory():
    engine = CalculatorEngine()
    for tok in ["7", "MS", "C", "3", "M+", "C", "MR"]:
        engine.press(tok)
    assert engine.state.expression == "10"
    engine.press("MC")
    assert not engine.state.memory_active


def test_memory_with_large_value():
    engine = CalculatorEngine()
    for tok in keys("99999999") + ["x²", "x²", "MS", "C", "MR"]:
        engine.press(tok)
    assert float(engine.state.expression.replace(",", ".")) == pytest.approx(99999999.0 ** 4, rel=1e-11)
