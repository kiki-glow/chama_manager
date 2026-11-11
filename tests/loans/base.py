"""Shared fixture for the loan tests (not a test module itself)."""

import unittest
from datetime import date
from decimal import Decimal

from chama_manager import Chama, ChamaRules, FlatInterest, Loan, Member

JAN = date(2026, 1, 1)


class LoanTestCase(unittest.TestCase):
    """Base class: Alice saves 2,000 and Bob 4,000, so the pool is 6,000."""

    rules: ChamaRules
    chama: Chama
    alice: Member
    bob: Member

    def setUp(self) -> None:
        self.rules = ChamaRules(
            Decimal("1000"),
            loan_multiple=3,
            max_term_months=6,
            monthly_interest_percent=Decimal("10"),
            interest_strategy=FlatInterest(),
        )
        self.chama = Chama("Test Chama", self.rules)
        self.alice = self.chama.add_member("Alice", "0712345678", JAN)
        self.bob = self.chama.add_member("Bob", "0722345678", JAN)
        self.chama.record_contribution(self.alice.id, 2000, date(2026, 1, 3))
        self.chama.record_contribution(self.bob.id, 4000, date(2026, 1, 3))

    def take_loan(self) -> Loan:
        """Helper: Alice borrows 3,000 over 3 months (flat 10% -> 3,900 total)."""
        return self.chama.issue_loan(self.alice.id, 3000, 3, date(2026, 1, 10))