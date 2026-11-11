"""LoanBook: issues loans, records repayments and enforces the loan rules."""

from datetime import date
from decimal import Decimal
from typing import Final

from ..contributions import ContributionLedger
from ..exceptions import (
    ActiveLoanExistsError,
    InsufficientFundsError,
    InvalidTermError,
    LoanLimitExceededError,
    LoanNotFoundError,
    RepaymentExceedsBalanceError,
)
from ..money import MoneyInput, to_money
from ..rules import ChamaRules
from .models import Loan, Repayment

_ZERO: Final = Decimal("0.00")


class LoanBook:
    """All loans of one chama.

    Eligibility needs savings and cash figures, so it is given the rules and
    the contribution ledger. It does not check that members exist; the Chama
    does that first.
    """

    def __init__(self, rules: ChamaRules, ledger: ContributionLedger) -> None:
        """Create an empty loan book."""
        self._rules = rules
        self._ledger = ledger
        self._loans: dict[int, Loan] = {}
        self._next_id: int = 1

    # ---- queries ----

    def get(self, loan_id: int) -> Loan:
        """Return a loan by id or raise LoanNotFoundError."""
        try:
            return self._loans[loan_id]
        except KeyError:
            raise LoanNotFoundError(f"No loan with id {loan_id}.") from None

    def all(self) -> list[Loan]:
        """Every loan, oldest first."""
        return list(self._loans.values())

    def for_member(self, member_id: int) -> list[Loan]:
        """All loans a member has taken, oldest first."""
        return [loan for loan in self._loans.values() if loan.member_id == member_id]

    def active_for(self, member_id: int) -> Loan | None:
        """The member's unpaid loan, or None."""
        return next((loan for loan in self.for_member(member_id) if loan.is_active), None)

    def max_for(self, member_id: int) -> Decimal:
        """Largest loan a member may take: loan_multiple x their savings."""
        return self._rules.loan_multiple * self._ledger.total_for(member_id)

    def available_funds(self) -> Decimal:
        """Cash the chama can lend: contributions + repayments - principal lent."""
        repaid = sum((loan.total_repaid for loan in self._loans.values()), _ZERO)
        lent = sum((loan.principal for loan in self._loans.values()), _ZERO)
        return self._ledger.total() + repaid - lent

    # ---- commands ----

    def issue(
        self,
        member_id: int,
        principal: MoneyInput,
        term_months: int,
        issued_on: date | None = None,
    ) -> Loan:
        """Lend money to a member if every eligibility rule passes."""
        amount = to_money(principal)
        self._check_term(term_months)
        self._check_eligibility(member_id, amount)

        issued_on = issued_on or date.today()
        # the chosen strategy builds the schedule; the loan records the rate used.
        schedule = self._rules.interest_strategy.build_schedule(
            amount, self._rules.monthly_rate, term_months, issued_on
        )
        loan = Loan(
            id=self._next_id,
            member_id=member_id,
            principal=amount,
            monthly_rate=self._rules.monthly_rate,
            term_months=term_months,
            issued_on=issued_on,
            schedule=schedule,
        )
        self._loans[loan.id] = loan
        self._next_id += 1
        return loan

    def repay(
        self, loan_id: int, amount: MoneyInput, paid_on: date | None = None
    ) -> Repayment:
        """Record a repayment. It may not exceed the outstanding balance."""
        loan = self.get(loan_id)
        value = to_money(amount)
        if value > loan.balance:
            raise RepaymentExceedsBalanceError(
                f"Repayment {value} is more than the balance of {loan.balance}."
            )
        repayment = Repayment(loan.id, value, paid_on or date.today())
        loan.repayments.append(repayment)
        return repayment

    # ---- checks ----

    def _check_term(self, term_months: int) -> None:
        """The term must be within the chama's allowed range."""
        if not 1 <= term_months <= self._rules.max_term_months:
            raise InvalidTermError(
                f"Term must be 1-{self._rules.max_term_months} months, got {term_months}."
            )

    def _check_eligibility(self, member_id: int, amount: Decimal) -> None:
        """One unpaid loan at a time, within savings limit, and cash on hand."""
        if self.active_for(member_id) is not None:
            raise ActiveLoanExistsError("Member already has an unpaid loan.")
        limit = self.max_for(member_id)
        if amount > limit:
            raise LoanLimitExceededError(f"Loan {amount} exceeds the limit of {limit}.")
        available = self.available_funds()
        if amount > available:
            raise InsufficientFundsError(f"Only {available} is available to lend.")