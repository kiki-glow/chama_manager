"""Tests for issuing loans: eligibility rules and the resulting loan."""

import unittest
from datetime import date
from decimal import Decimal
from typing import Any

from chama_manager import (
    ActiveLoanExistsError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidTermError,
    LoanLimitExceededError,
    MemberNotFoundError,
)

from .base import JAN, LoanTestCase


class IssueLoanTests(LoanTestCase):
    """Eligibility rules and the loan that results."""

    def test_limit_is_a_multiple_of_savings(self) -> None:
        self.assertEqual(self.chama.max_loan_for(self.alice.id), Decimal("6000.00"))

    def test_issued_loan_has_schedule_and_totals(self) -> None:
        loan = self.take_loan()
        self.assertEqual(loan.id, 1)
        self.assertEqual(len(loan.schedule), 3)
        self.assertEqual(loan.schedule[0].due_date, date(2026, 2, 10))
        self.assertEqual(loan.total_interest, Decimal("900.00"))
        self.assertEqual(loan.total_repayable, Decimal("3900.00"))
        self.assertEqual(loan.balance, Decimal("3900.00"))

    def test_lending_reduces_available_funds(self) -> None:
        self.assertEqual(self.chama.available_funds(), Decimal("6000.00"))
        self.take_loan()
        self.assertEqual(self.chama.available_funds(), Decimal("3000.00"))

    def test_loan_over_savings_limit_is_rejected(self) -> None:
        with self.assertRaises(LoanLimitExceededError):
            self.chama.issue_loan(self.alice.id, 6001, 3, date(2026, 1, 10))

    def test_loan_larger_than_available_cash_is_rejected(self) -> None:
        # Bob's limit is 12,000 but only 6,000 is in the pool.
        with self.assertRaises(InsufficientFundsError):
            self.chama.issue_loan(self.bob.id, 6500, 3, date(2026, 1, 10))

    def test_only_one_active_loan_per_member(self) -> None:
        self.take_loan()
        with self.assertRaises(ActiveLoanExistsError):
            self.chama.issue_loan(self.alice.id, 500, 2, date(2026, 1, 20))

    def test_term_outside_allowed_range_is_rejected(self) -> None:
        for term in (0, 7):
            with self.subTest(term=term):
                with self.assertRaises(InvalidTermError):
                    self.chama.issue_loan(self.alice.id, 500, term, JAN)

    def test_unknown_member_is_rejected(self) -> None:
        with self.assertRaises(MemberNotFoundError):
            self.chama.issue_loan(99, 500, 3, JAN)

    def test_float_principal_is_rejected(self) -> None:
        bad: Any = 500.5  # deliberately the wrong type
        with self.assertRaises(InvalidAmountError):
            self.chama.issue_loan(self.alice.id, bad, 3, JAN)

    def test_loan_ids_increment(self) -> None:
        first = self.take_loan()
        second = self.chama.issue_loan(self.bob.id, 1000, 1, date(2026, 1, 12))
        self.assertEqual((first.id, second.id), (1, 2))


if __name__ == "__main__":
    unittest.main()