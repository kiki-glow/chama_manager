"""Money helpers.

Money is always a Decimal, never a float, to avoid rounding drift.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Final, TypeAlias

from .exceptions import InvalidAmountError

# types callers may pass as an amount. floats are deliberately absent
MoneyInput: TypeAlias = int | str | Decimal

_CENTS: Final = Decimal("0.01") # all amounts are kept to 2 decimal places

def round_money(value: Decimal) -> Decimal:
    """Round a computed amount to 2 d.p. (half-up).
    
    Unlike to_money, zero is allowed: computed interest can legitimately be 0.
    """
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)

def to_money(value: MoneyInput) -> Decimal:
    """Covert an int, str, or Decimal into a positive Decimal (2 d.p.).

    Floats are rejected on purpose: in binary floating point 0.1 + 0.2 != 0.3.
    Raises InvalidAmountError for anything that is not a positive number.
    """
    # runtime guard: type hints don't stop a float from sneaking in from untyped code.
    # bool is a subclass of int in Python, so reject it explicitly too.
    if isinstance(value, (float, bool)):
        raise InvalidAmountError(
            f"Use str, int or Decimal for money, not {type(value).__name__}."
        )

    # Decimal() raises different errors depending on the bad input type
    # "abc" -> InvalidOperation (a subclass of ArithmeticError)
    # None -> TypeError, [1] -> ValueError
    try:
        amount = Decimal(value)
    except (ArithmeticError, TypeError, ValueError):
        raise InvalidAmountError(f"Not a valid amount: {value!r}") from None

    # check finiteness first: comparing NaN with 0 would itself raise.
    if not amount.is_finite() or amount <= 0:
        raise InvalidAmountError(f"Amount must be a positive number, got {value!r}.")

    return round_money(amount)