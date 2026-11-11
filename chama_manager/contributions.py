"""Contributions: the Contribution model and the ContributionLedger."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Final

from .dates import month_start
from .money import MoneyInput, to_money
from .rules import ChamaRules

_ZERO: Final = Decimal("0.00")

@dataclass(frozen=True)
class Contribution:
    """One payment by a member towards a given month.
    
    `period` is always the first day of the month being paid for, so several (partial) payments for the same month group together.
    """

    member_id: int
    amount: Decimal
    paid_on: date
    period: date

    def __post_init__(self) -> None:
        """Validate the amount and snap `period` to the starts of its month."""
        object.__setattr__(self, "amount", to_money(self.amount))
        object.__setattr__(self, "period", month_start(self.period))

class ContributionLedger:        
    """Records contributions and answers questions about them.
    
    It does not check that members exist; the Chama does that first."""

    def __init__(self, rules: ChamaRules) -> None:
        """Create an empty ledger governed by `rules`."""
        self._rules = rules
        self._items: list[Contribution] = []

    def record(
        self,
        member_id: int,
        amount: MoneyInput,
        paid_on: date,
        period: date | None = None
    ) -> Contribution:
        """Record a payment. `period` defaults to the month of `paid_on`."""
        contribution = Contribution(member_id, to_money(amount), paid_on, period or paid_on)
        self._items.append(contribution)
        return contribution

    @staticmethod
    def _sum(items: Iterable[Contribution]) -> Decimal:
        """Sum contributions (a Decimal start value keeps 2 d.p.)."""
        return sum((c.amount for c in items), _ZERO)

    def total(self) -> Decimal:
        """Everything contributed by all members."""
        return self._sum(self._items)

    def total_for(self, member_id: int) -> Decimal:
        """Everything one member has ever contributed."""
        return self._sum(c for c in self._items if c.member_id == member_id)

    def paid_for_period(self, member_id: int, period: date) -> Decimal:
        """How much a member has paid towards one month so far."""
        period = month_start(period)
        return self._sum(
            c for c in self._items if c.member_id == member_id and c.period == period
        )

    def balance_due(self, member_id: int, period: date) -> Decimal:
        """Amount still owed for a month (never negative, even if overpaid)."""
        owed = self._rules.contribution_amount - self.paid_for_period(member_id, period)
        return max(owed, _ZERO)

    def is_overdue(self, member_id: int, period: date, today: date | None = None) -> bool:
        """True if the grace period has passed and money is still owed."""
        today = today or date.today()
        due = self._rules.due_date(month_start(period))
        return today > due and self.balance_due(member_id, period) > 0

    def statement(self, member_id: int) -> list[Contribution]:
        """A member's contributions, oldest first."""
        mine = (c for c in self._items if c.member_id == member_id)
        return sorted(mine, key=lambda c: (c.paid_on, c.period))