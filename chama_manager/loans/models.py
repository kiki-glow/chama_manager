"""Loan data models: Repayment and Loan."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Final

from .schedule import Installment

_ZERO: Final = Decimal("0.00")


@dataclass(frozen=True)
class Repayment:
    """A payment made towards a loan."""

    loan_id: int
    amount: Decimal
    paid_on: date


@dataclass
class Loan:
    """A loan to a member, with its schedule and the repayments so far.

    Mutable on purpose: repayments are appended over the loan's life.
    """

    id: int
    member_id: int
    principal: Decimal
    monthly_rate: Decimal  # the rate agreed when the loan was issued
    term_months: int
    issued_on: date
    schedule: list[Installment]
    repayments: list[Repayment] = field(default_factory=list)

    @property
    def total_interest(self) -> Decimal:
        """All interest across the schedule."""
        return sum((i.interest for i in self.schedule), _ZERO)

    @property
    def total_repayable(self) -> Decimal:
        """Principal plus interest: what the member must pay back in total."""
        return sum((i.payment for i in self.schedule), _ZERO)

    @property
    def total_repaid(self) -> Decimal:
        """Everything repaid so far."""
        return sum((r.amount for r in self.repayments), _ZERO)

    @property
    def balance(self) -> Decimal:
        """Amount still owed."""
        return self.total_repayable - self.total_repaid

    @property
    def is_active(self) -> bool:
        """True while any balance remains."""
        return self.balance > 0

    def overdue_installments(self, today: date) -> list[Installment]:
        """Installments past their due date that repayments don't yet cover.

        Repayments are applied to installments in order, so an installment
        is covered once total repaid reaches the running total due.
        """
        overdue: list[Installment] = []
        due_so_far = _ZERO
        for installment in self.schedule:
            due_so_far += installment.payment
            if installment.due_date < today and self.total_repaid < due_so_far:
                overdue.append(installment)
        return overdue