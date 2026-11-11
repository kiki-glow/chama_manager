"""Chama: the public facade that ties members, contributions and loans together.

Each concern lives in its own module (members.py, contributions.py,
loans/book.py). This class checks that the member exists, then delegates.
"""

from datetime import date
from decimal import Decimal

from .contributions import Contribution, ContributionLedger
from .loans import Loan, Repayment
from .loans.book import LoanBook
from .members import Member, MemberRegistry
from .money import MoneyInput
from .rules import ChamaRules


class Chama:
    """A savings group: one object to run members, savings and loans."""

    def __init__(self, name: str, rules: ChamaRules) -> None:
        """Create an empty chama with the given name and rules."""
        self.name: str = name
        self.rules: ChamaRules = rules
        self._registry = MemberRegistry()
        self._ledger = ContributionLedger(rules)
        self._loans = LoanBook(rules, self._ledger)

    # ---- members ----

    def add_member(
        self, name: str, phone: str, joined_on: date | None = None
    ) -> Member:
        """Register a new member. Phone numbers must be unique."""
        return self._registry.add(name, phone, joined_on)

    def get_member(self, member_id: int) -> Member:
        """Return a member by id or raise MemberNotFoundError."""
        return self._registry.get(member_id)

    @property
    def members(self) -> list[Member]:
        """All members, in the order they joined."""
        return self._registry.all()

    # ---- contributions ----

    def record_contribution(
        self,
        member_id: int,
        amount: MoneyInput,
        paid_on: date,
        period: date | None = None,
    ) -> Contribution:
        """Record a payment. `period` defaults to the month of `paid_on`."""
        self.get_member(member_id)  # raises if the member doesn't exist
        return self._ledger.record(member_id, amount, paid_on, period)

    def paid_for_period(self, member_id: int, period: date) -> Decimal:
        """How much a member has paid towards one month so far."""
        self.get_member(member_id)
        return self._ledger.paid_for_period(member_id, period)

    def balance_due(self, member_id: int, period: date) -> Decimal:
        """Amount still owed for a month (never negative)."""
        self.get_member(member_id)
        return self._ledger.balance_due(member_id, period)

    def is_overdue(
        self, member_id: int, period: date, today: date | None = None
    ) -> bool:
        """True if the grace period has passed and money is still owed."""
        self.get_member(member_id)
        return self._ledger.is_overdue(member_id, period, today)

    def total_savings(self, member_id: int) -> Decimal:
        """Everything a member has ever contributed."""
        self.get_member(member_id)
        return self._ledger.total_for(member_id)

    def total_pool(self) -> Decimal:
        """Everything contributed by all members."""
        return self._ledger.total()

    def statement(self, member_id: int) -> list[Contribution]:
        """A member's contributions, oldest first."""
        self.get_member(member_id)
        return self._ledger.statement(member_id)

    # ---- loans ----

    def issue_loan(
        self,
        member_id: int,
        principal: MoneyInput,
        term_months: int,
        issued_on: date | None = None,
    ) -> Loan:
        """Lend money to a member if every eligibility rule passes."""
        self.get_member(member_id)
        return self._loans.issue(member_id, principal, term_months, issued_on)

    def repay_loan(
        self, loan_id: int, amount: MoneyInput, paid_on: date | None = None
    ) -> Repayment:
        """Record a repayment against a loan."""
        return self._loans.repay(loan_id, amount, paid_on)

    def get_loan(self, loan_id: int) -> Loan:
        """Return a loan by id or raise LoanNotFoundError."""
        return self._loans.get(loan_id)

    def all_loans(self) -> list[Loan]:
        """Every loan in the chama, oldest first."""
        return self._loans.all()
    
    def loans_for(self, member_id: int) -> list[Loan]:
        """All loans a member has taken, oldest first."""
        self.get_member(member_id)
        return self._loans.for_member(member_id)

    def active_loan_for(self, member_id: int) -> Loan | None:
        """The member's unpaid loan, or None."""
        self.get_member(member_id)
        return self._loans.active_for(member_id)

    def max_loan_for(self, member_id: int) -> Decimal:
        """Largest loan a member may take."""
        self.get_member(member_id)
        return self._loans.max_for(member_id)

    def available_funds(self) -> Decimal:
        """Cash the chama can lend right now."""
        return self._loans.available_funds()