"""Schedule building blocks: the Installment and a rounding-safe splitter."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ..money import round_money

@dataclass(frozen=True)
class Installment:
    """One scheduled loan payment, split into principal and interest."""

    number: int
    due_date: date 
    principal: Decimal
    interest: Decimal

    @property
    def payment(self) -> Decimal:
        """Total due on this installment."""
        return self.principal + self.interest

def split_evenly(total: Decimal, parts: int) -> list[Decimal]:
    """Split `total` into `parts` amount (2 d.p.) that add up exactly.
    
    The last part absorbs any rounding reminder e.g. 1000 / 3 -> 333.33, 333.34.
    """
    share = round_money(total / parts)
    amounts = [share] * (parts - 1)
    amounts.append(total - share * (parts - 1))
    return amounts