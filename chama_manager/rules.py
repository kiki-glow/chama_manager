"""Chama rules: the settings that govern contributions and deadlines."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from .exceptions import InvalidRulesError
from .loans import InterestStrategy, ReducingBalanceInterest
from .money import to_money

@dataclass(frozen=True)
class ChamaRules:
    """Immutable rules for one chama.
    
    Attributes:
        contribution_amount: Expected amount per member each month.
        grace_days: Days after the 1st of the month before a payment is late.
        late_fine: Fine for an overdue contribution (0 means no fine).
        loan_multiple: Max loan as a multiple of member's savings.
        max_term_months: Longest repayment period allowed.
        monthly_interest_percent: Interest per month, as a percentage (5 = 5%).
        interest_strategy: How interest is calculated (flat, reducing, ...). 
    """

    contribution_amount: Decimal
    grace_days: int = 5
    late_fine: Decimal = Decimal("0")
    loan_multiple: int = 3
    max_term_months: int = 12
    monthly_interest_percent: Decimal = Decimal("5")
    interest_strategy: InterestStrategy = field(default_factory=ReducingBalanceInterest)

    def __post_init__(self) -> None:
        """Validate and normalise values (frozen, so use object.__setattr__)."""
        object.__setattr__(
            self, "contribution_amount", to_money(self.contribution_amount)
        )
        # a zero/empty fine is allowed; any other value must be valid money.
        fine = to_money(self.late_fine) if self.late_fine else Decimal("0.00")
        object.__setattr__(self, "late_fine", fine)

        if not isinstance(self.grace_days, int) or self.grace_days < 0:
            raise InvalidRulesError("grace_days must be a whole number >= 0.")
        if not isinstance(self.loan_multiple, int) or self.loan_multiple < 1:
            raise InvalidRulesError("loan_multiple must be a whole number >= 1.")
        if not isinstance(self.max_term_months, int) or self.max_term_months < 1:
            raise InvalidRulesError("max_term_months must be a whole number >= 1.")
        if not Decimal("0") <= self.monthly_interest_percent <= Decimal("100"):
            raise InvalidRulesError("monthly_interest_percent must be 0-100.")

    @property
    def monthly_rate(self) -> Decimal:
        """The monthly interest rate as a fraction (5 -> 0.05)."""
        return self.monthly_interest_percent / 100

    def due_date(self, period: date) -> date:
        """Last on-time day for the month starting at `period`."""
        return period + timedelta(days=self.grace_days)