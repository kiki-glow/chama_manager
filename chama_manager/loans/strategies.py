"""Interest strategies (Strategy pattern).

Each strategy turns loan terms into a schedule, so new interest models
can be added without touching the rest of the code.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from ..dates import add_months
from ..money import round_money
from .schedule import Installment, split_evenly


class InterestStrategy(ABC):
    """Interface: turn loan terms into a month-by-month schedule."""

    @abstractmethod
    def build_schedule(
        self,
        principal: Decimal,
        monthly_rate: Decimal,
        term_months: int,
        issued_on: date,
    ) -> list[Installment]:
        """Return one Installment per month; principals must sum to `principal`."""


class FlatInterest(InterestStrategy):
    """Interest is charged on the original principal for every month.

    Total interest = principal x monthly rate x months, spread evenly.
    Simple and common in chamas, but costlier than reducing balance.
    """

    def build_schedule(
        self,
        principal: Decimal,
        monthly_rate: Decimal,
        term_months: int,
        issued_on: date,
    ) -> list[Installment]:
        """Build equal principal and equal interest installments."""
        total_interest = round_money(principal * monthly_rate * term_months)
        principals = split_evenly(principal, term_months)
        interests = split_evenly(total_interest, term_months)
        return [
            Installment(number, add_months(issued_on, number), p, i)
            for number, (p, i) in enumerate(
                zip(principals, interests, strict=True), start=1
            )
        ]


class ReducingBalanceInterest(InterestStrategy):
    """Interest is charged only on the balance still owed.

    Equal monthly payments (an annuity): early payments are mostly
    interest, later ones mostly principal.
    """

    def build_schedule(
        self,
        principal: Decimal,
        monthly_rate: Decimal,
        term_months: int,
        issued_on: date,
    ) -> list[Installment]:
        """Build an amortization schedule with a level monthly payment."""
        if monthly_rate == 0:
            payment = round_money(principal / term_months)
        else:
            # Annuity formula: P * r / (1 - (1 + r) ** -n)
            payment = round_money(
                principal * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)
            )

        schedule: list[Installment] = []
        balance = principal
        for number in range(1, term_months + 1):
            interest = round_money(balance * monthly_rate)
            if number == term_months:
                principal_part = balance  # last installment clears what's left
            else:
                principal_part = min(payment - interest, balance)
            due = add_months(issued_on, number)
            schedule.append(Installment(number, due, principal_part, interest))
            balance -= principal_part
        return schedule