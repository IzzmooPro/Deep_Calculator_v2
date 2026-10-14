"""
CalculatorEngine — saf iş mantığı, UI bağımlılığı yok.

Özellikler:
  - Bellek: MC, MR, M+, M-, MS token'ları
  - Hata durumu: buttons_disabled flag → UI butonları devre dışı bırakır
  - Hesap geçmişi: history_log listesi
  - Hata mesajları i18n anahtarı olarak tutulur ("error.div_zero" gibi);
    UI bunları t() ile aktif dile çevirir.
"""

from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass, field

from .constants import OPS, FUNCTIONS, ALLOWED_NODES
from .formatter import format_number, parse_number


# ── Veri Yapıları ─────────────────────────────────────────────────────────────

@dataclass
class CalculatorState:
    """Anlık hesap makinesi durumu."""
    expression:       str        = "0"
    history:          str        = ""
    error:            str        = ""
    just_evaluated:   bool       = False
    full_expression:  str        = ""
    last_op:          str        = ""
    last_operand:     str        = ""
    buttons_disabled: bool       = False   # hata sonrası
    memory:           float      = 0.0
    memory_active:    bool       = False   # M göstergesi
    history_log:      list[str]  = field(default_factory=list)


class CalculationError(Exception):
    """Mesajı bir i18n anahtarıdır (ör. "error.overflow")."""


# Hata anahtarları — çevirileri core/i18n.py içindedir.
ERR_DIV_ZERO     = "error.div_zero"
ERR_INVALID_OP   = "error.invalid_op"
ERR_NEG_SQRT     = "error.neg_sqrt"
ERR_INVALID_EXPR = "error.invalid_expr"
ERR_NOT_ALLOWED  = "error.not_allowed"
ERR_CALC         = "error.calc"
ERR_OVERFLOW     = "error.overflow"


def _finite(value: float) -> float:
    """Taşma (inf/nan) durumunda CalculationError fırlatır."""
    if not math.isfinite(value):
        raise CalculationError(ERR_OVERFLOW)
    return value


# ── Engine ────────────────────────────────────────────────────────────────────

class CalculatorEngine:

    def __init__(self) -> None:
        self._state = CalculatorState()

    @property
    def state(self) -> CalculatorState:
        return self._state

    def press(self, token: str) -> CalculatorState:
        handlers = {
            "=":   self._handle_equals,
            "C":   self._handle_clear,
            "CE":  self._handle_clear_entry,
            "⌫":  self._handle_backspace,
            "%":   self._handle_percent,
            "+/-": self._handle_negate,
            "1/x": self._handle_reciprocal,
            "x²":  self._handle_square,
            "2√x": self._handle_sqrt,
            # Bellek
            "MC":  self._handle_mc,
            "MR":  self._handle_mr,
            "M+":  self._handle_mplus,
            "M-":  self._handle_mminus,
            "MS":  self._handle_ms,
        }
        self._state.error = ""
        self._state.buttons_disabled = False

        if token in handlers:
            handlers[token]()
        elif token in OPS:
            self._handle_operator(token)
        elif token.isdigit() or token == ",":
            self._handle_digit(token)

        return self._state

    # ── Temel Handlers ────────────────────────────────────────────────────────

    def _handle_equals(self) -> None:
        expr = self._state.expression

        if self._state.just_evaluated and self._state.last_op and self._state.last_operand:
            current = self._state.expression
            repeat_expr = current + self._state.last_op + self._state.last_operand
            try:
                result = format_number(self._evaluate(repeat_expr))
                log_entry = repeat_expr + " = " + result
                self._state.history = repeat_expr + " ="
                self._state.expression = result
                self._state.history_log.append(log_entry)
            except ZeroDivisionError:
                self._set_error(ERR_DIV_ZERO)
            except CalculationError as e:
                self._set_error(str(e))
            return

        expr = expr.rstrip("".join(OPS))
        if not expr or expr == "0":
            return
        try:
            prefix, operand = self._split(expr)
            if prefix and operand:
                self._state.last_op = prefix[-1]
                self._state.last_operand = operand
            elif self._state.full_expression:
                fe = self._state.full_expression
                _, last_operand_in_fe = self._split(fe.rstrip("".join(OPS)))
                if last_operand_in_fe:
                    stripped_fe = fe.rstrip("".join(OPS))
                    pfx, _ = self._split(stripped_fe)
                    self._state.last_op = pfx[-1] if pfx else ""
                    self._state.last_operand = last_operand_in_fe
                else:
                    self._state.last_op = ""
                    self._state.last_operand = ""
            else:
                self._state.last_op = ""
                self._state.last_operand = ""

            if self._state.full_expression:
                full = self._state.full_expression + operand
                self._state.history = full + " ="
            else:
                self._state.history = expr + " ="

            result = format_number(self._evaluate(expr))
            log_entry = self._state.history.rstrip(" =").strip() + " = " + result
            self._state.history_log.append(log_entry)
            self._state.expression = result
            self._state.full_expression = ""
            self._state.just_evaluated = True
        except ZeroDivisionError:
            self._set_error(ERR_DIV_ZERO)
        except CalculationError as e:
            self._set_error(str(e))

    def _handle_clear(self) -> None:
        log = self._state.history_log
        mem = self._state.memory
        mem_active = self._state.memory_active
        self._state = CalculatorState()
        self._state.history_log = log
        self._state.memory = mem
        self._state.memory_active = mem_active

    def _handle_clear_entry(self) -> None:
        prefix, _ = self._split(self._state.expression)
        cleaned = prefix.rstrip("".join(OPS))
        self._state.expression = cleaned or "0"
        self._state.just_evaluated = False

    def _handle_backspace(self) -> None:
        if self._state.just_evaluated:
            self._state.expression = "0"
            self._state.just_evaluated = False
            return
        prefix, operand = self._split(self._state.expression)
        if not operand:
            # Operand yoksa son karakter operatördür — onu sil.
            self._state.expression = prefix[:-1] or "0"
            return
        if "e" in operand:
            # Bilimsel gösterimli sayı karakter karakter silinmez (ör. "1,5e1"
            # yanlış bir sayı olurdu) — operand tümden silinir.
            operand = ""
        else:
            operand = operand[:-1]
            if operand == "-":
                operand = ""
        new_expr = prefix + operand
        self._state.expression = new_expr or "0"

    def _handle_percent(self) -> None:
        """
        Windows Hesap Makinesi davranışı:
          a + b %  →  a + (a × b / 100)     (− için de aynı)
          a × b %  →  a × (b / 100)         (÷ için de aynı)
          b %      →  b / 100
        """
        prefix, op = self._split(self._state.expression)
        try:
            pct = self._parse(op) / 100
            if prefix and prefix[-1] in ("+", "−"):
                pct *= self._evaluate(prefix)
            self._replace_operand(format_number(_finite(pct)))
        except (ValueError, OverflowError):
            self._set_error(ERR_INVALID_OP)
        except ZeroDivisionError:
            self._set_error(ERR_DIV_ZERO)
        except CalculationError as e:
            self._set_error(str(e))

    def _handle_negate(self) -> None:
        prefix, op = self._split(self._state.expression)
        try:
            self._state.expression = prefix + format_number(-self._parse(op))
        except ValueError:
            self._set_error(ERR_INVALID_OP)

    def _handle_reciprocal(self) -> None:
        self._apply_unary(lambda v: 1 / v)

    def _handle_square(self) -> None:
        self._apply_unary(lambda v: v ** 2)

    def _handle_sqrt(self) -> None:
        def sqrt(v: float) -> float:
            if v < 0:
                raise CalculationError(ERR_NEG_SQRT)
            return math.sqrt(v)
        self._apply_unary(sqrt)

    def _apply_unary(self, fn) -> None:
        """Son operanda tek-girdili bir fonksiyon uygular; hataları yakalar."""
        _, op = self._split(self._state.expression)
        try:
            self._replace_operand(format_number(_finite(fn(self._parse(op)))))
        except ZeroDivisionError:
            self._set_error(ERR_DIV_ZERO)
        except OverflowError:
            self._set_error(ERR_OVERFLOW)
        except ValueError:
            self._set_error(ERR_INVALID_OP)
        except CalculationError as e:
            self._set_error(str(e))

    def _handle_operator(self, op: str) -> None:
        expr = self._state.expression
        if not expr or expr == "0":
            return
        if expr[-1] in OPS:
            self._state.expression = expr[:-1] + op
            if self._state.full_expression:
                fe = self._state.full_expression
                self._state.full_expression = fe[:-1] + op
            return

        prefix, operand = self._split(expr)
        if self._state.just_evaluated:
            self._state.last_op = ""
            self._state.last_operand = ""
            self._state.just_evaluated = False

        if prefix and operand:
            try:
                result = format_number(self._evaluate(expr))
                if self._state.full_expression:
                    self._state.full_expression += operand + op
                else:
                    self._state.full_expression = expr + op
                self._state.history = self._state.full_expression.rstrip("".join(OPS)) + " ="
                self._state.expression = result + op
            except ZeroDivisionError:
                self._set_error(ERR_DIV_ZERO)
                return
            except CalculationError as e:
                self._set_error(str(e))
                return
        else:
            self._state.expression = expr + op
            self._state.full_expression = ""

        self._state.just_evaluated = False

    def _handle_digit(self, digit: str) -> None:
        if self._state.just_evaluated:
            self._state.expression = "0"
            self._state.full_expression = ""
            self._state.just_evaluated = False

        prefix, operand = self._split(self._state.expression)
        if "e" in operand:
            # Bilimsel gösterimli bir sonucun sonuna rakam eklenmez; yeni sayı başlar.
            operand = "0"
        if digit == "," and "," in operand:
            return
        operand = digit if (operand == "0" and digit != ",") else operand + digit
        self._state.expression = prefix + operand

    # ── Bellek Handlers ───────────────────────────────────────────────────────

    def _handle_mc(self) -> None:
        """Memory Clear — belleği sıfırla."""
        self._state.memory = 0.0
        self._state.memory_active = False

    def _handle_mr(self) -> None:
        """Memory Recall — bellekteki değeri ekrana yükle."""
        if self._state.memory_active:
            prefix, _ = self._split(self._state.expression)
            self._state.expression = prefix + format_number(self._state.memory)
            # just_evaluated kasıtlı olarak True yapılmıyor:
            # MR sonrası operatör basıldığında last_op/last_operand korunur.

    def _handle_ms(self) -> None:
        """Memory Store — ekrandaki son operandı belleğe kaydet."""
        _, op = self._split(self._state.expression)
        try:
            self._state.memory = self._parse(op)
            self._state.memory_active = True
            # just_evaluated kasıtlı set edilmiyor:
            # MS sonrası kullanıcı hesaba kaldığı yerden devam edebilir.
        except ValueError:
            pass

    def _handle_mplus(self) -> None:
        """Memory + — ekrandaki değeri belleğe ekle."""
        _, op = self._split(self._state.expression)
        try:
            self._state.memory += self._parse(op)
            self._state.memory_active = True
            # just_evaluated kasıtlı set edilmiyor.
        except ValueError:
            pass

    def _handle_mminus(self) -> None:
        """Memory - — ekrandaki değeri bellekten çıkar."""
        _, op = self._split(self._state.expression)
        try:
            self._state.memory -= self._parse(op)
            self._state.memory_active = True
            # just_evaluated kasıtlı set edilmiyor.
        except ValueError:
            pass

    # ── Dışarıdan Değer Yükleme ───────────────────────────────────────────────

    def load_value(self, value: float) -> CalculatorState:
        """
        Yapıştırma / geçmişten seçme için: son operandı verilen değerle değiştirir.
        Hesap yeni bitmişse (just_evaluated) yeni bir hesaba başlanır.
        """
        self._state.error = ""
        self._state.buttons_disabled = False
        if self._state.just_evaluated:
            self._state.expression = "0"
            self._state.full_expression = ""
            self._state.history = ""
            self._state.just_evaluated = False
        try:
            self._replace_operand(format_number(_finite(float(value))))
        except (ValueError, CalculationError):
            self._set_error(ERR_INVALID_OP)
        return self._state

    # ── Hata ──────────────────────────────────────────────────────────────────

    def _set_error(self, msg: str) -> None:
        self._state.error = msg
        self._state.expression = "0"
        self._state.history = ""
        self._state.just_evaluated = False
        self._state.buttons_disabled = True   # operatör/fonksiyon butonları kapat

    # ── Yardımcılar ───────────────────────────────────────────────────────────

    def _replace_operand(self, new: str) -> None:
        prefix, _ = self._split(self._state.expression)
        self._state.expression = prefix + new

    @staticmethod
    def _split(expr: str) -> tuple[str, str]:
        i = len(expr) - 1
        while i >= 0 and expr[i] not in OPS:
            i -= 1
        return expr[: i + 1], expr[i + 1 :]

    @staticmethod
    def _parse(value: str) -> float:
        return parse_number(value)

    @staticmethod
    def _to_py(display_expr: str) -> str:
        """
        Türkçe görüntü ifadesini Python değerlendirme ifadesine çevirir.
        Binlik nokta ayraçlarını kaldırır, ondalık virgülü noktaya çevirir.
        """
        result = ""
        i = 0
        while i < len(display_expr):
            ch = display_expr[i]
            # Binlik ayraç tespiti: her iki yanında da rakam olmalı
            if (ch == "." and
                    i > 0 and display_expr[i - 1].isdigit() and
                    i + 1 < len(display_expr) and display_expr[i + 1].isdigit()):
                i += 1
                continue
            result += ch
            i += 1
        py = (result
              .replace(",", ".")
              .replace("×", "*")
              .replace("÷", "/")
              .replace("−", "-"))
        # Sondaki nokta varsa kaldır (örn: "42." → "42")
        py = re.sub(r"(\d)\.$", r"\1", py)
        # Operatör sonrası sondaki nokta (örn: "5+." → "5+0")
        py = re.sub(r"([+\-*/])\.$", r"\g<1>0", py)
        return py

    def _evaluate(self, display_expr: str) -> float:
        py = self._to_py(display_expr.rstrip("".join(OPS)))
        try:
            tree = ast.parse(py, mode="eval")
        except SyntaxError as e:
            raise CalculationError(ERR_INVALID_EXPR) from e
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                raise CalculationError(ERR_NOT_ALLOWED)
        try:
            return _finite(float(self._eval_node(tree.body)))
        except (ZeroDivisionError, CalculationError):
            raise
        except OverflowError as e:
            raise CalculationError(ERR_OVERFLOW) from e
        except Exception as e:
            raise CalculationError(ERR_CALC) from e

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            left, right = self._eval_node(node.left), self._eval_node(node.right)
            op = node.op
            if isinstance(op, ast.Add):  return left + right
            if isinstance(op, ast.Sub):  return left - right
            if isinstance(op, ast.Mult): return left * right
            if isinstance(op, ast.Div):
                if right == 0: raise ZeroDivisionError
                return left / right
        if isinstance(node, ast.UnaryOp):
            v = self._eval_node(node.operand)
            if isinstance(node.op, ast.USub): return -v
            if isinstance(node.op, ast.UAdd): return v
        raise CalculationError(ERR_NOT_ALLOWED)
